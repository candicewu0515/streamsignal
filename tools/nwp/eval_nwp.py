import sys,json,numpy as np; import os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'..')); CACHE=os.path.join(HERE,'../../data/nwp_forecast_cache')
import train_forecast as base, train_multihazard as mh
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss as B, roc_auc_score as AUC
data=base.load_data(); gc={g:next(s['cityName'] for s in data['sites'] if s['group']==g) for g in range(21)}
# daily forecast totals by lead: F[g][(date,lead)] -> (rain_mm, tmax)
F={}
for g in range(21):
    h=json.load(open(os.path.join(CACHE,f'g{g}.json')))['hourly']; t=h['time']; out={}
    for L in [1,2,3]:
        p=h[f'precipitation_previous_day{L}']; T=h[f'temperature_2m_previous_day{L}']; day={}
        for i,ts in enumerate(t):
            d=ts[:10]; day.setdefault(d,[]).append((p[i],T[i]))
        for d,v in day.items():
            if len(v)==24 and all(a is not None and b is not None for a,b in v):
                out[(d,L)]=(sum(a for a,_ in v),max(b for _,b in v))
    F[g]=out
idx={d:i for i,d in enumerate(data['dates'])}
def nwp_feat(r,kind):
    i=idx[r['issueDate']]; vals=[]
    for L in [1,2,3]:
        d=data['dates'][i+L]; k=(d,L)
        if k not in F[r['group']]: return None
        vals.append(F[r['group']][k])
    rain=sum(v[0] for v in vals); tmax=max(v[1] for v in vals)
    return [np.log1p(rain),np.log1p(max(v[0] for v in vals))] if kind=='rain' else [tmax, tmax**2/100]
def bs_ci(y,p,q,dates,n=500):
    rng=np.random.default_rng(42); days=sorted(set(dates)); ix={d:i for i,d in enumerate(days)}; di=np.array([ix[d] for d in dates])
    blocks=[np.where((di>=s)&(di<s+7))[0] for s in range(0,len(days),7)]; out=[]
    for _ in range(n):
        ii=np.concatenate([blocks[j] for j in rng.integers(0,len(blocks),len(blocks))]); out.append(1-B(y[ii],p[ii])/B(y[ii],q[ii]))
    return np.percentile(out,[5,95])
for kind in ['rain','heat']:
    rows=mh.build(data,3,kind); sp=mh.splits(rows)
    for r in rows: r['nwp']=nwp_feat(r,kind)
    print(f"\n=== {kind} 3-day, held-out city ===   (fit: other cities 2024-2025 NWP rows; test: held-out city 2026)")
    print(f"{'city':10}{'n':>5}{'ev':>5}{'AUC_nwp':>8}{'AUC_seas':>9}{'skill_vs_seasonal':>19}{'90% CI':>18}")
    for city in sorted(set(gc.values())):
        fit=[r for k in ['train','validation'] for r in sp[k] if gc[r['group']]!=city and r['nwp'] and r['targetDate']>='2024-01-01']
        test=[r for r in sp['test'] if gc[r['group']]==city and r['nwp']]
        m=LogisticRegression(C=1.0,max_iter=1000).fit([r['nwp'] for r in fit],[r['label'] for r in fit])
        p=m.predict_proba([r['nwp'] for r in test])[:,1]; y=np.array([r['label'] for r in test])
        seas=mh.pooled_season([r for r in sp['train'] if gc[r['group']]!=city],test)
        ci=bs_ci(y,p,seas,[r['issueDate'] for r in test]); sk=1-B(y,p)/B(y,seas)
        print(f"{city:10}{len(y):5}{y.sum():5}{AUC(y,p):8.3f}{AUC(y,seas):9.3f}{sk*100:17.1f}%   [{ci[0]*100:6.1f},{ci[1]*100:6.1f}]")
    n_all=len(sp['test']); n_ok=sum(1 for r in sp['test'] if r['nwp']); print(f"coverage: {n_ok}/{n_all} test windows have complete NWP")
