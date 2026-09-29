import sys,json,numpy as np; import os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'..')); CACHE=os.path.join(HERE,'../../data/nwp_forecast_cache')
import train_forecast as base, train_multihazard as mh
from sklearn.metrics import brier_score_loss as B, roc_auc_score as AUC
data=base.load_data(); gc={g:next(s['cityName'] for s in data['sites'] if s['group']==g) for g in range(21)}
F={}
for g in range(21):
    h=json.load(open(os.path.join(CACHE,f'g{g}.json')))['hourly']; out={}
    for L in [1,2,3]:
        p=h[f'precipitation_previous_day{L}']; T=h[f'temperature_2m_previous_day{L}']; day={}
        for i,ts in enumerate(h['time']): day.setdefault(ts[:10],[]).append((p[i],T[i]))
        for d,v in day.items():
            if len(v)==24 and all(a is not None and b is not None for a,b in v): out[(d,L)]=(sum(a for a,_ in v),max(b for _,b in v))
    F[g]=out
idx={d:i for i,d in enumerate(data['dates'])}
def nwp_feat(r,kind='rain'):
    i=idx[r['issueDate']]; vals=[]
    for L in [1,2,3]:
        k=(data['dates'][i+L],L)
        if k not in F[r['group']]: return None
        vals.append(F[r['group']][k])
    rain=sum(v[0] for v in vals); tmax=max(v[1] for v in vals)
    return [np.log1p(rain),np.log1p(max(v[0] for v in vals))] if kind=='rain' else [tmax,tmax**2/100]
def rows(kind='rain'):
    rs=[r for r in mh.build(data,3,kind) if r['targetDate']>='2024-01-01']
    for r in rs: r['nwp']=nwp_feat(r,kind); r['city']=gc[r['group']]
    return [r for r in rs if r['nwp']]
def period(rs,lo,hi): return [r for r in rs if r['targetDate']>=lo and r['endDate']<=hi]
def bs_ci(y,p,q,dates,n=500):
    rng=np.random.default_rng(42); days=sorted(set(dates)); ix={d:i for i,d in enumerate(days)}; di=np.array([ix[d] for d in dates])
    blocks=[np.where((di>=s)&(di<s+7))[0] for s in range(0,len(days),7)]; out=[]
    for _ in range(n):
        ii=np.concatenate([blocks[j] for j in rng.integers(0,len(blocks),len(blocks))]); out.append(1-B(y[ii],p[ii])/B(y[ii],q[ii]))
    return np.percentile(out,[5,95])
