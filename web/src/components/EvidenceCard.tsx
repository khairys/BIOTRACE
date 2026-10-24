import { useEffect, useRef, useState } from 'react';
import { ArrowDown, Check, ClipboardList, Info, X } from 'lucide-react';
import type { Claim } from '../api/generated';
import { causeNames, formatNumber, labelNames, percent, rankLabels, warningNames } from '../i18n/id';
import { DecisionBadge, GradeBadge } from './Common';

export default function EvidenceCard({claim,onClose}:{claim:Claim;onClose:()=>void}){
  const dialog=useRef<HTMLDialogElement>(null);
  const [language,setLanguage]=useState<'id'|'en'>('id');
  useEffect(()=>{const element=dialog.current;element?.showModal();return()=>element?.close();},[]);
  return <dialog ref={dialog} className="evidence-dialog" onCancel={onClose} onClick={event=>{if(event.target===event.currentTarget)onClose();}} aria-labelledby="evidence-title"><article className="evidence-card"><div className="evidence-header"><span><ClipboardList size={16}/>BUKTI PER KLAIM</span><button className="icon-button" aria-label="Tutup Evidence Card" onClick={onClose}><X size={20}/></button></div><div className="evidence-body">
    <div className="eyebrow">{claim.site_id} <span>·</span> {claim.asv_id}</div><h2 id="evidence-title"><i>{claim.reported_name}</i></h2><span className="rank-label">{rankLabels[claim.reported_rank]}</span>
    {claim.taxon_lab?<div className="lab-name"><span>Dari lab</span><ArrowDown size={12}/><i className={claim.taxon_lab!==claim.reported_name?'changed-name':''}>{claim.taxon_lab}</i></div>:null}
    <div className="evidence-badges"><GradeBadge grade={claim.grade}/><DecisionBadge decision={claim.decision}/></div><div className="label-list">{claim.labels.map(label=><span className="taxon-label" key={label}>{labelNames[label]??label}</span>)}{claim.is_simulated?<span className="simulation-tag">SIMULASI</span>:null}</div>
    <section><h3>Kenapa keputusan ini?</h3><div className="cause-list">{claim.causes.length?claim.causes.map(c=><span key={c}><Info size={13}/>{causeNames[c]??c}</span>):<span><Check size={13}/>Tidak ada penyebab ketidakpastian yang terpicu.</span>}</div><div className="language-tabs" role="group" aria-label="Bahasa alasan"><button className={language==='id'?'selected':''} onClick={()=>setLanguage('id')}>Indonesia</button><button className={language==='en'?'selected':''} onClick={()=>setLanguage('en')}>English</button></div><ul className="reasons-list">{(language==='id'?claim.reasons_id:claim.reasons_en).map((reason,i)=><li key={i}>{reason}</li>)}</ul></section>
    <section><h3>Bukti pendukung</h3><div className="score-grid">{[['L1','Kamus',claim.l1,2],['L2','Lokasi',claim.l2,1],['L4','Sinyal lab',claim.l4,2]].map(([key,label,value,max])=><div key={String(key)}><span>{key} <small>{label}</small><strong>{value}/{max}</strong></span><div className="score-track"><b style={{width:`${Number(value)/Number(max)*100}%`}}/></div></div>)}</div><dl className="evidence-facts"><div><dt>Replikat positif</dt><dd>{claim.n_pos} / {claim.n_rep}</dd></div><div><dt>Total bacaan</dt><dd>{formatNumber(claim.total_reads)}</dd></div><div><dt>Fraksi celah kamus</dt><dd>{percent(claim.p_missing)}</dd></div><div><dt>Voucher pendukung</dt><dd>{claim.voucher_support??'Tidak tersedia'}{claim.is_simulated?' (SIMULASI)':''}</dd></div><div><dt>Kontrol negatif terkait</dt><dd>{claim.in_negative_control?'DNA terdeteksi':'DNA tidak terdeteksi'}</dd></div></dl>
    {claim.assessed_with_lab_database?<p className="muted">Dinilai dengan database lab.</p>:null}
    {claim.candidates.length?<table className="candidate-table"><thead><tr><th>Kandidat</th><th>Kemiripan</th></tr></thead><tbody>{claim.candidates.map((candidate,i)=><tr key={i}><td><i>{candidate.species}</i></td><td>{candidate.pct.toLocaleString('id-ID',{maximumFractionDigits:2})}%</td></tr>)}</tbody></table>:<p className="muted">Tidak ada kandidat yang memenuhi ambang penamaan.</p>}
    {claim.supporting_seq_ids.length?<p className="mono small">ID referensi: {claim.supporting_seq_ids.join(', ')}</p>:null}{claim.supporting_accessions.length?<p className="mono small">Aksesi: {claim.supporting_accessions.join(', ')}</p>:null}</section>
    <section><h3>Asal-usul (kemungkinan)</h3><p>{claim.origin_status}</p><p>{claim.origin_pathway}</p><p>{claim.origin_other_sources}</p></section>
    <section className={`follow-up ${claim.decision}`}><h3>Tindak lanjut</h3><p>{claim.follow_up}</p></section>
    {claim.warnings.length?<ul className="small muted">{claim.warnings.map(w=><li key={w}>{warningNames[w]??w}</li>)}</ul>:null}
    <p className="evidence-limit"><Info size={15}/>{claim.interpretation_limit}</p><p className="mono small muted">Aturan: {claim.rule_ids.join(', ')}</p>
  </div></article></dialog>;
}
