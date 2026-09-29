"""Export the existing logistic specification; verify parity with frozen test predictions."""
import json
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from threadpoolctl import threadpool_limits
import train_multihazard as m
D=m.base.load_data(); frozen=json.loads((m.ROOT/'data/multihazard.js').read_text().split('=',1)[1].rstrip(';\n'));out={'version':'v3-logistic-export-v1','features':m.FEATURES,'models':{}}
with threadpool_limits(limits=1):
 for key,task in frozen['tasks'].items():
  h=task['horizon'];split=m.splits(m.build(D,h,key.split('_')[0]));model=make_pipeline(StandardScaler(),LogisticRegression(C=.1,max_iter=2000,random_state=42));model.fit([r['features'] for r in split['train']],[r['label'] for r in split['train']]);p=model.predict_proba([r['features'] for r in split['test']])[:,1];error=float(np.max(np.abs(p-np.array([r[5] for r in task['predictions']]))));assert error<1e-10,(key,error)
  scale,lr=model.steps[0][1],model.steps[1][1];out['models'][key]={'mean':scale.mean_.tolist(),'scale':scale.scale_.tolist(),'coef':lr.coef_[0].tolist(),'intercept':float(lr.intercept_[0]),'parityMaxError':error}
(m.ROOT/'data/live-models.json').write_text(json.dumps(out,separators=(',',':')))
(m.ROOT/'data/sites.json').write_text(json.dumps([ {**{k:s[k] for k in ['code','name','city','cityName','lat','lon','group']},'context':{'impervious':(s.get('urban') or {}).get('imperviousPct500m'),'vegetation':(s.get('urban') or {}).get('vegCoverFrac500m'),'sewageDistance':(s.get('urban') or {}).get('distanceToSewageStations'),'urbanDate':(s.get('urban') or {}).get('samplingDate'),'health':[{'date':h.get('samplingDate'),'fecal':h.get('scaledFecalRisk'),'pathogen':h.get('scaledPathogenRisk'),'arg':h.get('scaledArgRisk')} for h in s.get('health',[])]}} for s in D['sites']],separators=(',',':')))
print('Exported 8 models with frozen-prediction parity, plus small site catalogue.')
