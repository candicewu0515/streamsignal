const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const A=require('../assets/analytics.js'),Core=require('../assets/core.js'),Reports=require('../assets/reports.js');
const ctx={window:{}};for(const file of ['snapshot.js','replay.js'])vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../data',file),'utf8'),ctx);
const D=ctx.window.STREAM_DATA,R=ctx.window.STREAM_REPLAY;
const record=(score,heat=1,dry=1)=>[score,heat,dry,score===null?null:12,heat===null?null:25,dry===null?null:2];
const toyData={sites:[{code:'S1',city:'A',cityName:'Alpha',group:0},{code:'S2',city:'A',cityName:'Alpha',group:0},{code:'S3',city:'A',cityName:'Alpha',group:1}]};
const dates=['2025-01-01','2025-01-02','2025-01-03','2025-01-04','2025-01-05'];
const toyReplay={dates,groups:[[record(96),record(97),record(null,null,null),record(96),record(20)],[record(10),record(30),record(null,null,null),record(96),record(20)]]};

test('expected random coverage agrees with enumerated small populations',()=>{
  assert.equal(A.expectedGroups([3,1],2),1.5);
  assert.ok(Math.abs(A.expectedGroups([2,2],2)-10/6)<1e-12);
  assert.equal(A.expectedGroups([2,2],20),2);
  assert.equal(A.expectedGroups([2,2],0),0);
  assert.throws(()=>A.expectedGroups([2,2],-1),RangeError);
});
test('partial and absent records have distinct denominators',()=>{
  const r=A.analyze(toyData,toyReplay,{budget:2});
  assert.equal(r.counts.calendarDays,5);assert.equal(r.counts.eligibleDays,4);
  assert.equal(r.counts.groupDays,8);assert.equal(r.counts.missingGroupDays,2);
  assert.equal(r.counts.flaggedGroupDays,4);assert.equal(r.flaggedPct,50);
  const clone=JSON.parse(JSON.stringify(toyReplay));clone.groups[0][0][2]=null;
  const incomplete=A.analyze(toyData,clone,{budget:2});
  assert.equal(incomplete.counts.groupDays,8);assert.equal(incomplete.counts.incompleteGroupDays,1);
});
test('episode segmentation respects missing days, threshold breaks and window censoring',()=>{
  const r=A.analyze(toyData,toyReplay,{budget:2});
  const group=r.episodes.filter(e=>e.group===0).sort((a,b)=>a.start.localeCompare(b.start));
  assert.equal(group.length,2);assert.equal(group[0].days,2);assert.equal(group[0].end,'2025-01-02');
  assert.equal(group[0].leftCensored,true);assert.equal(group[0].rightCensored,true);
  assert.equal(group[1].start,'2025-01-04');assert.equal(group[1].leftCensored,true);assert.equal(group[1].rightCensored,false);
  const clipped=A.analyze(toyData,toyReplay,{budget:2,start:'2025-01-02',end:'2025-01-02'});
  assert.equal(clipped.episodes[0].days,1);assert.equal(clipped.episodes[0].leftCensored,true);assert.equal(clipped.episodes[0].rightCensored,true);
});
test('sensitivity percentages are monotone and use the valid group-day denominator',()=>{
  const r=A.analyze(toyData,toyReplay,{budget:2});
  assert.ok(r.sensitivity.every(s=>s.valid===8));
  for(let i=1;i<r.sensitivity.length;i++)assert.ok(r.sensitivity[i].flagged<=r.sensitivity[i-1].flagged);
});
test('a smaller available group pool leaves visits unfilled and reports actual means',()=>{
  const r=A.analyze(toyData,toyReplay,{budget:3});
  assert.equal(r.comparison.naiveMeanVisits,3);assert.equal(r.comparison.diverseMeanVisits,2);
  assert.equal(r.comparison.diverseMeanGroups,2);assert.equal(r.comparison.validDays,4);
});
test('an all-missing window is unscored, not zero risk or zero average performance',()=>{
  const r=A.analyze(toyData,toyReplay,{start:'2025-01-03',end:'2025-01-03',budget:2});
  assert.equal(r.flaggedPct,null);assert.equal(r.comparison.naiveMeanGroups,null);assert.equal(r.comparison.meanIndexTradeoff,null);
  assert.equal(r.episodes.length,0);assert.equal(r.extremes.heat,null);
  assert.equal(r.daily[0].validGroups,0);assert.equal(r.daily[0].flaggedPct,null);
});
test('scope validation rejects invalid dates, empty regions and negative budgets',()=>{
  assert.throws(()=>A.analyze(toyData,toyReplay,{start:'2026-01-01'}),RangeError);
  assert.throws(()=>A.analyze(toyData,toyReplay,{city:'NOPE'}),RangeError);
  assert.throws(()=>A.analyze(toyData,toyReplay,{budget:0}),RangeError);
  assert.throws(()=>A.analyze(toyData,toyReplay,{threshold:101}),RangeError);
});
test('materialized replay values match fresh core calculations at boundary and sample dates',()=>{
  const e=Core.engine(D),indices=[0,36,164,365,580,581,R.dates.length-1];
  for(const g of [0,3,10,17,20])for(const i of indices){const s=D.sites.find(s=>s.group===g),j=D.dates.indexOf(R.dates[i]),r=e.assess(s,j),a=A.unpack(R.groups[g][i]);assert.deepEqual(a.scores,r.scores);assert.deepEqual(a.values,r.values);assert.equal(a.score,r.score);}
});
test('full replay counts reconcile to source dates without duplicating weather groups',()=>{
  const r=A.analyze(D,R);
  assert.equal(r.counts.calendarDays,629);assert.equal(r.counts.eligibleDays,627);
  assert.equal(r.counts.groupDays,21*627);assert.equal(r.counts.missingGroupDays,21*2);
  assert.equal(r.counts.siteDays,106*627);
  assert.equal(r.groups.reduce((n,g)=>n+g.flagged,0),r.counts.flaggedGroupDays);
  assert.equal(r.monthly.reduce((n,m)=>n+m.flagged,0),r.counts.flaggedGroupDays);
  assert.equal(r.episodes.reduce((n,e)=>n+e.days,0),r.counts.flaggedGroupDays);
  assert.equal(r.comparison.diverseMeanGroups,5);
  assert.ok(r.comparison.naiveMeanGroups>=1&&r.comparison.naiveMeanGroups<=5);
});
test('HTML report escapes analyst annotations and source names',()=>{
  const site={code:'X',name:'<img src=x onerror=alert(1)>',cityName:'A&B',lat:40,lon:1,group:0,health:[]};
  const row={site,score:98,level:'high',values:{rain:12,heat:30,dry:2},scores:{rain:98,heat:80,dry:30},complete:true};
  const html=Reports.field([row],'2025-01-01',{'2025-01-01:X':{note:'<script>alert(1)</script>',status:'Reviewed'}},{baselineStart:'2023-01-01',baselineEnd:'2024-12-31'});
  assert.ok(!html.includes('<script>alert(1)</script>'));assert.ok(html.includes('&lt;script&gt;'));assert.ok(!html.includes('<img src=x'));assert.ok(html.includes('A&amp;B'));
});
