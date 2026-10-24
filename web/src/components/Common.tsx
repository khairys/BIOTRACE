import { AlertTriangle, CheckCircle2, CircleHelp, Info, LoaderCircle, ShieldCheck, XCircle } from 'lucide-react';
import type { Claim } from '../api/generated';
import { decisionLabels, limitNotice } from '../i18n/id';

export function DecisionBadge({decision}:{decision:Claim['decision']}){
  const Icon=decision==='safe'?CheckCircle2:decision==='with_note'?Info:decision==='must_verify'?AlertTriangle:XCircle;
  return <span className={`decision-badge ${decision}`}><Icon size={13}/>{decisionLabels[decision]}</span>;
}
export function GradeBadge({grade}:{grade:Claim['grade']}){return <span className={`grade grade-${grade}`}>{grade}</span>;}
export function SimulationBanner(){return <div className="simulation-banner" role="note"><AlertTriangle size={16}/><strong>SIMULASI</strong><span>Data dibuat tim untuk demo. Nama, sekuens, voucher, dan status bersifat fiktif.</span></div>;}
export function LimitNotice(){return <div className="limit-notice"><ShieldCheck size={17}/><span>{limitNotice} Laporan ini merupakan verifikasi pendukung, bukan dokumen AMDAL resmi.</span></div>;}
export function Loading(){return <div className="loading" role="status"><LoaderCircle className="spinner" size={22}/>Memuat data…</div>;}
export function ErrorNotice({message}:{message:string}){return <div className="error-notice" role="alert"><AlertTriangle size={18}/><span>{message}</span></div>;}
export function EmptyState({message}:{message:string}){return <div className="empty-state"><CircleHelp size={28}/><p>{message}</p></div>;}
