"""Pre-declared: 4 calibration variants; choose by mean 2025 Brier skill across all 5 cities (fit on 2024), tie -> best worst city.
Then refit on 2024-2025 and report 2026 for ALL cities and ALL variants. Held-out city's 2026 data never used before scoring."""
import sys; import os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'..')); CACHE=os.path.join(HERE,'../../data/nwp_forecast_cache'); from nwp_common import *
from sklearn.linear_model import LogisticRegression
def X(rs): return np.array([r['nwp'] for r in rs])
def Y(rs): return np.array([r['label'] for r in rs])
def season(train,target):  # smoothed +-30 day frequency
    return mh.pooled_season(train,target)
def predict(variant,fit,city,target):
    other=[r for r in fit if r['city']!=city]; local=[r for r in fit if r['city']==city]
    if variant in ('B_local','D_pooled+local_offset') and len(set(Y(local)))<2: variant='A_pooled'  # fallback: no local events
    if variant=='A_pooled':
        return LogisticRegression(max_iter=1000).fit(X(other),Y(other)).predict_proba(X(target))[:,1]
    if variant=='B_local':
        return LogisticRegression(max_iter=1000).fit(X(local),Y(local)).predict_proba(X(target))[:,1]
    if variant=='C_bias_scaled':   # rescale forecast rain by each city's historical obs/forecast ratio, then pooled calibration
        ratio=lambda rs:np.mean([r['rain'] for r in rs])/np.mean([np.expm1(r['nwp'][0]) for r in rs])
        rat={c:ratio([r for r in fit if r['city']==c]) for c in set(r['city'] for r in fit)}
        sc=lambda rs:np.array([[np.log1p(np.expm1(r['nwp'][0])*rat[r['city']]),np.log1p(np.expm1(r['nwp'][1])*rat[r['city']])] for r in rs])
        return LogisticRegression(max_iter=1000).fit(sc(other),Y(other)).predict_proba(sc(target))[:,1]
    if variant=='D_pooled+local_offset':  # pooled slope, local intercept refit
        m=LogisticRegression(max_iter=1000).fit(X(other),Y(other)); z=X(local)@m.coef_[0]
        off=LogisticRegression(max_iter=1000).fit(z.reshape(-1,1),Y(local))
        return off.predict_proba((X(target)@m.coef_[0]).reshape(-1,1))[:,1]
V=['A_pooled','B_local','C_bias_scaled','D_pooled+local_offset']
cities=['Benevento','Coimbra','Ghent','Oslo','Toulouse']
for kind in (sys.argv[1:] or ['rain']):
    R=rows(kind)
    print(f'\n##### {kind} 3-day #####\n--- step 1: selection on 2025 (fit 2024) ---')
    fit=period(R,'2024-01-01','2024-12-31'); val=period(R,'2025-01-01','2025-12-31'); sel={}
    for v in V:
        sk=[]
        for c in cities:
            t=[r for r in val if r['city']==c]; y=Y(t); p=predict(v,fit,c,t); q=season([r for r in fit if r['city']!=c],t); sk.append(1-B(y,p)/B(y,q))
        sel[v]=(np.mean(sk),min(sk)); print(f'{v:24} mean {np.mean(sk)*100:6.1f}%  worst {min(sk)*100:6.1f}%  ', ' '.join(f'{c[:4]}:{s*100:5.1f}' for c,s in zip(cities,sk)))
    best=max(V,key=lambda v:sel[v]); print('SELECTED:',best)
    print('--- step 2: 2026 test (fit 2024-2025) ---')
    fit=period(R,'2024-01-01','2025-12-31'); test=period(R,'2026-01-01','2026-09-21')
    for v in V:
        print(f'{v}{"  <== selected" if v==best else ""}')
        for c in cities:
            t=[r for r in test if r['city']==c]; y=Y(t); p=predict(v,fit,c,t)
            qp=season([r for r in fit if r['city']!=c],t); ql=season([r for r in fit if r['city']==c],t); d=[r['issueDate'] for r in t]
            ci=bs_ci(y,p,qp,d); print(f'   {c:10} ev={y.sum():4} AUC {AUC(y,p):.3f}  vs pooled-season {100*(1-B(y,p)/B(y,qp)):6.1f}% [{ci[0]*100:6.1f},{ci[1]*100:6.1f}]   vs own-city-season {100*(1-B(y,p)/B(y,ql)):6.1f}%   meanP {p.mean():.3f} rate {y.mean():.3f}')
