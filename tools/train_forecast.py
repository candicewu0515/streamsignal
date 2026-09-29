"""Reproduce the prespecified next-day rainfall experiment.
Requires NumPy, scikit-learn and matplotlib; see requirements-model.txt.
No network or credentials are used. Split membership follows TARGET date.
"""
from pathlib import Path
import csv, datetime as dt, json, platform
import numpy as np
import sklearn
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (brier_score_loss, roc_auc_score, average_precision_score,
                             precision_recall_curve, confusion_matrix)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
FEATURES=['Temperature mean','Temperature minimum','Temperature maximum','Relative humidity',
          'Daily rainfall','Mean wind','Maximum wind','Surface pressure','Cloud cover','Solar radiation',
          'Log rainfall','Previous-day rainfall','Three-day rainfall','Three-day mean temperature',
          'Three-day mean humidity','Pressure change','Season sine','Season cosine']

def load_data():
    s=(ROOT/'data/snapshot.js').read_text(encoding='utf-8')
    return json.loads(s.removeprefix('window.STREAM_DATA=').removesuffix(';\n'))

def doy(date):
    day=dt.date.fromisoformat(date)
    return (dt.date(2000,day.month,day.day)-dt.date(2000,1,1)).days

def build_rows(data):
    rows=[]
    for g,series in enumerate(data['series']):
        for i in range(2,len(data['dates'])-1):
            past=series[i-2:i+1];target=series[i+1]
            if any(v is None for day in past for v in day) or target[4] is None:continue
            now=series[i];angle=2*np.pi*doy(data['dates'][i+1])/366
            features=now+[np.log1p(now[4]),series[i-1][4],sum(r[4] for r in past),
                          sum(r[0] for r in past)/3,sum(r[3] for r in past)/3,
                          now[7]-series[i-1][7],np.sin(angle),np.cos(angle)]
            rows.append(dict(group=g,issueDate=data['dates'][i],targetDate=data['dates'][i+1],
                             targetRain=target[4],label=int(target[4]>=10),features=features))
    return rows

def select_threshold(y,p):
    precision,recall,thresholds=precision_recall_curve(y,p)
    f1=np.divide(2*precision[:-1]*recall[:-1],precision[:-1]+recall[:-1],out=np.zeros_like(thresholds),where=(precision[:-1]+recall[:-1])>0)
    best=np.flatnonzero(np.isclose(f1,f1.max(),rtol=0,atol=1e-12))[-1]
    return float(thresholds[best])

def metrics(y,p,threshold):
    tn,fp,fn,tp=confusion_matrix(y,p>=threshold,labels=[0,1]).ravel()
    precision=tp/(tp+fp) if tp+fp else 0
    recall=tp/(tp+fn) if tp+fn else 0
    return dict(n=int(len(y)),events=int(y.sum()),eventRate=float(y.mean()),brier=float(brier_score_loss(y,p)),
                rocAuc=float(roc_auc_score(y,p)) if len(set(y))==2 else None,
                averagePrecision=float(average_precision_score(y,p)) if y.sum() else None,
                threshold=float(threshold),precision=float(precision),recall=float(recall),
                f1=float(2*precision*recall/(precision+recall)) if precision+recall else 0,
                tn=int(tn),fp=int(fp),fn=int(fn),tp=int(tp))

def seasonal_prob(train,rows):
    labels={}
    for g in sorted({r['group'] for r in train}):
        selected=[r for r in train if r['group']==g]
        labels[g]=(np.array([doy(r['targetDate']) for r in selected]),np.array([r['label'] for r in selected]))
    cache={}
    out=[]
    for r in rows:
        key=(r['group'],doy(r['targetDate']))
        if key not in cache:
            days,ys=labels[key[0]];distance=np.abs(days-key[1]);match=np.minimum(distance,366-distance)<=30
            cache[key]=float((ys[match].sum()+1)/(match.sum()+2))
        out.append(cache[key])
    return np.array(out)

def reliability(y,p):
    out=[]
    for lo,hi in zip(np.linspace(0,1,11)[:-1],np.linspace(0,1,11)[1:]):
        mask=(p>=lo)&((p<hi) if hi<1 else (p<=hi))
        out.append(dict(lower=float(lo),upper=float(hi),count=int(mask.sum()),
                        meanPrediction=float(p[mask].mean()) if mask.any() else None,
                        observedRate=float(y[mask].mean()) if mask.any() else None))
    return out

def block_difference(rows,y,model,baseline,iterations=300):
    start=dt.date.fromisoformat(min(r['targetDate'] for r in rows));end=dt.date.fromisoformat(max(r['targetDate'] for r in rows))
    dates=[(start+dt.timedelta(days=i)).isoformat() for i in range((end-start).days+1)]
    contributions=(baseline-y)**2-(model-y)**2
    day_lookup={date:np.array([i for i,r in enumerate(rows) if r['targetDate']==date],dtype=int) for date in dates}
    rng=np.random.default_rng(42);values=[]
    for _ in range(iterations):
        chosen=[]
        while len(chosen)<len(dates):
            i=int(rng.integers(0,len(dates)-7+1));chosen.extend(dates[i:i+7])
        indices=np.concatenate([day_lookup[d] for d in chosen[:len(dates)]])
        values.append(float(contributions[indices].mean()))
    return dict(method='Moving-block bootstrap; all weather groups retained together by target day',blockCalendarDays=7,resamples=iterations,seed=42,
                estimate=float(contributions.mean()),lower=float(np.quantile(values,.025)),upper=float(np.quantile(values,.975)))

def write_csv(path,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def plot_outputs(result,dest):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#163850','text.color':'#163850','axes.edgecolor':'#bccddb','xtick.color':'#45677f','ytick.color':'#45677f'})
    fig,axes=plt.subplots(1,3,figsize=(13.5,4.2),layout='constrained')
    models=result['test'];labels=['Logistic model','Seasonal baseline','Constant baseline'];colours=['#087f8b','#547b98','#9ab0c1']
    briers=[models[k]['brier'] for k in ['logistic','seasonal','constant']]
    axes[0].barh(labels[::-1],briers[::-1],color=colours[::-1]);axes[0].set_xlabel('Brier score (lower is better)');axes[0].set_title('A  Temporal test performance',loc='left',fontweight='bold',pad=14)
    for i,v in enumerate(briers[::-1]):axes[0].text(v+.001,i,f'{v:.4f}',va='center',fontsize=9)
    axes[0].set_xlim(0,max(briers)*1.25)
    for key,label,color in zip(['logistic','seasonal'],labels,colours):
        bins=[x for x in result['reliability'][key] if x['count']]
        axes[1].plot([x['meanPrediction'] for x in bins],[x['observedRate'] for x in bins],marker='o',color=color,label=label)
    axes[1].plot([0,1],[0,1],'--',color='#a4b5c3',linewidth=1);axes[1].set(xlim=(0,1),ylim=(0,1),xlabel='Mean predicted probability',ylabel='Observed event frequency');axes[1].legend(frameon=False,fontsize=8);axes[1].set_title('B  Reliability (10 fixed bins)',loc='left',fontweight='bold',pad=14)
    coefficients=sorted(result['coefficients'],key=lambda x:abs(x['coefficient']),reverse=True)[:8][::-1]
    axes[2].barh([r['feature'] for r in coefficients],[r['coefficient'] for r in coefficients],color=['#087f8b' if r['coefficient']>0 else '#c06646' for r in coefficients]);axes[2].axvline(0,color='#8ba6ba',linewidth=1);axes[2].set_xlabel('Standardized log-odds coefficient');axes[2].set_title('C  Model associations, not causes',loc='left',fontweight='bold',pad=14)
    fig.suptitle('Next-day recorded rainfall ≥10 mm · 2026 temporal test',fontweight='bold',fontsize=14)
    fig.savefig(dest/'forecast_evaluation.png',dpi=200,facecolor='white');fig.savefig(dest/'forecast_evaluation.svg',facecolor='white');plt.close(fig)

def main():
    data=load_data();rows=build_rows(data)
    split={name:[r for r in rows if lo<=r['targetDate']<=hi] for name,lo,hi in [('train','2023-01-01','2024-12-31'),('validation','2025-01-01','2025-12-31'),('test','2026-01-01','2026-09-21')]}
    matrices={k:np.array([r['features'] for r in v],dtype=float) for k,v in split.items()};ys={k:np.array([r['label'] for r in v]) for k,v in split.items()}
    candidates=[];models={}
    for strength in [.01,.1,1.,10.]:
        model=make_pipeline(StandardScaler(),LogisticRegression(C=strength,solver='lbfgs',max_iter=2000,tol=1e-8,random_state=42))
        model.fit(matrices['train'],ys['train']);prob=model.predict_proba(matrices['validation'])[:,1]
        candidates.append(dict(C=strength,validationBrier=float(brier_score_loss(ys['validation'],prob)),iterations=int(model[-1].n_iter_[0])));models[strength]=model
    chosen=min(candidates,key=lambda c:(c['validationBrier'],c['C']));model=models[chosen['C']]
    train_rate=float(ys['train'].mean());probs={}
    for name in ['validation','test']:
        probs[name]={'logistic':model.predict_proba(matrices[name])[:,1],
                     'seasonal':seasonal_prob(split['train'],split[name]),'constant':np.full(len(split[name]),train_rate)}
    thresholds={k:select_threshold(ys['validation'],p) for k,p in probs['validation'].items()}
    scores={name:{k:metrics(ys[name],p,thresholds[k]) for k,p in probs[name].items()} for name in ['validation','test']}
    monthly=[]
    for month in sorted({r['targetDate'][:7] for r in split['test']}):
        mask=np.array([r['targetDate'].startswith(month) for r in split['test']]);monthly.append(dict(month=month,n=int(mask.sum()),events=int(ys['test'][mask].sum()),modelBrier=float(brier_score_loss(ys['test'][mask],probs['test']['logistic'][mask])),seasonalBrier=float(brier_score_loss(ys['test'][mask],probs['test']['seasonal'][mask]))))
    audit={name:dict(rows=len(v),events=int(ys[name].sum()),eventRate=float(ys[name].mean()),targetStart=min(r['targetDate'] for r in v),targetEnd=max(r['targetDate'] for r in v),groups=len({r['group'] for r in v})) for name,v in split.items()}
    coefficients=[dict(feature=feature,coefficient=float(weight)) for feature,weight in zip(FEATURES,model[-1].coef_[0])]
    result=dict(protocol='docs/FORECAST_PROTOCOL.md',target='Next calendar day recorded rainfall >= 10 mm',version=2,
        timing='Issue after complete daily weather is available; retrospective hindcast, not a live forecast',
        split=audit,candidates=candidates,selectedC=chosen['C'],featureNames=FEATURES,thresholdSelection='Maximum validation F1; ties choose higher threshold',
        validation=scores['validation'],test=scores['test'],coefficients=coefficients,monthly=monthly,
        reliability={k:reliability(ys['test'],p) for k,p in probs['test'].items()},
        brierSkill=1-scores['test']['logistic']['brier']/scores['test']['seasonal']['brier'],
        brierDifferenceInterval=block_difference(split['test'],ys['test'],probs['test']['logistic'],probs['test']['seasonal']),
        model=dict(means=model[0].mean_.tolist(),scales=model[0].scale_.tolist(),coefficients=model[-1].coef_[0].tolist(),intercept=float(model[-1].intercept_[0])),
        runtime=dict(python=platform.python_version(),numpy=np.__version__,sklearn=sklearn.__version__,matplotlib=matplotlib.__version__))
    dest=ROOT/'results';dest.mkdir(exist_ok=True)
    (dest/'forecast_metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    predictions=[]
    for i,r in enumerate(split['test']):
        representative=next(s for s in data['sites'] if s['group']==r['group'])
        predictions.append(dict(weatherGroup=r['group']+1,region=representative['cityName'],issueDate=r['issueDate'],targetDate=r['targetDate'],recordedRainMm=r['targetRain'],event=r['label'],modelProbability=float(probs['test']['logistic'][i]),seasonalProbability=float(probs['test']['seasonal'][i]),constantProbability=train_rate,modelFlag=int(probs['test']['logistic'][i]>=thresholds['logistic']),threshold=thresholds['logistic']))
    write_csv(dest/'forecast_test_predictions.csv',predictions);write_csv(dest/'forecast_monthly.csv',monthly);write_csv(dest/'forecast_coefficients.csv',coefficients)
    payload={**result,'predictions':[[r['weatherGroup']-1,r['issueDate'],r['targetDate'],r['recordedRainMm'],r['event'],r['modelProbability'],r['seasonalProbability']] for r in predictions]}
    (ROOT/'data/forecast.js').write_text('window.STREAM_FORECAST='+json.dumps(payload,separators=(',',':'))+';\n',encoding='utf-8')
    plot_outputs(result,dest)
    print(json.dumps({k:result[k] for k in ['split','selectedC','test','brierSkill','brierDifferenceInterval']},indent=2))

if __name__=='__main__':main()
