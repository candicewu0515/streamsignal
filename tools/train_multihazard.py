"""Reproduce the pre-fit multi-hazard protocol. No network required."""
from pathlib import Path
import json,csv,datetime as dt
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from threadpoolctl import threadpool_limits
import train_forecast as base
ROOT=Path(__file__).resolve().parents[1]
FEATURES=base.FEATURES[:10]+['Previous rainfall','Log rainfall','Rain 3d','Rain 7d','Mean temperature 3d','Mean temperature 7d','Maximum temperature 7d','Humidity 3d','Humidity 7d','Pressure change 1d','Pressure change 3d','Temperature change 1d','Maximum wind 7d','Season sine','Season cosine']
HAZARDS={'rain':'Rain accumulation','heat':'Heat exposure','dry':'Low rainfall','compound':'Hot and dry'}
def label(window,kind,h):
    rain=round(sum(r[4] for r in window),6);heat=max(r[2] for r in window)
    return int({'rain':rain>=(20 if h==3 else 40),'heat':heat>=30,'dry':rain<h,'compound':heat>=30 and rain<h}[kind])
def build(data,h,kind):
    rows=[]
    for g,series in enumerate(data['series']):
        for i in range(6,len(series)-h):
            past=series[i-6:i+1];future=series[i+1:i+h+1]
            if any(v is None for day in past for v in day) or any(day[4] is None or day[2] is None for day in future):continue
            now=series[i];a=2*np.pi*base.doy(data['dates'][i+1])/366
            f=now+[series[i-1][4],np.log1p(now[4]),sum(x[4] for x in past[-3:]),sum(x[4] for x in past),np.mean([x[0] for x in past[-3:]]),np.mean([x[0] for x in past]),max(x[2] for x in past),np.mean([x[3] for x in past[-3:]]),np.mean([x[3] for x in past]),now[7]-series[i-1][7],now[7]-series[i-3][7],now[0]-series[i-1][0],max(x[6] for x in past),np.sin(a),np.cos(a)]
            rows.append(dict(group=g,issueDate=data['dates'][i],targetDate=data['dates'][i+1],endDate=data['dates'][i+h],features=f,label=label(future,kind,h),pastState=label(past[-h:],kind,h),rain=round(sum(x[4] for x in future),4),heat=max(x[2] for x in future)))
    return rows
def splits(rows):
    return {k:[r for r in rows if r['targetDate']>=lo and r['endDate']<=hi] for k,lo,hi in [('train','2023-01-01','2024-12-31'),('validation','2025-01-01','2025-12-31'),('test','2026-01-01','2026-09-21')]}
def pooled_season(train,target):
    days=np.array([base.doy(r['targetDate']) for r in train]);y=np.array([r['label'] for r in train]);cache={};out=[]
    for r in target:
        d=base.doy(r['targetDate'])
        if d not in cache:
            delta=np.abs(days-d);mask=np.minimum(delta,366-delta)<=30;cache[d]=float((y[mask].sum()+1)/(mask.sum()+2))
        out.append(cache[d])
    return np.array(out)
def fit(split,geographic=False):
    X={k:np.array([r['features'] for r in rows]) for k,rows in split.items()};y={k:np.array([r['label'] for r in rows]) for k,rows in split.items()}
    models={'logistic':make_pipeline(StandardScaler(),LogisticRegression(C=.1,max_iter=2000,random_state=42)), 'boosted':HistGradientBoostingClassifier(max_iter=100,learning_rate=.06,max_leaf_nodes=15,min_samples_leaf=40,l2_regularization=2,early_stopping=False,random_state=42)}
    p={k:{} for k in ['validation','test']}
    for name,model in models.items():
        model.fit(X['train'],y['train'])
        for k in p:p[k][name]=model.predict_proba(X[k])[:,1]
    for k in p:
        p[k]['seasonal']=pooled_season(split['train'],split[k]) if geographic else base.seasonal_prob(split['train'],split[k])
        states={v:[r['label'] for r in split['train'] if r['pastState']==v] for v in [0,1]}
        p[k]['persistence']=np.array([(sum(states[r['pastState']])+1)/(len(states[r['pastState']])+2) for r in split[k]])
    thresholds={name:base.select_threshold(y['validation'],prob) for name,prob in p['validation'].items()}
    scores={k:{name:base.metrics(y[k],prob,thresholds[name]) for name,prob in p[k].items()} for k in p}
    chosen=min(models,key=lambda name:scores['validation'][name]['brier'])
    return chosen,scores,p,y

def main():
    data=base.load_data();group_city={g:next(s['cityName'] for s in data['sites'] if s['group']==g) for g in range(len(data['series']))};tasks={};predictions=[];regional=[]
    for h in [3,7]:
        for kind,name in HAZARDS.items():
            key=f'{kind}_{h}';split=splits(build(data,h,kind));chosen,scores,probs,y=fit(split)
            test=split['test'];selected=probs['test'][chosen];seasonal=probs['test']['seasonal']
            task=dict(key=key,name=name,horizon=h,selected=chosen,features=FEATURES,split={k:dict(n=len(v),events=sum(r['label'] for r in v),targetStart=min(r['targetDate'] for r in v),targetEnd=max(r['endDate'] for r in v)) for k,v in split.items()},metrics=scores,brierSkill=1-scores['test'][chosen]['brier']/scores['test']['seasonal']['brier'],interval=base.block_difference(test,y['test'],selected,seasonal),reliability=base.reliability(y['test'],selected),thresholds=[base.metrics(y['test'],selected,t) for t in [.1,.2,.3,.4,.5,.6,.7,.8,.9]],monthly=[])
            for month in sorted({r['targetDate'][:7] for r in test}):
                mask=np.array([r['targetDate'].startswith(month) for r in test]);task['monthly'].append(dict(month=month,n=int(mask.sum()),events=int(y['test'][mask].sum()),modelBrier=float(np.mean((selected[mask]-y['test'][mask])**2)),seasonalBrier=float(np.mean((seasonal[mask]-y['test'][mask])**2))))
            task['predictions']=[]
            for j,r in enumerate(test):
                task['predictions'].append([r['group'],r['issueDate'],r['targetDate'],r['endDate'],r['label'],float(selected[j]),float(seasonal[j]),float(probs['test']['persistence'][j]),r['rain'],r['heat']])
                predictions.append(dict(task=key,region=group_city[r['group']],weatherGroup=r['group']+1,issueDate=r['issueDate'],targetStart=r['targetDate'],targetEnd=r['endDate'],event=r['label'],selectedModel=chosen,probability=float(selected[j]),seasonalProbability=float(seasonal[j]),persistenceProbability=float(probs['test']['persistence'][j]),observedRainMm=r['rain'],observedMaxAirTemperatureC=r['heat']))
            tasks[key]=task
            print(key,chosen,'Brier skill',round(100*task['brierSkill'],2),'%',flush=True)
            if key=='rain_3':
                for city in sorted(set(group_city.values())):
                    local={k:[r for r in rows if (group_city[r['group']]==city if k=='test' else group_city[r['group']]!=city)] for k,rows in split.items()}
                    selected_name,sc,_,_=fit(local,True);regional.append(dict(city=city,selected=selected_name,trainingCities=sorted(set(group_city.values())-{city}),trainRows=len(local['train']),validationRows=len(local['validation']),test=sc['test'],skill=1-sc['test'][selected_name]['brier']/sc['test']['seasonal']['brier']))
    summary=dict(version=3,protocol='docs/MULTIHAZARD_PROTOCOL.md',tasks=tasks,geographic=regional,predictionColumns=['group','issueDate','targetStart','targetEnd','event','probability','seasonalProbability','persistenceProbability','rainMm','maxAirTemperatureC'])
    (ROOT/'data/multihazard.js').write_text('window.STREAM_MULTI='+json.dumps(summary,separators=(',',':'))+';\n')
    slim={**summary,'tasks':{k:{a:b for a,b in t.items() if a!='predictions'} for k,t in tasks.items()}}
    (ROOT/'results/multihazard_metrics.json').write_text(json.dumps(slim,indent=2));base.write_csv(ROOT/'results/multihazard_predictions.csv',predictions)
    base.write_csv(ROOT/'results/multihazard_comparison.csv',[dict(task=k,model=name,selected=name==t['selected'],**m) for k,t in tasks.items() for name,m in t['metrics']['test'].items()])
    (ROOT/'results/geographic_stress_test.json').write_text(json.dumps(regional,indent=2))
if __name__=='__main__':
    with threadpool_limits(limits=1):main()
