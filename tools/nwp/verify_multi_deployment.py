from pathlib import Path
import json,sys,numpy as np
source=Path(__file__).with_name('evaluate_multi.py').resolve()
root=source.parents[2]
ns={'__file__':str(source)}
exec(compile(source.read_text().split("V=['A','B','C','D']")[0],str(source),'exec'),ns)
p=json.loads((root/'results/nwp_multi/calibration_params_all_tasks.json').read_text());fixtures=[];audit=[]
for key,t in p['tasks'].items():
 kind,h=key.split('_');h=int(h);rs=ns['rows'](kind,h);fit=ns['period'](rs,'2024-01-01','2025-12-31');test=ns['period'](rs,'2026-01-01','2026-09-21')
 from datetime import date
 gaps=sum((date.fromisoformat(r['endDate'])-date.fromisoformat(r['issueDate'])).days!=h for r in rs)
 assert not gaps,(key,gaps)
 for city in ns['CITIES']:
  target=[r for r in test if r['city']==city][::37]
  pred,profile=ns['fit_predict'](t['variant'],kind,fit,city,target,deploy=True)
  for name in ['coef','pooled_coef']:
   if name in profile: assert np.allclose(profile[name],t['deployment'][city][name],rtol=1e-10,atol=1e-10),(key,city,name)
  assert profile==t['deployment'][city],(key,city,'profile mismatch')
  fixtures.extend(dict(task=key,city=city,features=r['x'],expected=float(y)) for r,y in zip(target,pred))
 audit.append(dict(task=key,fitRows=len(fit),testRows=len(test),calendarGapWindows=gaps))
 print(key,'refit verified',flush=True)
(root/'tests/nwp-multi-parity.json').write_text(json.dumps(fixtures))
(root/'results/nwp_multi/integration_audit.json').write_text(json.dumps(dict(profilesRefitted=40,fixtures=len(fixtures),tasks=audit),indent=2)+'\n')
