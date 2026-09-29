/* Reproduce v4 decision-support outputs without retraining weather models. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),R=require('../assets/resilience.js'),C=require('../assets/core.js'),c={window:{}};
for(const f of ['snapshot','multihazard'])vm.runInNewContext(fs.readFileSync(path.join(root,`data/${f}.js`),'utf8'),c);
const D=c.window.STREAM_DATA,M=c.window.STREAM_MULTI,s={issue:'2026-02-02',hazard:'rain',city:'CO',site:'C2',yellow:20,red:40,horizon:3,outcome:'all',timelinePage:0};
function csv(name,rows){const keys=Object.keys(rows[0]);fs.writeFileSync(path.join(root,'results',name),C.csv([keys,...rows.map(r=>keys.map(k=>r[k]??''))]));}
const timeline=R.timeline(D,M,s);
csv('alert_timeline_Coimbra_rain3.csv',timeline.map(r=>({...r,city:'Coimbra',hazard:'rain',horizon:3,red_threshold_pct:40,provenance:'Historical weather replay; overlapping forecast windows'})));
const matrix=R.matrix(D),valid=matrix.filter(r=>r.sensitivity!==null),mx=R.median(valid.map(r=>r.exposure)),my=R.median(valid.map(r=>r.sensitivity));
csv('vulnerability_matrix.csv',matrix.map(r=>({site:r.site.code,city:r.site.cityName,weather_group:r.site.group+1,exposure_pct:r.exposure,sensitivity:r.sensitivity,observed_days:r.n,rain_days:r.rain,heat_days:r.heat,above_both_medians:r.sensitivity===null?'Unscored':r.exposure>=mx&&r.sensitivity>=my,period_start:'2025-01-01',period_end:D.meta.weatherEnd,provenance:'Exploratory historical index; not damage or health prediction'})));
csv('citizen_field_mapping.csv',R.mapping());
fs.writeFileSync(path.join(root,'examples','StreamSignal_warning_draft.txt'),R.alertDraft(D,M,s));
fs.writeFileSync(path.join(root,'examples','StreamSignal_citizen_task.txt'),R.citizenTask(D,M,s));
const audit={version:4,generatedFrom:'Frozen source snapshot and version 3 test predictions',defaultIssue:s.issue,defaultContextSite:s.site,timeline:{city:'Coimbra',hazard:'rain',horizon:3,redThresholdPct:40,rows:timeline.length,outcomes:Object.fromEntries(['Hit','False alarm','Miss','Correct rejection'].map(k=>[k,timeline.filter(r=>r.outcome===k).length])),example:timeline.find(r=>r.issued===s.issue&&r.group===7)},matrix:{sites:matrix.length,scored:valid.length,exposureMedian:mx,sensitivityMedian:my},combinedBackgroundFlagSites:D.sites.filter(site=>{const x=R.context(D,site,s.issue);return x.nearSewer&&x.highImpervious&&x.highFecal;}).map(x=>x.code)};
fs.writeFileSync(path.join(root,'results','resilience_audit.json'),JSON.stringify(audit,null,2)+'\n');console.log(JSON.stringify(audit,null,2));
