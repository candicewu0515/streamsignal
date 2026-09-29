"""Refresh the offline browser bundle after exporting NWP deployment parameters.
The reviewed evaluation metrics in data/nwp-calibration.json are not regenerated.
Run build_field_release.py afterwards to version the offline cache.
"""
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
params=root/'results/nwp_calibration/calibration_params.json'
catalog=root/'data/nwp-calibration.json'
data=json.loads(catalog.read_text())
data['parameters']=json.loads(params.read_text())
data['parameterSha256']=hashlib.sha256(params.read_bytes()).hexdigest()
data.pop('v6',None)
data.pop('v6Sha256',None)
multi=root/'results/nwp_multi/calibration_params_all_tasks.json'
if multi.exists():
 data['multi']=json.loads(multi.read_text())
 data['multi']['version']='nwp-eight-tasks-2024-2025-v1'
 data['multiSha256']=hashlib.sha256(multi.read_bytes()).hexdigest()
 report=json.loads((root/'results/nwp_multi/multi_summary.json').read_text())
 (root/'data/nwp-research.js').write_text('window.StreamNWPResearch='+json.dumps(report,separators=(',',':'))+';\n')
 for key,t in data['multi']['tasks'].items():
  t['policy']={**t['thresholds'],'singleLevel':not key.startswith('rain_'),'selectionPeriod':'2025','fitPeriod':'2024'}
  t['metrics']=report[key]['cities']
  t['headToHead']=report[key]['headToHead']
catalog.write_text(json.dumps(data,indent=2)+'\n')
bundle=root/'assets/nwp.js'
lines=bundle.read_text().splitlines()
assert lines[2].startswith('const data=')
lines[2]='const data='+json.dumps(data,separators=(',',':'))+';'
bundle.write_text('\n'.join(lines)+'\n')
print('NWP offline bundle updated:',data['version'],data['parameterSha256'])
