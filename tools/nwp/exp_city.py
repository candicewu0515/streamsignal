import numpy as np, sys
import os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'..'))
import train_forecast as base, train_multihazard as mh
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
data=base.load_data()
gc={g:next(s['cityName'] for s in data['sites'] if s['group']==g) for g in range(len(data['series']))}
rows=mh.build(data,3,'rain'); sp=mh.splits(rows)
# realistic "new city" info: each group's own 2023-2024 WEATHER history (no water labels exist anyway)
own_seasonal={}
def own_season(r):  # climatological freq from the same group's train-period windows
    return own_seasonal[r['group']](r)
for g in set(gc):
    tr=[r for r in sp['train'] if r['group']==g]
    d=np.array([base.doy(r['targetDate']) for r in tr]); y=np.array([r['label'] for r in tr]); c={}
    def f(r,d=d,y=y,c=c):
        k=base.doy(r['targetDate'])
        if k not in c:
            dl=np.abs(d-k); m=np.minimum(dl,366-dl)<=30; c[k]=(y[m].sum()+1)/(m.sum()+2)
        return c[k]
    own_seasonal[g]=f
stats={}
for g in set(gc):
    X=np.array([r['features'] for r in sp['train'] if r['group']==g]); stats[g]=(X.mean(0),X.std(0)+1e-9)
def feats(rs,mode):
    X=np.array([r['features'] for r in rs])
    if mode=='orig': return X
    Z=np.array([(np.array(r['features'])-stats[r['group']][0])/stats[r['group']][1] for r in rs])
    # keep season sin/cos raw
    Z[:,-2:]=X[:,-2:]
    if mode=='anom': return Z
    clim=np.array([[own_season(r)] for r in rs]); return np.hstack([Z,np.log(clim/(1-clim))])
def bs_ci(y,p,q,dates,n=300):
    rng=np.random.default_rng(42); days=np.array(sorted(set(dates))); idx={d:i for i,d in enumerate(days)}; di=np.array([idx[d] for d in dates])
    blocks=[np.where((di>=s)&(di<s+7))[0] for s in range(0,len(days),7)]; out=[]
    for _ in range(n):
        ii=np.concatenate([blocks[j] for j in rng.integers(0,len(blocks),len(blocks))])
        out.append(1-np.mean((p[ii]-y[ii])**2)/np.mean((q[ii]-y[ii])**2))
    return np.percentile(out,[5,95])
print(f"{'city':10}{'mode':7}{'AUC':>6}{'skill_vs_pooled':>17}{'90%CI':>16}{'skill_vs_ownclim':>18}")
for city in sorted(set(gc.values())):
    loc={k:[r for r in v if (gc[r['group']]==city)==(k=='test')] for k,v in sp.items()}
    yt=np.array([r['label'] for r in loc['test']]); dates=[r['issueDate'] for r in loc['test']]
    pooled=mh.pooled_season(loc['train'],loc['test']); own=np.array([own_season(r) for r in loc['test']])
    for mode in ['orig','anom','anom+clim']:
        m=make_pipeline(StandardScaler(),LogisticRegression(C=.1,max_iter=2000)); m.fit(feats(loc['train'],mode),[r['label'] for r in loc['train']])
        p=m.predict_proba(feats(loc['test'],mode))[:,1]
        s1=1-brier_score_loss(yt,p)/brier_score_loss(yt,pooled); s2=1-brier_score_loss(yt,p)/brier_score_loss(yt,own); ci=bs_ci(yt,p,pooled,dates)
        print(f"{city:10}{mode:10}{roc_auc_score(yt,p):6.3f}{s1*100:14.1f}%   [{ci[0]*100:5.1f},{ci[1]*100:5.1f}]{s2*100:14.1f}%")
