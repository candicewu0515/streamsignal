import sys,json,time,urllib.request,urllib.parse; import os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'..')); CACHE=os.path.join(HERE,'../../data/nwp_forecast_cache'); import train_forecast as base
os.makedirs(CACHE,exist_ok=True)
d=base.load_data(); groups={}
for s in d['sites']: groups.setdefault(s['group'],[]).append((s['lat'],s['lon'],s['cityName']))
V=','.join(f'{v}_previous_day{k}' for v in ['precipitation','temperature_2m'] for k in [1,2,3])
for g,pts in sorted(groups.items()):
    lat=sum(p[0] for p in pts)/len(pts); lon=sum(p[1] for p in pts)/len(pts)
    q=urllib.parse.urlencode(dict(latitude=round(lat,4),longitude=round(lon,4),start_date='2024-01-01',end_date='2026-09-24',hourly=V,timezone='auto'))
    for t in range(4):
        try:
            r=json.load(urllib.request.urlopen('https://previous-runs-api.open-meteo.com/v1/forecast?'+q,timeout=120));break
        except Exception as e: print('retry',g,e); time.sleep(10)
    r['city']=pts[0][2]; json.dump(r,open(os.path.join(CACHE,f'g{g}.json'),'w')); print(g,pts[0][2],len(pts),'sites',r.get('model') ,flush=True); time.sleep(1)
