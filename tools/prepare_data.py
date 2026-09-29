"""Build the offline app payload from the downloaded OneAquaHealth CSV snapshot.
Usage: python3 tools/prepare_data.py --input ../OneAquaHealth [--map countries.geojson]
Only Python's standard library is required. No credentials or network requests.
"""
import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['t2mMeanC', 't2mMinC', 't2mMaxC', 'rh2mMeanPct', 'precipTotalMm',
          'windMeanMs', 'windMaxMs', 'surfacePressureMeanHpa', 'cloudCoverMeanPct', 'ssrdTotalMjm2']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--map', type=Path, help='Optional original Natural Earth GeoJSON; otherwise keep the bundled map.')
    args = parser.parse_args()
    def read(name):
        with (args.input / (name + '.csv')).open(encoding='utf-8-sig', newline='') as f:
            return list(csv.DictReader(f))
    sites, weather = read('sites'), read('weather_daily')
    health, nitrate, urban = read('health_risks'), read('nitrates'), read('urban_parameters')
    observed_dates = sorted({r['date'] for r in weather})
    start,end=map(dt.date.fromisoformat,[observed_dates[0],observed_dates[-1]])
    dates=[(start+dt.timedelta(days=i)).isoformat() for i in range((end-start).days+1)]
    missing_dates=sorted(set(dates)-set(observed_dates))
    grouped = collections.defaultdict(list)
    keys = set()
    for r in weather:
        key = (r['siteCode'], r['date'])
        assert key not in keys, key
        keys.add(key)
        grouped[r['siteCode']].append(r)
    series, signatures, by_site = [], {}, {}
    for code, rows in sorted(grouped.items()):
        rows.sort(key=lambda x: x['date'])
        lookup={r['date']:r for r in rows}
        packed = [[float(lookup[day][k]) if day in lookup and lookup[day][k] != '' else None for k in FIELDS] for day in dates]
        signature = hashlib.sha256(json.dumps(packed).encode()).hexdigest()
        if signature not in signatures:
            signatures[signature] = len(series)
            series.append(packed)
        by_site[code] = signatures[signature]
    def cast(row):
        return {k: (None if v == '' else float(v) if k not in ['researchSiteCode','siteCode','samplingDate','date'] else v)
                for k,v in row.items() if k != 'id'}
    def match(rows, key, code):
        return [cast(r) for r in rows if r[key] == code]
    packed_sites=[]
    for r in sites:
        code=r['code']
        packed_sites.append(dict(code=code,name=r['name'],city=r['city.id'],cityName=r['city.name'],
            lat=float(r['latitude']),lon=float(r['longitude']),group=by_site[code],
            health=match(health,'researchSiteCode',code),nitrate=match(nitrate,'siteCode',code),
            urban=next(iter(match(urban,'researchSiteCode',code)),None)))
    source_files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in args.input.glob('*.csv')}
    payload=dict(meta=dict(downloaded='2026-09-28',weatherStart=dates[0],weatherEnd=dates[-1],
        weatherRows=len(weather),healthRows=len(health),nitrateRows=len(nitrate),urbanRows=len(urban),
        baselineStart='2023-01-01',baselineEnd='2024-12-31',replayStart='2025-01-01',
        source='https://apps.oneaquahealth.eu/resmap/',api='https://api.enora-oah.eu/api',
        fields=FIELDS,sourceHashes=source_files,missingDates=missing_dates),dates=dates,sites=packed_sites,series=series)
    dest=ROOT/'data';dest.mkdir(exist_ok=True)
    (dest/'snapshot.js').write_text('window.STREAM_DATA='+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    if args.map:
        geo=json.loads(args.map.read_text())
        features=[]
        for f in geo['features']:
            prop=f['properties']
            if prop.get('CONTINENT') in ['Europe','Africa','Asia']:
                features.append(dict(type='Feature',properties=dict(name=prop.get('ADMIN','')),geometry=f['geometry']))
        (dest/'countries.js').write_text('window.STREAM_MAP='+json.dumps(dict(type='FeatureCollection',features=features),separators=(',',':'))+';\n')
    elif not (dest/'countries.js').exists():
        raise FileNotFoundError('Bundled map missing. Supply --map with the original Natural Earth GeoJSON.')
    audit=dict(sites=len(sites),weatherRows=len(weather),uniqueWeatherSeries=len(series),
        sharedWeatherGroups={str(i+1):[s['code'] for s in packed_sites if s['group']==i] for i in range(len(series))},
        missingDates=missing_dates,weatherMissingValuesInUniqueSeries=sum(v is None for g in series for r in g for v in r),
        healthMissingSites=[s['code'] for s in packed_sites if not s['health']],
        nitrateMissingSites=[s['code'] for s in packed_sites if not s['nitrate']],
        urbanMissingSites=[s['code'] for s in packed_sites if not s['urban']],
        dateCount=len(dates),weatherStart=dates[0],weatherEnd=dates[-1],sourceHashes=source_files)
    (dest/'audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in audit.items() if k not in ['sharedWeatherGroups','sourceHashes']},indent=2))

if __name__=='__main__':
    main()
