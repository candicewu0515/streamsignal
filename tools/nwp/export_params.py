"""Export variant D (pooled slope + local intercept) calibration parameters.
deployment: pooled fit on all 5 cities 2024-2025; heldout: pooled fit excludes that city (the configuration scored in results/).
p = sigmoid(local_a + local_b * (x . pooled_coef)); x = features below. Fallback to pooled-only if a city has no local events."""
import sys,os,json; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from nwp_common import *
from sklearn.linear_model import LogisticRegression
FEATS={'rain':['log1p(3-day forecast precipitation mm)','log1p(max daily forecast precipitation mm)'],'heat':['3-day max forecast air temperature C','(3-day max forecast air temperature C)^2/100']}
LABEL={'rain':'3-day precipitation >= 20 mm','heat':'3-day max air temperature >= 30 C'}
def X(rs): return np.array([r['nwp'] for r in rs])
def Y(rs): return np.array([r['label'] for r in rs])
def fitD(pool,local):
    m=LogisticRegression(max_iter=1000).fit(X(pool),Y(pool)); out=dict(pooled_coef=m.coef_[0].tolist(),pooled_intercept=float(m.intercept_[0]))
    if len(set(Y(local)))<2: out.update(local=None,fallback='pooled-only (no local events)'); return out
    z=X(local)@m.coef_[0]; o=LogisticRegression(max_iter=1000).fit(z.reshape(-1,1),Y(local))
    out.update(local=dict(a=float(o.intercept_[0]),b=float(o.coef_[0][0]),n=len(local),events=int(Y(local).sum()))); return out
cities=['Benevento','Coimbra','Ghent','Oslo','Toulouse']; res=dict(variant='D_pooled+local_offset',source='Open-Meteo Previous Runs API, leads 1-3 days, site-group centroid, local-time daily totals',fitPeriod='2024-01-01..2025-12-31',formula='p = sigmoid(a + b * dot(x, pooled_coef)); if local is null: p = sigmoid(pooled_intercept + dot(x, pooled_coef))',hazards={})
for kind in ['rain','heat']:
    fit=period(rows(kind),'2024-01-01','2025-12-31')
    h=dict(label=LABEL[kind],features=FEATS[kind],deployment={},heldout={})
    for c in cities:
        loc=[r for r in fit if r['city']==c]
        h['deployment'][c]=fitD(fit,loc); h['heldout'][c]=fitD([r for r in fit if r['city']!=c],loc)
    res['hazards'][kind]=h
json.dump(res,open(os.path.join(HERE,'../../results/nwp_calibration/calibration_params.json'),'w'),indent=2); print('written')
