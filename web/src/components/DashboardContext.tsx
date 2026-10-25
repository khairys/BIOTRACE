import { useMemo } from 'react';
import type { RunResult } from '../api/generated';
import { causeNames, formatNumber } from '../i18n/id';

/** F23/F25 [MVP]: why claims are uncertain, counted from this run only. */
export default function CauseSummary({run}:{run:RunResult}){
  const counts=useMemo(()=>Object.keys(causeNames).map(cause=>({cause,count:run.claims.filter(c=>c.causes.includes(cause)).length})),[run.claims]);
  const max=Math.max(1,...counts.map(c=>c.count));
  return <section className="card dashboard-context"><div className="card-heading"><div><h2>Alasan keraguan</h2><p>Satu klaim bisa punya lebih dari satu alasan.</p></div></div>
    <div className="uncertainty-bars">{counts.map(({cause,count})=><div key={cause}><div><strong>{causeNames[cause]}</strong><span>{formatNumber(count)} klaim</span></div><div className="uncertainty-track"><b className={cause} style={{width:`${count/max*100}%`}}/></div></div>)}</div>
  </section>;
}

export function downloadPriorities(run:RunResult){
  const columns=['type','name_or_asv','waterbody_id','score','reasons','sites','total_reads','nearest_hint','is_simulated'] as const;
  const cell=(value:unknown)=>{let text=Array.isArray(value)?value.join(';'):String(value??'');if(/^[=+@-]/.test(text))text=`'${text}`;return `"${text.replaceAll('"','""')}"`;};
  const csv=[columns.join(','),...run.barcode_priority.map(row=>columns.map(key=>cell(row[key])).join(','))].join('\r\n');
  const url=URL.createObjectURL(new Blob(['﻿',csv],{type:'text/csv;charset=utf-8'}));
  const link=document.createElement('a');link.href=url;link.download=`prioritas_barcode_${run.run_id}${run.summary.is_simulated?'_SIMULASI':''}.csv`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
