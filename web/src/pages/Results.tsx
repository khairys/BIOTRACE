import { lazy, Suspense, useDeferredValue, useMemo, useState } from 'react';
import { ArrowDownToLine, ArrowUpRight, Check, ChevronDown, Copy, FileCheck2, Fingerprint, Info, MapPin, Search } from 'lucide-react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import type { Claim, DataProvenance, RunResult, SitePoint } from '../api/generated';
import { useResource } from '../api/client';
import { causeNames, decisionLabels, decisions, formatNumber, labelNames } from '../i18n/id';
import ClaimsTable from '../components/ClaimsTable';
import EvidenceCard from '../components/EvidenceCard';
import CauseSummary, { downloadPriorities } from '../components/DashboardContext';
import { BaselineSentence, useBaselinePct } from '../components/Baseline';
import { DecisionBadge, EmptyState, ErrorNotice, LimitNotice, Loading, SimulationBanner } from '../components/Common';

const Charts=lazy(()=>import('../components/Charts'));
// Waterbody ids are reference keys (e.g. LAUT_INDONESIA); users see them as words.
const placeName=(id:string)=>id.toLocaleLowerCase('id').split('_').map(w=>w.charAt(0).toLocaleUpperCase('id')+w.slice(1)).join(' ');
const genusOf=(c:Claim)=>(c.reported_rank==='genus'?c.reported_name:c.reported_rank==='species'||c.reported_rank==='hybrid_alias'?c.reported_name:c.best_match||'').split(' ')[0];
const reasonNames:Record<string,string>={...labelNames,observed_reference_gap:'Belum ada referensi',unknown:'DNA tidak dikenal'};

export default function Results(){
  const {id}=useParams();
  const resource=useResource<RunResult>(`/api/runs/${id}`);
  const sites=useResource<SitePoint[]>(`/api/runs/${id}/sites`);
  const baselinePct=useBaselinePct();
  const [search,setSearch]=useState('');
  const [decision,setDecision]=useState('');
  const [site,setSite]=useState('');
  const [label,setLabel]=useState('');
  const [copied,setCopied]=useState(false);
  const [showPriorities,setShowPriorities]=useState(false);
  const [showCoverage,setShowCoverage]=useState(false);
  const [expanded,setExpanded]=useState(false);
  const [params,setParams]=useSearchParams();
  const query=useDeferredValue(search);
  const claims=resource.data?.claims;
  const filtered=useMemo(()=>claims?.filter(c=>(!decision||c.decision===decision)&&(!site||c.site_id===site)&&(!label||c.labels.includes(label))&&(!query||`${c.reported_name} ${c.taxon_lab}`.toLocaleLowerCase('id').includes(query.toLocaleLowerCase('id'))))??[],[claims,decision,site,label,query]);
  const runGenera=useMemo(()=>new Set((claims??[]).map(genusOf).filter(Boolean)),[claims]);
  if(resource.loading)return <Loading/>;
  if(resource.error)return <ErrorNotice message={resource.error}/>;
  if(!resource.data)return null;
  const run=resource.data;const summary=run.summary;
  const provenance=run.manifest.parameters.data_provenance as DataProvenance|undefined;
  const selected=filtered.find(c=>c.claim_id===params.get('claim'))??filtered[0];
  // Only genera that occur in this run, with at least one species still missing a reference.
  const coverageRows=run.coverage.filter(r=>runGenera.has(r.genus)&&r.r<r.n).sort((a,b)=>b.p_missing-a.p_missing||b.n-a.n||a.genus.localeCompare(b.genus));
  const openClaim=(claim:Claim)=>{setParams(old=>{const next=new URLSearchParams(old);next.set('claim',claim.claim_id);return next;},{replace:true});document.getElementById('claims')?.scrollIntoView({block:'start'});};
  const attention=[...run.claims].filter(c=>c.decision==='must_verify'||c.in_negative_control||c.reported_rank==='unknown').sort((a,b)=>Number(b.labels.includes('endemic'))-Number(a.labels.includes('endemic'))||Number(b.labels.includes('invasive'))-Number(a.labels.includes('invasive'))||Number(b.in_negative_control)-Number(a.in_negative_control)||b.total_reads-a.total_reads||a.claim_id.localeCompare(b.claim_id)).slice(0,5);
  const priorities=run.barcode_priority.slice(0,showPriorities?25:5);
  const code=run.manifest.report_fingerprint.slice(0,12);
  return <div className="results-page">
    <div className="page-heading"><div><h1>Hasil verifikasi eDNA</h1><p className="run-context"><MapPin size={14}/>{summary.waterbodies.map(placeName).join(', ')}<span>·</span>{summary.sites.length} lokasi<span>·</span>{run.manifest.started_at.slice(0,10)}</p></div>
      <div className="heading-actions"><a className="button primary" href={`/api/runs/${id}/report.pdf`}><FileCheck2 size={16}/>Unduh PDF</a><details className="download-menu"><summary className="button secondary">Lainnya<ChevronDown size={14}/></summary><div><a href={`/api/runs/${id}/summary.pdf`}>Ringkasan 1 halaman (PDF)</a><a href={`/api/runs/${id}/export.zip`}>Unduh CSV</a></div></details></div></div>
    {summary.is_simulated?<SimulationBanner/>:null}
    {provenance?<details className="real-data-banner"><summary><Info size={16}/><span><strong>Data asli</strong> · {provenance.label} · {provenance.license} · Kamus {run.manifest.reference_version}</span><ChevronDown size={14}/></summary><div><p>{provenance.citation} · <a className="text-button" href={`https://doi.org/${provenance.doi}`} target="_blank" rel="noreferrer">Dataset sumber</a></p><ul>{provenance.limitations.map((limitation,i)=><li key={i}>{limitation}</li>)}</ul></div></details>:null}
    <nav className="section-nav" aria-label="Bagian hasil">{[['summary','Ringkasan'],['claims','Daftar klaim'],['coverage','Celah kamus'],['audit','Kode verifikasi']].map(([anchor,text])=><a href={`#${anchor}`} key={anchor}>{text}</a>)}</nav>
    <section id="summary" className="result-section">
      <div className="kpi-grid">{[[formatNumber(summary.total_claims),'Deteksi diperiksa'],[formatNumber(summary.total_taxa),'Jenis ikan'],[`${summary.safe_percent.toLocaleString('id-ID',{maximumFractionDigits:0})}%`,'Aman dilaporkan'],[formatNumber(summary.must_verify_count),'Wajib verifikasi']].map(([value,title])=><div className="card kpi-card" key={title}><span>{title}</span><strong>{value}</strong></div>)}</div>
      <div className="decision-grid">{summary.decisions.map(d=><button className={`decision-tile ${d.decision} ${decision===d.decision?'is-active':''}`} key={d.decision} onClick={()=>{setDecision(old=>old===d.decision?'':d.decision);document.getElementById('claims')?.scrollIntoView({block:'start'});}}><div className="decision-tile-top"><DecisionBadge decision={d.decision}/><ArrowUpRight size={15}/></div><strong>{formatNumber(d.claims)}<small> klaim</small></strong></button>)}</div>
      <BaselineSentence claims={run.claims} pct={baselinePct}/>
    </section>
    <div className="two-column result-section"><section className="card attention-card"><div className="card-heading"><h2>Perlu perhatian</h2></div>{attention.length?<div className="attention-list">{attention.map(c=><button key={c.claim_id} onClick={()=>{setDecision('');setSite('');setLabel('');setSearch('');openClaim(c);}}><span className={`attention-dot ${c.decision}`}/><div><i>{c.reported_name}</i><small>{c.site_id} · {c.labels.length?c.labels.map(l=>labelNames[l]??l).join(', '):c.causes.map(x=>causeNames[x]??x).join(', ')}</small></div><ArrowUpRight size={15}/></button>)}</div>:<EmptyState message="Tidak ada yang perlu perhatian khusus."/>}</section><CauseSummary run={run}/></div>
    {summary.sites.length>1?<section className="card result-section location-card"><div className="card-heading"><h2>Keputusan per lokasi</h2></div><Suspense fallback={<Loading/>}><Charts claims={run.claims}/></Suspense></section>:null}
    {sites.data?.length?<section className="card result-section"><div className="card-heading"><div><h2>Peta lokasi</h2><p>Lokasi sensitif disamarkan.</p></div></div><Suspense fallback={<Loading/>}><Charts sites={sites.data}/></Suspense></section>:null}
    <div className="claims-workspace result-section"><section id="claims" className="card result-section claims-section"><div className="card-heading"><div><h2>Daftar klaim <span className="count-pill">{filtered.length}</span></h2><p>Klik baris untuk melihat bukti.</p></div></div><div className="table-filters"><label className="search-field"><Search size={16}/><input aria-label="Cari klaim" placeholder="Cari nama ikan…" value={search} onChange={e=>setSearch(e.target.value)}/></label><select aria-label="Filter keputusan" value={decision} onChange={e=>setDecision(e.target.value)}><option value="">Semua keputusan</option>{decisions.map(d=><option key={d} value={d}>{decisionLabels[d]}</option>)}</select><select aria-label="Filter lokasi" value={site} onChange={e=>setSite(e.target.value)}><option value="">Semua lokasi</option>{summary.sites.map(s=><option key={s}>{s}</option>)}</select><select aria-label="Filter label" value={label} onChange={e=>setLabel(e.target.value)}><option value="">Semua label</option>{Object.entries(labelNames).map(([key,text])=><option value={key} key={key}>{text}</option>)}</select></div><ClaimsTable claims={filtered} onSelect={openClaim} selectedClaimId={selected?.claim_id}/></section>{selected?<EvidenceCard key={`inline-${selected.claim_id}`} inline claim={selected} runId={run.run_id} onClose={()=>setExpanded(false)} onExpand={()=>setExpanded(true)}/>:<aside className="card"><EmptyState message="Ubah filter untuk melihat bukti."/></aside>}</div>
    <div id="coverage" className="two-column result-section">
      <section className="card coverage-card"><div className="card-heading"><div><h2>Celah kamus</h2><p>Genus pada hasil ini yang sebagian spesiesnya belum punya referensi DNA.</p></div><span className="muted small">Punya / tercatat</span></div>{coverageRows.length?<><Suspense fallback={<Loading/>}><Charts coverage={coverageRows.slice(0,8)}/></Suspense><div className="coverage-details">{(showCoverage?coverageRows:coverageRows.slice(0,8)).map(r=><details key={`${r.waterbody_id}-${r.genus}`}><summary><i>{r.genus}</i><span>{r.r} / {r.n}</span><ChevronDown size={14}/></summary><p>Belum ada referensi: {r.missing_species.join(', ')}.</p></details>)}</div>{coverageRows.length>8?<button className="text-button" onClick={()=>setShowCoverage(v=>!v)}>{showCoverage?'Ringkas':`Lihat semua (${coverageRows.length})`}</button>:null}</>:<EmptyState message="Semua genus pada hasil ini sudah punya referensi."/>}</section>
      <section className="card priority-card"><div className="card-heading"><div><h2>Prioritas referensi DNA</h2><p>Ikan yang perlu dibuatkan referensi berikutnya.</p></div></div>{priorities.length?<ol className="priority-list">{priorities.map((p,i)=><li key={`${p.waterbody_id}-${p.name_or_asv}`}><span className="priority-number">{i+1}</span><div>{p.type==='asv'?<span>DNA tidak dikenal <small>{p.name_or_asv}</small></span>:<i>{p.name_or_asv}</i>}<small>{p.reasons.map(r=>reasonNames[r]??r).join(' · ')}</small></div></li>)}</ol>:<EmptyState message="Tidak ada prioritas pada hasil ini."/>}<div className="priority-actions">{run.barcode_priority.length>5?<button className="text-button" onClick={()=>setShowPriorities(v=>!v)}>{showPriorities?'Tampilkan 5 teratas':'Lihat lebih banyak'}</button>:null}<button className="text-button" onClick={()=>downloadPriorities(run)}><ArrowDownToLine size={14}/>Unduh daftar lengkap (CSV)</button></div></section>
    </div>
    <section id="audit" className="card result-section audit-compact"><div className="audit-title"><Fingerprint size={18}/><div><h2>Kode verifikasi</h2><p>Penerima laporan dapat memeriksa keasliannya dengan kode ini.</p></div></div><div className="audit-code"><code>{code}</code><button className="icon-button" aria-label="Salin kode verifikasi" onClick={()=>void navigator.clipboard.writeText(code).then(()=>setCopied(true))}>{copied?<Check size={17}/>:<Copy size={17}/>}</button><Link className="text-button" to="/verify">Periksa laporan</Link></div><span className="small muted">Kamus {run.manifest.reference_version} · Aturan {run.manifest.rules_version}</span></section>
    <LimitNotice/>
    {selected&&expanded?<EvidenceCard key={selected.claim_id} claim={selected} runId={run.run_id} onClose={()=>setExpanded(false)}/>:null}
  </div>;
}
