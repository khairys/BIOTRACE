import { ArrowRight, FlaskConical, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { Claim, MethodsResponse, ValidationResults } from '../api/generated';
import { useResource } from '../api/client';
import { decisionLabels, formatNumber, percent } from '../i18n/id';

// R-VAL-01 baseline shown for contrast only: "name the best hit at >= baseline_species_pct".
// The threshold comes from the active rules YAML; nothing here changes a claim.
export function useBaselinePct(){
  const methods=useResource<MethodsResponse>('/api/methods');
  return methods.data?.rules.validation.baseline_species_pct??null;
}
export function baselineName(claim:Claim,pct:number|null){
  return pct!==null&&claim.best_pct!==null&&claim.best_pct>=pct&&claim.best_match?claim.best_match:null;
}
const isSpecies=(c:Claim)=>c.reported_rank==='species'||c.reported_rank==='hybrid_alias';

export function BaselineSummary({claims,pct}:{claims:Claim[];pct:number|null}){
  if(pct===null)return null;
  const named=claims.filter(c=>baselineName(c,pct));
  const lowered=named.filter(c=>!isSpecies(c));
  const renamed=named.filter(c=>isSpecies(c)&&c.reported_name!==c.best_match);
  const flagged=named.filter(c=>isSpecies(c)&&c.reported_name===c.best_match&&c.decision!=='safe');
  const held=lowered.length+renamed.length+flagged.length;
  return <section className="card result-section baseline-card"><div className="card-heading"><div><h2><ShieldCheck size={18}/>Dibanding pencocokan BLAST ≥{pct}% saja</h2><p>Cara umum langsung memberi nama spesies pada kemiripan ≥{pct}%. BioTrace meminta bukti kamus, lokasi, dan sinyal lab terlebih dulu.</p></div></div>
    <div className="baseline-grid"><div><span>Akan langsung diberi nama spesies</span><strong>{formatNumber(named.length)}</strong><small>dari {formatNumber(claims.length)} klaim</small></div><div className="highlight"><span>Ditahan BioTrace</span><strong>{formatNumber(held)}</strong><small>{named.length?percent(held/named.length):'—'} dari klaim tersebut</small></div><div><span>Diturunkan ke kompleks/genus/tidak dikenal</span><strong>{formatNumber(lowered.length)}</strong></div><div><span>Nama spesies diganti</span><strong>{formatNumber(renamed.length)}</strong></div><div><span>Tetap spesies, tetapi tidak "Aman dilaporkan"</span><strong>{formatNumber(flagged.length)}</strong><small>{Object.entries(flagged.reduce<Record<string,number>>((acc,c)=>{acc[c.decision]=(acc[c.decision]??0)+1;return acc;},{})).map(([d,n])=>`${decisionLabels[d as Claim['decision']]} ${n}`).join(' · ')}</small></div></div>
    <p className="small muted">"Ditahan" berarti bukti belum cukup untuk nama spesies yang aman, bukan bukti bahwa nama tersebut salah.</p></section>;
}

// One-line contrast for the dashboard; the full breakdown lives in the PDF and export.
export function BaselineSentence({claims,pct}:{claims:Claim[];pct:number|null}){
  if(pct===null)return null;
  const named=claims.filter(c=>baselineName(c,pct));
  const held=named.filter(c=>!isSpecies(c)||c.reported_name!==c.best_match||c.decision!=='safe').length;
  if(!named.length)return null;
  return <p className="baseline-sentence"><ShieldCheck size={15}/>Pencocokan biasa (kemiripan ≥{pct}%) langsung memberi nama spesies pada {formatNumber(named.length)} deteksi. BioTrace menahan {formatNumber(held)} di antaranya sampai buktinya cukup.</p>;
}

export function BaselineLine({claim,pct}:{claim:Claim;pct:number|null}){
  if(pct===null)return null;
  const name=baselineName(claim,pct);
  const same=name&&isSpecies(claim)&&claim.reported_name===name&&claim.decision==='safe';
  return <div className={`baseline-line ${same?'same':''}`}><span>BLAST ≥{pct}% saja</span><ArrowRight size={12}/>{name?<><i>{name}</i><small>{same?'sama dengan BioTrace':'langsung dilaporkan sebagai spesies'}</small></>:<small>tidak memberi nama spesies</small>}</div>;
}

export function LosoEvidence({referenceVersion,rulesVersion}:{referenceVersion?:string;rulesVersion?:string}){
  const results=useResource<ValidationResults>('/api/validation/latest');
  const real=results.data?.results.filter(r=>!r.is_simulated&&!r.partial&&r.metrics.M3!=null&&r.baseline_blast97.M3!=null)??[];
  if(!real.length)return null;
  const r=real.find(r=>r.reference_version===referenceVersion&&r.rules_version===rulesVersion)??real[real.length-1];
  return <section className="card loso-evidence" aria-label="Bukti uji mesin"><div><span className="eyebrow"><FlaskConical size={14}/>UJI PUSTAKA INTERNAL · DATA NYATA</span><h2>Nama keliru pada tingkat apa pun</h2><p className="small muted">M3 · {formatNumber(r.n_queries)} query, {formatNumber(r.n_species)} spesies · {r.reference_version} · {r.marker}. Semua referensi spesies asli dihapus sebelum pencocokan.</p></div><div className="loso-bars"><div><span>BioTrace {r.rules_version}</span><b style={{width:`${Math.min(100,Math.max(2,(r.metrics.M3??0)/Math.max(r.baseline_blast97.M3??0,0.0001)*100))}%`}} className="ours"/><strong>{percent(r.metrics.M3)}</strong></div><div><span>BLAST ≥97% saja</span><b style={{width:'100%'}}/><strong>{percent(r.baseline_blast97.M3)}</strong></div></div><p className="small muted">Uji pustaka, belum validasi lapangan atau ahli. M1 nol pada pustaka tanpa spesimen Indonesia dapat berasal dari pembatasan R-DEC-09. <Link className="text-button" to="/validation">Rincian validasi</Link></p></section>;
}
