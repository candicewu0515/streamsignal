const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const C=require('../assets/core.js');
const box={window:{}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../data/snapshot.js'),'utf8'),box);
const D=JSON.parse(JSON.stringify(box.window.STREAM_DATA));
const E=C.engine(D);
const row=(rain,heat=25)=>[20,15,heat,70,rain,2,4,1010,50,10];

test('percentile uses midrank ties, preserves missing values and bounds',()=>{
  assert.equal(C.percentile(0,[0,0,0,0]),50);
  assert.equal(C.percentile(2,[0,1,2,3]),62.5);
  assert.equal(C.percentile(5,[0,1,2,3]),100);
  assert.equal(C.percentile(-1,[0,1,2,3]),0);
  assert.equal(C.percentile(null,[0,1]),null);
  assert.equal(C.percentile(1,[]),null);
});
test('year-end and leap-day season windows use a circular calendar',()=>{
  assert.equal(C.seasonalDistance(C.dayOfYear('2023-12-31'),C.dayOfYear('2025-01-01')),1);
  assert.equal(C.dayOfYear('2024-03-01'),C.dayOfYear('2023-03-01'));
  assert.equal(C.seasonalDistance(C.dayOfYear('2024-02-29'),C.dayOfYear('2025-03-01')),1);
});
test('rolling rainfall needs three known calendar days; missing rain is never zero',()=>{
  const x=C.derive([row(1),row(2),row(3),row(null),row(4),row(5),row(6)]);
  assert.deepEqual(x.map(r=>r.rain),[null,null,6,null,null,null,15]);
});
test('dry spells stay unknown after a gap until a wet day, including left-censoring',()=>{
  const x=C.derive([row(0),row(0),row(1),row(.2),row(0),row(null),row(0),row(2),row(0)]);
  assert.deepEqual(x.map(r=>r.dry),[null,null,0,1,2,null,null,0,1]);
});
test('snapshot preserves 106 sites, 21 exact series, 143948 observations and two missing days',()=>{
  assert.equal(D.sites.length,106);assert.equal(D.series.length,21);
  const nonMissing=D.sites.reduce((n,s)=>n+D.series[s.group].filter(r=>r.some(x=>x!==null)).length,0);
  assert.equal(nonMissing,143948);
  assert.deepEqual(D.meta.missingDates,['2026-08-04','2026-08-27']);
  for(const day of D.meta.missingDates){const i=D.dates.indexOf(day);for(const s of D.sites){const r=E.assess(s,i);assert.equal(r.score,null);assert.equal(r.level,'unknown');assert.equal(r.complete,false);}}
});
test('no score is produced in the baseline period or outside the snapshot',()=>{
  assert.throws(()=>E.assess(D.sites[0],0),RangeError);
  assert.throws(()=>E.assess(D.sites[0],-1),RangeError);
  assert.throws(()=>E.assess(D.sites[0],D.dates.length),RangeError);
});
test('reference samples exclude all replay-period and future observations',()=>{
  const clone=JSON.parse(JSON.stringify(D));
  const g=D.sites[0].group,day=D.dates.indexOf('2025-06-15');
  for(let i=day+1;i<clone.dates.length;i++)clone.series[g][i]=row(90000,90000);
  const future=C.engine(clone);
  assert.deepEqual(future.sample(g,day,'rain'),E.sample(g,day,'rain'));
  assert.deepEqual(future.assess(clone.sites[0],day).scores,E.assess(D.sites[0],day).scores);
  const expected=D.dates.map((d,i)=>({d,i})).filter(x=>x.d>='2023-01-01'&&x.d<='2024-12-31'&&C.seasonalDistance(C.dayOfYear(x.d),C.dayOfYear(D.dates[day]))<=30).map(x=>E.derived[g][x.i].heat).filter(x=>x!==null);
  assert.deepEqual(E.sample(g,day,'heat'),expected);
});
test('scoring thresholds classify raw percentiles, and group duplicates agree',()=>{
  const i=D.dates.length-1,byGroup=new Map();
  for(const s of D.sites){const r=E.assess(s,i);assert.ok(r.score>=0&&r.score<=100);assert.equal(r.score,Math.max(...Object.values(r.scores).filter(v=>v!==null)));assert.equal(r.level,r.score>=95?'high':r.score>=85?'watch':'routine');if(byGroup.has(s.group))assert.deepEqual(r.scores,byGroup.get(s.group));else byGroup.set(s.group,r.scores);}
});
test('field plans respect budgets, exclude missing scores and avoid repeated groups',()=>{
  const rr=D.sites.map(s=>E.assess(s,D.dates.length-1));
  const picked=C.plan(rr,5,true);assert.equal(picked.length,5);assert.equal(new Set(picked.map(r=>r.site.group)).size,5);
  assert.equal(C.plan(rr,100,true).length,21);
  assert.equal(C.plan(rr,5,false).length,5);
  assert.equal(C.plan(rr,0,true).length,0);
  assert.equal(C.plan(rr.map(r=>({...r,score:null})),5,true).length,0);
});
test('CSV escapes names, newlines, formulas and preserves numeric negatives',()=>{
  const x=C.csv([['a,b','"quoted"','a\nb','=1+1','-2.5','@name',null]]);
  assert.equal(x,'\uFEFF"a,b","""quoted""","a\nb",\'=1+1,-2.5,\'@name,');
});
