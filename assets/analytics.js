/* Auditable descriptive results over a held-out-in-time replay period.
   Counts are weather-group days, not independent trials or health outcomes. */
(function(root,factory){
  const api=factory(typeof module==='object'&&module.exports?require('./core.js'):root.StreamCore);
  if(typeof module==='object'&&module.exports)module.exports=api;else root.StreamAnalytics=api;
})(typeof window==='object'?window:globalThis,function(Core){
  'use strict';
  const metrics=['rain','heat','dry'];
  const mean=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:null;
  const percentage=(n,d)=>d?100*n/d:null;
  function unpack(record){
    const valid=record.slice(0,3).filter(v=>v!==null);
    const score=valid.length?Math.max(...valid):null;
    const driver=score===null?null:metrics[record.slice(0,3).findIndex(v=>v===score)];
    return {score,driver,complete:valid.length===3,scores:{rain:record[0],heat:record[1],dry:record[2]},values:{rain:record[3],heat:record[4],dry:record[5]}};
  }
  function expectedGroups(groupSizes,budget){
    const n=groupSizes.reduce((a,b)=>a+b,0),k=Math.min(n,budget);
    if(!Number.isInteger(budget)||budget<0)throw new RangeError('Budget must be a nonnegative integer');
    if(!n)return 0;
    return groupSizes.reduce((sum,m)=>{
      let absent=1;
      for(let i=0;i<k;i++)absent*=Math.max(0,n-m-i)/(n-i);
      return sum+1-absent;
    },0);
  }
  function analyze(data,replay,options={}){
    const city=options.city||'all',start=options.start||replay.dates[0],end=options.end||replay.dates.at(-1),threshold=options.threshold??95,budget=options.budget??5;
    if(start>end||!replay.dates.includes(start)||!replay.dates.includes(end))throw new RangeError('Invalid results period');
    if(!Number.isFinite(threshold)||threshold<0||threshold>100)throw new RangeError('Invalid screening threshold');
    if(!Number.isInteger(budget)||budget<1)throw new RangeError('Invalid visit budget');
    const sites=data.sites.filter(s=>city==='all'||s.city===city),groupIDs=[...new Set(sites.map(s=>s.group))].sort((a,b)=>a-b);
    if(!sites.length)throw new RangeError('No sites in the selected region');
    const members=new Map(groupIDs.map(g=>[g,sites.filter(s=>s.group===g)]));
    const ids=replay.dates.map((date,i)=>({date,i})).filter(x=>x.date>=start&&x.date<=end);
    const counts={calendarDays:ids.length,eligibleDays:0,groupDays:0,missingGroupDays:0,incompleteGroupDays:0,flaggedGroupDays:0,siteDays:0,flaggedSiteDays:0};
    const drivers={rain:0,heat:0,dry:0};
    const byMonth=new Map(),daily=[],episodes=[],open=new Map();
    const byGroup=new Map(groupIDs.map(g=>[g,{group:g,city:members.get(g)[0].city,cityName:members.get(g)[0].cityName,siteCodes:members.get(g).map(s=>s.code),valid:0,flagged:0,incomplete:0,missing:0}]));
    const sensitivity=[85,90,95,98,99].map(value=>({threshold:value,flagged:0}));
    const samples={naiveGroups:[],diverseGroups:[],naiveMeanIndex:[],diverseMeanIndex:[],randomExpectedGroups:[],diverseVisits:[],naiveVisits:[]};
    let reducedRedundancyDays=0;
    const extremes={rain:null,heat:null,dry:null};
    function close(g,rightCensored=false){const e=open.get(g);if(e){e.rightCensored=rightCensored;episodes.push(e);open.delete(g);}}
    for(const {date,i} of ids){
      const month=date.slice(0,7);if(!byMonth.has(month))byMonth.set(month,{month,valid:0,flagged:0,missing:0,incomplete:0});const mon=byMonth.get(month);
      const results=new Map();let flagged=0,valid=0;
      for(const g of groupIDs){
        const r=unpack(replay.groups[g][i]);results.set(g,r);const group=byGroup.get(g),n=members.get(g).length;
        if(r.score===null){counts.missingGroupDays++;group.missing++;mon.missing++;close(g,true);continue;}
        valid++;counts.groupDays++;group.valid++;mon.valid++;counts.siteDays+=n;
        if(!r.complete){counts.incompleteGroupDays++;group.incomplete++;mon.incomplete++;}
        for(const s of sensitivity)if(r.score>=s.threshold)s.flagged++;
        for(const m of metrics){const v=r.values[m];if(v!==null&&(!extremes[m]||v>extremes[m].value))extremes[m]={metric:m,value:v,date,group:g,cityName:group.cityName,siteCodes:group.siteCodes,percentile:r.scores[m]};}
        if(r.score>=threshold){
          flagged++;counts.flaggedGroupDays++;counts.flaggedSiteDays+=n;group.flagged++;mon.flagged++;drivers[r.driver]++;
          let ep=open.get(g);
          if(!ep){const prev=i>0?unpack(replay.groups[g][i-1]):null;ep={id:`${g}-${date}`,group:g,cityName:group.cityName,city:group.city,start:date,end:date,days:0,peakDate:date,peakIndex:r.score,driver:r.driver,peakValues:r.values,incompleteDays:0,siteCodes:group.siteCodes,leftCensored:!prev||prev.score===null||prev.score>=threshold};open.set(g,ep);}
          ep.end=date;ep.days++;if(!r.complete)ep.incompleteDays++;
          if(r.score>ep.peakIndex){ep.peakIndex=r.score;ep.peakDate=date;ep.driver=r.driver;ep.peakValues=r.values;}
        }else close(g,false);
      }
      const candidates=sites.map(site=>({...results.get(site.group),site}));
      const naive=Core.plan(candidates,budget,false),diverse=Core.plan(candidates,budget,true);
      let nGroups=null,dGroups=null,nMean=null,dMean=null,random=null;
      if(naive.length){
        counts.eligibleDays++;nGroups=new Set(naive.map(r=>r.site.group)).size;dGroups=new Set(diverse.map(r=>r.site.group)).size;
        nMean=mean(naive.map(r=>r.score));dMean=mean(diverse.map(r=>r.score));
        random=expectedGroups(groupIDs.filter(g=>results.get(g).score!==null).map(g=>members.get(g).length),budget);
        samples.naiveGroups.push(nGroups);samples.diverseGroups.push(dGroups);samples.naiveMeanIndex.push(nMean);samples.diverseMeanIndex.push(dMean);samples.randomExpectedGroups.push(random);samples.diverseVisits.push(diverse.length);samples.naiveVisits.push(naive.length);
        if(dGroups>nGroups)reducedRedundancyDays++;
      }
      daily.push({date,validGroups:valid,flaggedGroups:flagged,flaggedPct:percentage(flagged,valid),naiveGroups:nGroups,diverseGroups:dGroups,randomExpectedGroups:random,naiveMeanIndex:nMean,diverseMeanIndex:dMean,naiveVisits:naive.length,diverseVisits:diverse.length});
    }
    const last=ids.at(-1).i;
    for(const g of [...open.keys()]){const next=last+1<replay.dates.length?unpack(replay.groups[g][last+1]):null;close(g,!next||next.score===null||next.score>=threshold);}
    const ordered=episodes.sort((a,b)=>b.days-a.days||b.peakIndex-a.peakIndex||a.start.localeCompare(b.start)||a.group-b.group);
    const comparison={budget,validDays:counts.eligibleDays,naiveMeanGroups:mean(samples.naiveGroups),diverseMeanGroups:mean(samples.diverseGroups),randomExpectedGroups:mean(samples.randomExpectedGroups),naiveMeanIndex:mean(samples.naiveMeanIndex),diverseMeanIndex:mean(samples.diverseMeanIndex),naiveMeanVisits:mean(samples.naiveVisits),diverseMeanVisits:mean(samples.diverseVisits),reducedRedundancyDays};
    comparison.coverageGain=comparison.diverseMeanGroups===null?null:comparison.diverseMeanGroups-comparison.naiveMeanGroups;
    comparison.meanIndexTradeoff=comparison.naiveMeanIndex===null?null:comparison.naiveMeanIndex-comparison.diverseMeanIndex;
    return {scope:{city,start,end,threshold,budget,siteCount:sites.length,groupCount:groupIDs.length},counts,flaggedPct:percentage(counts.flaggedGroupDays,counts.groupDays),drivers,comparison,monthly:[...byMonth.values()].map(m=>({...m,flaggedPct:percentage(m.flagged,m.valid)})),daily,groups:[...byGroup.values()].map(g=>({...g,flaggedPct:percentage(g.flagged,g.valid)})),episodes:ordered,extremes,sensitivity:sensitivity.map(s=>({...s,valid:counts.groupDays,flaggedPct:percentage(s.flagged,counts.groupDays)}))};
  }
  return {unpack,expectedGroups,analyze};
});
