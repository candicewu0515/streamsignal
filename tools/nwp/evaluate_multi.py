"""Professional forecast + local calibration for all 8 StreamSignal hazard tasks.

PRE-DECLARED PROTOCOL (written before any 7-day / dry / compound result was seen)
- Tasks: rain, heat, dry, compound x horizon 3 and 7 days; labels = train_multihazard.label (unchanged definitions).
- Inputs: Open-Meteo Previous Runs daily totals (local time, group centroid). Day i+L of a window issued on day i
  uses the forecast issued L days earlier (lead L, L=1..h). Windows with any missing lead are excluded.
  rain/dry:  [log1p(total mm), log1p(max daily mm)]
  heat:      [max air C, (max air C)^2/100]
  compound:  [max air C, (max air C)^2/100, log1p(total mm)]
- Variants: A pooled; B local only; C precipitation scaled by each city's historical observed/forecast ratio then pooled
  (identical to A when a task has no precipitation feature); D pooled slope + local intercept/slope.
  B/D fall back to A when the city has a single class locally.
- Held-out city: pooled parts never see the scored city; local parts use only that city's past (fit-period) labels.
- Selection: fit 2024, score 2025, choose the variant with the best mean Brier skill across 5 cities (tie -> best worst city).
  Then refit on 2024-2025 and score 2026-01-01..2026-09-21. 2026 is never used for any choice.
- Alert thresholds (per task, from the 2025 held-out predictions of the selected variant):
  yellow = highest threshold with recall >= 0.80.
  red (rule 2) = lowest threshold ABOVE yellow with 2025 precision >= 0.80; none if unattainable.
  Rule 1 (red = lowest threshold with precision >= 0.50) collapsed onto yellow for all 8 tasks on the 2025 data,
  so it was replaced before re-scoring. Rule-1 output is kept in results/multi/multi_output_threshold_rule1.txt.
  Note: rule-1 2026 alert statistics had already been printed when rule 2 was written.
- Reported: every variant, every city, pooled vs own-city seasonal baselines, 90% 7-day block bootstrap CI,
  head-to-head vs the original frozen StreamSignal model on identical rows, reliability bins, threshold outcomes.
"""
import sys,os,json,csv; HERE=os.path.dirname(os.path.abspath(__file__))
from pathlib import Path
SS=str(Path(__file__).resolve().parents[2]); sys.path.insert(0,os.path.join(SS,'tools')); CACHE=os.environ.get('STREAMSIGNAL_NWP_CACHE',os.path.join(SS,'forecast_cache')); OUT=os.environ.get('STREAMSIGNAL_NWP_OUTPUT',os.path.join(SS,'results/nwp_multi_reproduced'))
os.makedirs(OUT,exist_ok=True)
import numpy as np
import train_forecast as base, train_multihazard as mh
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss as B, roc_auc_score as AUC
data=base.load_data(); gc={g:next(s['cityName'] for s in data['sites'] if s['group']==g) for g in range(21)}
CITIES=['Benevento','Coimbra','Ghent','Oslo','Toulouse']; idx={d:i for i,d in enumerate(data['dates'])}

# ---- forecast cache: F[g][(date,lead)] = (rain_mm, tmax_C)
F={}
for g in range(21):
    out={}
    for fn,leads in [(f'g{g}.json',[1,2,3]),(f'g{g}_L47.json',[4,5,6,7])]:
        h=json.load(open(os.path.join(CACHE,fn)))['hourly']
        for L in leads:
            p=h[f'precipitation_previous_day{L}']; T=h[f'temperature_2m_previous_day{L}']; day={}
            for i,ts in enumerate(h['time']): day.setdefault(ts[:10],[]).append((p[i],T[i]))
            for d,v in day.items():
                if len(v)==24 and all(a is not None and b is not None for a,b in v): out[(d,L)]=(sum(a for a,_ in v),max(b for _,b in v))
    F[g]=out

def feats(r,kind,h):
    i=idx[r['issueDate']]; vals=[]
    for L in range(1,h+1):
        k=(data['dates'][i+L],L)
        if k not in F[r['group']]: return None
        vals.append(F[r['group']][k])
    tot=sum(v[0] for v in vals); mx=max(v[0] for v in vals); t=max(v[1] for v in vals)
    return {'rain':[np.log1p(tot),np.log1p(mx)],'dry':[np.log1p(tot),np.log1p(mx)],'heat':[t,t*t/100],'compound':[t,t*t/100,np.log1p(tot)]}[kind]
PRECIP_IDX={'rain':[0,1],'dry':[0,1],'heat':[],'compound':[2]}

def rows(kind,h):
    rs=[r for r in mh.build(data,h,kind) if r['targetDate']>='2024-01-01']
    for r in rs: r['x']=feats(r,kind,h); r['city']=gc[r['group']]
    return [r for r in rs if r['x'] is not None]
def period(rs,lo,hi): return [r for r in rs if r['targetDate']>=lo and r['endDate']<=hi]
X=lambda rs:np.array([r['x'] for r in rs],float); Y=lambda rs:np.array([r['label'] for r in rs])
LR=lambda:LogisticRegression(max_iter=2000)

def fit_predict(variant,kind,fit,city,target,deploy=False):
    """Return (probabilities, parameter dict). deploy=True pools all cities (for export only, never scored)."""
    other=fit if deploy else [r for r in fit if r['city']!=city]; local=[r for r in fit if r['city']==city]
    used=variant
    if variant in('B','D') and len(set(Y(local)))<2: used='A'
    if variant=='C' and not PRECIP_IDX[kind]: used='A'
    if used=='A':
        m=LR().fit(X(other),Y(other)); return m.predict_proba(X(target))[:,1],dict(variant='A',coef=m.coef_[0].tolist(),intercept=float(m.intercept_[0]))
    if used=='B':
        m=LR().fit(X(local),Y(local)); return m.predict_proba(X(target))[:,1],dict(variant='B',coef=m.coef_[0].tolist(),intercept=float(m.intercept_[0]))
    if used=='C':
        cities=set(r['city'] for r in fit); ratio={}
        for c in cities:
            rc=[r for r in fit if r['city']==c]; ratio[c]=float(np.mean([r['rain'] for r in rc])/max(np.mean([np.expm1(r['x'][PRECIP_IDX[kind][0]]) for r in rc]),1e-6))
        def sc(rs):
            A=X(rs).copy()
            for j in PRECIP_IDX[kind]:
                A[:,j]=np.log1p(np.expm1(A[:,j])*np.array([ratio[r['city']] for r in rs]))
            return A
        m=LR().fit(sc(other),Y(other)); return m.predict_proba(sc(target))[:,1],dict(variant='C',coef=m.coef_[0].tolist(),intercept=float(m.intercept_[0]),precipScale=ratio[city],precipIndex=PRECIP_IDX[kind])
    m=LR().fit(X(other),Y(other)); z=X(local)@m.coef_[0]; o=LR().fit(z.reshape(-1,1),Y(local))
    return o.predict_proba((X(target)@m.coef_[0]).reshape(-1,1))[:,1],dict(variant='D',pooled_coef=m.coef_[0].tolist(),pooled_intercept=float(m.intercept_[0]),local=dict(a=float(o.intercept_[0]),b=float(o.coef_[0][0]),n=len(local),events=int(Y(local).sum())))

def season(train,target): return mh.pooled_season(train,target)
def bs_ci(y,p,q,dates,n=500):
    rng=np.random.default_rng(42); days=sorted(set(dates)); ix={d:i for i,d in enumerate(days)}; di=np.array([ix[d] for d in dates])
    blocks=[np.where((di>=s)&(di<s+7))[0] for s in range(0,len(days),7)]; out=[]
    for _ in range(n):
        ii=np.concatenate([blocks[j] for j in rng.integers(0,len(blocks),len(blocks))]); qb=B(y[ii],q[ii])
        if qb>0: out.append(1-B(y[ii],p[ii])/qb)
    return [float(x) for x in np.percentile(out,[5,95])]
def skill(y,p,q): return float(1-B(y,p)/B(y,q)) if B(y,q)>0 else float('nan')
def pick_thresholds(y,p):
    ts=np.round(np.arange(.02,.99,.01),2); rec=lambda t:((p>=t)&(y==1)).sum()/max(y.sum(),1); prec=lambda t:((p>=t)&(y==1)).sum()/max((p>=t).sum(),1)
    ok=[t for t in ts if rec(t)>=.8]; yellow=float(max(ok)) if ok else float(ts[0])
    okr=[t for t in ts if t>yellow and (p>=t).sum()>0 and prec(t)>=.8]
    return yellow,(float(min(okr)) if okr else None)
def alert_stats(y,p,t,months):
    a=p>=t; tp=int((a&(y==1)).sum()); fp=int((a&(y==0)).sum()); fn=int((~a&(y==1)).sum())
    return dict(threshold=t,hitRate=tp/max(tp+fn,1),precision=tp/max(tp+fp,1),alerts=int(a.sum()),falseAlerts=fp,missed=fn,falseAlertsPerGroupMonth=fp/months)

# ---- original frozen model predictions for head-to-head
orig={}
with open(os.path.join(SS,'results/multihazard_predictions.csv'),encoding='utf-8-sig') as f:
    for r in csv.DictReader(f): orig[(r['task'],int(r['weatherGroup'])-1,r['issueDate'])]=(float(r['probability']),float(r['seasonalProbability']))

V=['A','B','C','D']; summary={}; params={}; lines=[]
def log(s=''): print(s,flush=True); lines.append(s)
for h in [3,7]:
    for kind in ['rain','heat','dry','compound']:
        key=f'{kind}_{h}'; R=rows(kind,h)
        log(f'\n##### {key}: {mh.HAZARDS[kind]}, {h} days  (rows with complete forecasts: {len(R)}) #####')
        fit=period(R,'2024-01-01','2024-12-31'); val=period(R,'2025-01-01','2025-12-31'); sel={}
        for v in V:
            sk=[]
            for c in CITIES:
                t=[r for r in val if r['city']==c]; p,_=fit_predict(v,kind,fit,c,t); sk.append(skill(Y(t),p,season([r for r in fit if r['city']!=c],t)))
            sel[v]=(float(np.nanmean(sk)),float(np.nanmin(sk))); log(f'  2025 selection  {v}: mean {sel[v][0]*100:6.1f}%  worst {sel[v][1]*100:6.1f}%   '+' '.join(f'{c[:4]}:{s*100:6.1f}' for c,s in zip(CITIES,sk)))
        best=max(V,key=lambda v:sel[v]); log(f'  SELECTED: {best}')
        # thresholds from 2025 held-out predictions of selected variant (fit 2024)
        yv,pv=[],[]
        for c in CITIES:
            t=[r for r in val if r['city']==c]; p,_=fit_predict(best,kind,fit,c,t); yv+=list(Y(t)); pv+=list(p)
        yellow,red=pick_thresholds(np.array(yv),np.array(pv)); log(f'  thresholds chosen on 2025: yellow {yellow:.2f}, red '+(f'{red:.2f}' if red is not None else 'none (precision 0.80 unattainable above yellow)'))
        fit2=period(R,'2024-01-01','2025-12-31'); test=period(R,'2026-01-01','2026-09-21'); task=dict(key=key,selected=best,selection=sel,thresholds=dict(yellow=yellow,red=red),cities={},variants={})
        allY,allP,allSeasG,allOrig,allOrigSeas=[],[],[],[],[]
        for v in V:
            res={}
            for c in CITIES:
                t=[r for r in test if r['city']==c]; y=Y(t); p,_=fit_predict(v,kind,fit2,c,t)
                qp=season([r for r in fit2 if r['city']!=c],t); ql=season([r for r in fit2 if r['city']==c],t)
                res[c]=dict(n=len(y),events=int(y.sum()),auc=float(AUC(y,p)) if 0<y.sum()<len(y) else None,skillPooled=skill(y,p,qp),skillOwn=skill(y,p,ql),ci=bs_ci(y,p,qp,[r['issueDate'] for r in t]) if y.sum() else None,meanP=float(p.mean()),rate=float(y.mean()))
                if v==best:
                    ok=[j for j,r in enumerate(t) if (key,r['group'],r['issueDate']) in orig]
                    for j in ok:
                        o=orig[(key,t[j]['group'],t[j]['issueDate'])]; allY.append(y[j]); allP.append(p[j]); allOrig.append(o[0]); allOrigSeas.append(o[1])
                    res[c]['pred']=p
            task['variants'][v]={c:{k:x for k,x in d.items() if k!='pred'} for c,d in res.items()}
            flag='  <== selected' if v==best else ''
            log(f'  2026 test {v}{flag}')
            for c in CITIES:
                d=res[c]; ci=d['ci'] or [float('nan')]*2; auc=f"{d['auc']:.3f}" if d['auc'] is not None else '  n/a'
                log(f"     {c:10} n={d['n']:5} ev={d['events']:4} AUC {auc}  vs pooled-season {d['skillPooled']*100:7.1f}% [{ci[0]*100:6.1f},{ci[1]*100:6.1f}]  vs own-city-season {d['skillOwn']*100:7.1f}%  meanP {d['meanP']:.3f} rate {d['rate']:.3f}")
            if v==best: task['cities']=task['variants'][v]; bestres=res
        # head-to-head vs original frozen model on identical rows, original's own group-seasonal baseline
        yA=np.array(allY); pA=np.array(allP); oA=np.array(allOrig); sA=np.array(allOrigSeas)
        task['headToHead']=dict(rows=len(yA),events=int(yA.sum()),originalSkill=skill(yA,oA,sA),forecastSkill=skill(yA,pA,sA),originalAUC=float(AUC(yA,oA)),forecastAUC=float(AUC(yA,pA)))
        hh=task['headToHead']; log(f"  HEAD-TO-HEAD same {hh['rows']} rows (baseline = original same-group seasonal): original {hh['originalSkill']*100:.1f}%  ->  forecast+calibration {hh['forecastSkill']*100:.1f}%   AUC {hh['originalAUC']:.3f} -> {hh['forecastAUC']:.3f}")
        # thresholds on 2026 + reliability (held-out selected predictions)
        yT=np.concatenate([Y([r for r in test if r['city']==c]) for c in CITIES]); pT=np.concatenate([bestres[c]['pred'] for c in CITIES])
        months=len(set(r['targetDate'][:7] for r in test))*21
        task['alerts']=dict(yellow=alert_stats(yT,pT,yellow,months),red=alert_stats(yT,pT,red,months) if red is not None else None)
        for k in ['yellow','red']:
            a=task['alerts'][k]
            if a is None: log(f'  2026 {k:6}: not defined'); continue
            log(f"  2026 {k:6} >= {a['threshold']:.2f}: caught {a['hitRate']*100:5.1f}% of events, {a['precision']*100:5.1f}% of alerts correct, {a['falseAlertsPerGroupMonth']:.2f} false alerts per weather-group-month")
        bins=np.linspace(0,1,11); rel=[]
        for lo,hi in zip(bins[:-1],bins[1:]):
            m=(pT>=lo)&(pT<hi if hi<1 else pT<=hi)
            if m.sum(): rel.append(dict(lo=float(lo),hi=float(hi),n=int(m.sum()),predicted=float(pT[m].mean()),observed=float(yT[m].mean())))
        task['reliability']=rel; log('  reliability 2026: '+'  '.join(f"[{r['lo']:.1f}-{r['hi']:.1f}) n={r['n']} p={r['predicted']:.2f} obs={r['observed']:.2f}" for r in rel))
        summary[key]=task
        # parameters: deployment (all cities pooled) + heldout (scored configuration)
        params[key]=dict(label=key,variant=best,features={'rain':['log1p(total mm)','log1p(max daily mm)'],'dry':['log1p(total mm)','log1p(max daily mm)'],'heat':['max air C','max air C^2/100'],'compound':['max air C','max air C^2/100','log1p(total mm)']}[kind],
            leads=list(range(1,h+1)),thresholds=dict(yellow=yellow,red=red),
            deployment={c:fit_predict(best,kind,fit2,c,[r for r in fit2 if r['city']==c][:1],deploy=True)[1] for c in CITIES},
            heldout={c:fit_predict(best,kind,fit2,c,[r for r in fit2 if r['city']==c][:1])[1] for c in CITIES})
json.dump(summary,open(os.path.join(OUT,'multi_summary.json'),'w'),indent=1,default=float)
json.dump(dict(source='Open-Meteo Previous Runs API; daily local-time totals at weather-group centroid; lead L for day L of the window',fitPeriod='2024-01-01..2025-12-31',
    formula={'A/B':'p = sigmoid(intercept + dot(x, coef))','C':'scale precipitation features: log1p(expm1(x_j)*precipScale), then A','D':'p = sigmoid(a + b*dot(x, pooled_coef)); pooled_intercept unused'},
    tasks=params),open(os.path.join(OUT,'calibration_params_all_tasks.json'),'w'),indent=1)
open(os.path.join(OUT,'multi_output.txt'),'w').write('\n'.join(lines))
