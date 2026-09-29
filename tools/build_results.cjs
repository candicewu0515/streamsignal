/* Reproducible research outputs: node tools/build_results.cjs */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),Core=require('../assets/core.js'),A=require('../assets/analytics.js');
const ctx={window:{}};vm.runInNewContext(fs.readFileSync(path.join(root,'data/snapshot.js'),'utf8'),ctx);
const D=ctx.window.STREAM_DATA,E=Core.engine(D),start=D.dates.indexOf(D.meta.replayStart);
const reps=D.series.map((_,g)=>D.sites.find(s=>s.group===g));
const replay={version:2,baselineStart:D.meta.baselineStart,baselineEnd:D.meta.baselineEnd,dates:D.dates.slice(start),groups:reps.map(s=>D.dates.slice(start).map((d,j)=>{const r=E.assess(s,start+j);return [r.scores.rain,r.scores.heat,r.scores.dry,r.values.rain,r.values.heat,r.values.dry];}))};
fs.writeFileSync(path.join(root,'data/replay.js'),'window.STREAM_REPLAY='+JSON.stringify(replay)+';\n');
const results=A.analyze(D,replay),dir=path.join(root,'results');fs.mkdirSync(dir,{recursive:true});
fs.appendFileSync(path.join(root,'data/replay.js'),'window.STREAM_RESULTS_SUMMARY='+JSON.stringify(results.comparison)+';\n');
fs.writeFileSync(path.join(dir,'analysis.json'),JSON.stringify(results,null,2));
fs.writeFileSync(path.join(dir,'analysis_report.html'),require('../assets/reports.js').analysis(results));
const exportRows=(name,rows)=>{const keys=Object.keys(rows[0]||{});fs.writeFileSync(path.join(dir,name),Core.csv([keys,...rows.map(r=>keys.map(k=>Array.isArray(r[k])?r[k].join(';'):typeof r[k]==='object'&&r[k]!==null?JSON.stringify(r[k]):r[k]))]));};
exportRows('daily_comparison.csv',results.daily);exportRows('weather_groups.csv',results.groups);exportRows('screening_episodes.csv',results.episodes);exportRows('threshold_sensitivity.csv',results.sensitivity);exportRows('monthly_screening.csv',results.monthly);
const regional=['CO','TO','GH','BE','OS'].map(city=>{const r=A.analyze(D,replay,{city});return {...r.scope,...r.counts,flaggedPct:r.flaggedPct,naiveMeanGroups:r.comparison.naiveMeanGroups,diverseMeanGroups:r.comparison.diverseMeanGroups,meanIndexTradeoff:r.comparison.meanIndexTradeoff};});
exportRows('regional_summary.csv',regional);
console.log(JSON.stringify({counts:results.counts,flaggedPct:results.flaggedPct,comparison:results.comparison,episodes:results.episodes.length,extremes:results.extremes,regional},null,2));
