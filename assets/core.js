/* Deterministic, retrospective weather screening. No forecasts or disease model. */
(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.StreamCore = api;
})(typeof window === 'object' ? window : globalThis, function() {
  'use strict';
  const METRICS = ['rain', 'heat', 'dry'];
  const finite = v => typeof v === 'number' && Number.isFinite(v);
  function dayOfYear(iso) {
    const [m,d] = iso.slice(5).split('-').map(Number);
    return Math.round((Date.UTC(2000,m-1,d)-Date.UTC(2000,0,1))/86400000);
  }
  function seasonalDistance(a,b) { const d=Math.abs(a-b); return Math.min(d,366-d); }
  function percentile(value, sample) {
    const valid=sample.filter(finite);
    if (!finite(value) || !valid.length) return null;
    // Midrank ties: identical observations do not all become extreme anomalies.
    const below=valid.filter(x=>x<value).length, equal=valid.filter(x=>x===value).length;
    return 100*(below+0.5*equal)/valid.length;
  }
  function derive(rows) {
    let run=null;
    return rows.map((r,i)=>{
      const rain=r[4];
      run = !finite(rain) ? null : rain<1 ? (run===null ? null : run+1) : 0;
      const three=rows.slice(Math.max(0,i-2),i+1).map(x=>x[4]);
      return {rain:three.length===3 && three.every(finite) ? Math.round(three.reduce((a,b)=>a+b,0)*100)/100 : null,
        heat:finite(r[2])?r[2]:null,dry:run};
    });
  }
  function engine(data) {
    const derived=data.series.map(derive), days=data.dates.map(dayOfYear), cache=new Map();
    const baseline=data.dates.map((date,i)=>({date,i})).filter(x=>x.date>=data.meta.baselineStart && x.date<=data.meta.baselineEnd).map(x=>x.i);
    function sample(group,index,metric) {
      const key=`${group}:${days[index]}:${metric}`;
      if (!cache.has(key)) cache.set(key,baseline.filter(i=>seasonalDistance(days[i],days[index])<=30).map(i=>derived[group][i][metric]).filter(finite));
      return cache.get(key);
    }
    function assess(site,index,thresholds={watch:85,high:95}) {
      if (!Number.isInteger(index) || index<0 || index>=data.dates.length) throw new RangeError('Invalid replay date');
      if (data.dates[index]<data.meta.replayStart) throw new RangeError('Replay must be later than calibration period');
      const values=derived[site.group][index], scores={},counts={};
      for(const metric of METRICS) {const s=sample(site.group,index,metric);counts[metric]=s.length;scores[metric]=percentile(values[metric],s);}
      const valid=METRICS.filter(m=>finite(scores[m]));
      const score=valid.length ? Math.max(...valid.map(m=>scores[m])) : null;
      const driver=valid.slice().sort((a,b)=>scores[b]-scores[a] || METRICS.indexOf(a)-METRICS.indexOf(b))[0] || null;
      const level=score===null?'unknown':score>=thresholds.high?'high':score>=thresholds.watch?'watch':'routine';
      return {site,index,date:data.dates[index],values,scores,counts,score,driver,level,complete:valid.length===3};
    }
    return {assess,derived,sample};
  }
  function rank(rows) {return [...rows].sort((a,b)=>(b.score??-1)-(a.score??-1) || a.site.code.localeCompare(b.site.code,undefined,{numeric:true}));}
  function plan(rows,budget,diversify=true) {
    const sorted=rank(rows).filter(r=>r.score!==null),seen=new Set(),selected=[];
    for(const r of sorted) {
      if(selected.length>=budget) break;
      if(diversify && seen.has(r.site.group)) continue;
      seen.add(r.site.group);selected.push(r);
    }
    return selected;
  }
  function csv(rows) {
    const escape=value=>{
      let s=value===null||value===undefined?'':String(value);
      if (/^[=+@\t\r]/.test(s) || (/^-/.test(s) && !/^-\d+(\.\d+)?$/.test(s))) s="'"+s;
      return /[",\n\r]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;
    };
    return '\uFEFF'+rows.map(r=>r.map(escape).join(',')).join('\r\n');
  }
  return {METRICS,dayOfYear,seasonalDistance,percentile,derive,engine,rank,plan,csv};
});
