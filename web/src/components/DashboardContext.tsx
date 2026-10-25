import { useMemo } from 'react';
import type { RunResult } from '../api/generated';
import { causeNames, formatNumber } from '../i18n/id';

/** F23/F25 [MVP]: presentation aggregates from this run, never from a different reference. */
export default function DashboardContext({run}:{run:RunResult}){
  const counts=useMemo(()=>Object.keys(causeNames).map(cause=>({cause,count:run.claims.filter(c=>c.causes.includes(cause)).length})),[run.claims]);
  const max=Math.max(1,...counts.map(c=>c.count));
  return <div className="two-column result-section dashboard-context">
    <section className="card"><div className="card-heading"><div><h2>Penyebab ketidakpastian</h2><p>Jumlah klaim per penyebab; satu klaim bisa memiliki beberapa penyebab.</p></div></div>
      <div className="uncertainty-bars">{counts.map(({cause,count})=><div key={cause}><div><strong>{causeNames[cause]}</strong><span>{formatNumber(count)} klaim</span></div><div className="uncertainty-track"><b className={cause} style={{width:`${count/max*100}%`}}/></div></div>)}</div>
      <p className="small muted">{formatNumber(run.claims.filter(c=>c.reported_rank==='unknown').length)} klaim tidak dikenal · {formatNumber(new Set(run.claims.map(c=>c.asv_id)).size)} ASV memiliki klaim pada run ini.</p>
    </section>
    <section className="card"><div className="card-heading"><div><h2>Data masuk dan jejak audit</h2><p>Berkas tersimpan yang membentuk hasil ini; SHA-256 lengkap tersedia di jejak audit.</p></div></div>
      <ul className="input-audit-list">{Object.entries(run.manifest.input_hashes).map(([file,hash])=><li key={file}><span>{file}</span><code title={hash}>{hash.slice(0,8)}…{hash.slice(-6)}</code></li>)}</ul>
      <div className="audit-versions"><span>Kamus <strong>{run.manifest.reference_version}</strong></span><span>Aturan <strong>{run.manifest.rules_version}</strong></span><span>Engine <strong>{run.manifest.engine_version}</strong></span></div>
      <details className="dashboard-warnings"><summary>{run.summary.warnings.length} peringatan proses · Lihat rincian</summary>{run.summary.warnings.length?<ul>{run.summary.warnings.map((w,i)=><li key={i}>{w}</li>)}</ul>:<p>Tidak ada peringatan proses tercatat.</p>}</details>
      <p className="small muted">Ambang usulan tim, belum dikalibrasi ahli. Hash mengidentifikasi berkas; bukan tanda validasi ilmiah.</p>
    </section>
  </div>;
}

export function downloadPriorities(run:RunResult){
  const columns=['type','name_or_asv','waterbody_id','score','reasons','sites','total_reads','nearest_hint','is_simulated'] as const;
  const cell=(value:unknown)=>{let text=Array.isArray(value)?value.join(';'):String(value??'');if(/^[=+@-]/.test(text))text=`'${text}`;return `"${text.replaceAll('"','""')}"`;};
  const csv=[columns.join(','),...run.barcode_priority.map(row=>columns.map(key=>cell(row[key])).join(','))].join('\r\n');
  const url=URL.createObjectURL(new Blob(['\uFEFF',csv],{type:'text/csv;charset=utf-8'}));
  const link=document.createElement('a');link.href=url;link.download=`prioritas_barcode_${run.run_id}${run.summary.is_simulated?'_SIMULASI':''}.csv`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
