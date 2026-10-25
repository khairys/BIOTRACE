import { useEffect, useRef, useState } from 'react';
import { ArrowDown, BadgeCheck, Check, ClipboardList, Info, MessageSquarePlus, X } from 'lucide-react';
import type { Claim, ReviewNote } from '../api/generated';
import { ApiError, request, useResource } from '../api/client';
import { causeNames, formatNumber, labelNames, rankLabels } from '../i18n/id';
import { DecisionBadge, GradeBadge } from './Common';

// Score-formula lines (L1 = …) and the limit sentence are shown elsewhere; keep the plain reasons.
const plainReasons=(claim:Claim)=>claim.reasons_id.filter(r=>!/^L\d\s*=/.test(r)&&r!==claim.interpretation_limit&&!r.startsWith('Dinilai dengan database lab'));

export default function EvidenceCard({claim,runId,onClose,inline=false,onExpand}:{claim:Claim;runId:string;onClose:()=>void;inline?:boolean;onExpand?:()=>void}){
  const dialog=useRef<HTMLDialogElement>(null);
  useEffect(()=>{if(inline)return;const element=dialog.current;element?.showModal();return()=>element?.close();},[inline]);
  const reasons=plainReasons(claim);
  const card=<article className="evidence-card"><div className="evidence-header"><span><ClipboardList size={16}/>Bukti</span>{inline?<button className="text-button" onClick={onExpand}>Buka kartu penuh</button>:<button className="icon-button" aria-label="Tutup Evidence Card" onClick={onClose}><X size={20}/></button>}</div><div className="evidence-body">
    <div className="eyebrow">{claim.site_id}</div><h2 id={inline?'evidence-inline-title':'evidence-title'}><i>{claim.reported_name}</i></h2><span className="rank-label">{rankLabels[claim.reported_rank]}</span>
    {claim.taxon_lab?<div className="lab-name"><span>Dari lab</span><ArrowDown size={12}/><i className={claim.taxon_lab!==claim.reported_name?'changed-name':''}>{claim.taxon_lab}</i></div>:null}
    <div className="evidence-badges"><GradeBadge grade={claim.grade}/><DecisionBadge decision={claim.decision}/></div><div className="label-list">{claim.labels.map(label=><span className="taxon-label" key={label}>{labelNames[label]??label}</span>)}{claim.is_simulated?<span className="simulation-tag">SIMULASI</span>:null}</div>
    <section className={`follow-up ${claim.decision}`}><h3>Tindak lanjut</h3><p>{claim.follow_up}</p></section>
    <section><h3>Kenapa?</h3><div className="cause-list">{claim.causes.length?claim.causes.map(c=><span key={c}><Info size={13}/>{causeNames[c]??c}</span>):<span><Check size={13}/>Bukti kuat di semua sisi.</span>}</div>{reasons.length?<ul className="reasons-list">{reasons.map((reason,i)=><li key={i}>{reason}</li>)}</ul>:null}</section>
    <section><h3>Bukti</h3><div className="score-grid">{[['Kecocokan dengan kamus',claim.l1,2],['Tercatat di perairan ini',claim.l2,1],['Konsistensi antar sampel',claim.l4,2]].map(([label,value,max])=><div key={String(label)}><span>{label}<strong>{value}/{max}</strong></span><div className="score-track"><b style={{width:`${Number(value)/Number(max)*100}%`}}/></div></div>)}</div><dl className="evidence-facts"><div><dt>Terdeteksi di sampel</dt><dd>{claim.n_pos} dari {claim.n_rep}</dd></div><div><dt>Jumlah bacaan DNA</dt><dd>{formatNumber(claim.total_reads)}</dd></div></dl></section>
    <details className="review-details"><summary>Catatan ahli</summary><ReviewNotes runId={runId} claimId={claim.claim_id}/></details>
    <p className="evidence-limit"><Info size={15}/>{claim.interpretation_limit}</p>
  </div></article>;
  return inline?<aside className="evidence-inline card" aria-labelledby="evidence-inline-title">{card}</aside>:<dialog ref={dialog} className="evidence-dialog" onCancel={onClose} onClick={event=>{if(event.target===event.currentTarget)onClose();}} aria-labelledby="evidence-title">{card}</dialog>;
}

function ReviewNotes({runId,claimId}:{runId:string;claimId:string}){
  const loaded=useResource<ReviewNote[]>(`/api/runs/${runId}/notes`);
  const [added,setAdded]=useState<ReviewNote[]>([]);
  const [reviewer,setReviewer]=useState('');
  const [note,setNote]=useState('');
  const [verified,setVerified]=useState(false);
  const [error,setError]=useState('');
  const [busy,setBusy]=useState(false);
  const notes=[...(loaded.data??[]),...added].filter(n=>n.claim_id===claimId);
  const isVerified=notes.some(n=>n.verified);
  const submit=async(event:React.FormEvent)=>{event.preventDefault();setBusy(true);setError('');try{const saved=await request<ReviewNote>(`/api/runs/${runId}/claims/${encodeURIComponent(claimId)}/notes`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({reviewer,note,verified})});setAdded(old=>[...old,saved]);setNote('');setVerified(false);}catch(e){setError(e instanceof ApiError?e.message:'Catatan gagal disimpan.');}finally{setBusy(false);}};
  return <section>{isVerified?<p><span className="verified-tag"><BadgeCheck size={12}/>Sudah diverifikasi ahli</span></p>:null}
    {notes.length?<ul className="note-list">{notes.map((n,i)=><li key={i}><div><strong>{n.reviewer}</strong><small>{n.created_at.slice(0,16).replace('T',' ')} UTC</small>{n.verified?<span className="verified-tag"><BadgeCheck size={11}/>Diverifikasi</span>:null}</div><p>{n.note}</p></li>)}</ul>:null}
    <form className="note-form" onSubmit={e=>void submit(e)}><input className="text-input" aria-label="Nama peninjau" placeholder="Nama peninjau" value={reviewer} onChange={e=>setReviewer(e.target.value)} maxLength={120}/><textarea className="text-input" aria-label="Catatan" placeholder="Catatan tinjauan…" value={note} onChange={e=>setNote(e.target.value)} maxLength={4000} rows={3}/><label className="check-row"><input type="checkbox" checked={verified} onChange={e=>setVerified(e.target.checked)}/>Tandai sudah diverifikasi</label>{error?<p className="small error-text">{error}</p>:null}<button className="button secondary" disabled={busy||!reviewer.trim()||!note.trim()}><MessageSquarePlus size={15}/>Simpan catatan</button></form>
    <p className="small muted">Catatan tidak mengubah keputusan.</p></section>;
}
