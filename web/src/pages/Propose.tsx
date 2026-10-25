import { useState } from 'react';
import { FileUp, FlaskRound, Info, Send } from 'lucide-react';
import type { ProposalResponse } from '../api/generated';
import { ApiError, request } from '../api/client';
import { ErrorNotice, LimitNotice } from '../components/Common';
import { formatNumber } from '../i18n/id';

const resultNames:Record<string,string>={accepted:'Diterima',flagged:'Ditandai',rejected:'Ditolak'};
export default function Propose(){
  const [fasta,setFasta]=useState<File|null>(null);
  const [metadata,setMetadata]=useState<File|null>(null);
  const [simulation,setSimulation]=useState(false);
  const [result,setResult]=useState<ProposalResponse|null>(null);
  const [error,setError]=useState('');
  const [busy,setBusy]=useState(false);
  const submit=async(event:React.FormEvent)=>{event.preventDefault();if(!fasta||!metadata)return;setBusy(true);setError('');setResult(null);const body=new FormData();body.append('fasta',fasta);body.append('metadata',metadata);body.append('simulation',String(simulation));try{setResult(await request<ProposalResponse>('/api/reference/proposals',{method:'POST',body}));}catch(e){setError(e instanceof ApiError?e.message:'Usulan gagal diperiksa.');}finally{setBusy(false);}};
  return <div className="document-page"><div className="eyebrow"><FlaskRound size={15}/>USULAN SEKUENS KOLABORATOR</div><h1>Usulkan sekuens untuk kamus.</h1><p className="page-intro">Unggah FASTA dan metadata sekuens. BioTrace memeriksanya dan menampilkan mana yang diterima, ditandai, atau ditolak. Usulan tidak langsung masuk kamus; kurator yang menerbitkan versi baru.</p>
  <div className="info-notice"><Info size={16}/><span>Sekuens eDNA (voucher V4) tidak pernah masuk kamus. Nama spesies hanya dari sumber yang dapat ditelusuri.</span></div>
  <form className="card propose-form" onSubmit={e=>void submit(e)}><label>FASTA sekuens<input type="file" accept=".fasta,.fa,.fna" onChange={e=>setFasta(e.target.files?.[0]??null)}/></label><label>Metadata sekuens (CSV/TSV)<input type="file" accept=".csv,.tsv" onChange={e=>setMetadata(e.target.files?.[0]??null)}/></label><label className="check-row"><input type="checkbox" checked={simulation} onChange={e=>setSimulation(e.target.checked)}/>Periksa terhadap kamus demo SIMULASI</label><button className="button primary" disabled={busy||!fasta||!metadata}>{busy?<FileUp size={16}/>:<Send size={16}/>}{busy?'Memeriksa…':'Periksa usulan'}</button></form>
  {error?<ErrorNotice message={error}/>:null}
  {result?<section className="card"><div className="card-heading"><div><h2>Laporan kurasi <span className="count-pill">{result.proposal_id}</span></h2><p>Terhadap kamus {result.reference_version} · aturan {result.rules_version} · status menunggu kurator</p></div>{result.contains_simulated?<span className="simulation-tag">SIMULASI</span>:null}</div><div className="audit-versions"><span>Diajukan <strong>{formatNumber(result.submitted)}</strong></span>{Object.entries(result.counts).map(([key,value])=><span key={key}>{resultNames[key]??key} <strong>{formatNumber(value)}</strong></span>)}<span>Layak setelah kurasi <strong>{formatNumber(result.eligible_after_curation)}</strong></span></div><div className="table-scroll"><table className="parameter-table"><thead><tr><th>ID</th><th>Aksesi</th><th>Langkah</th><th>Hasil</th><th>Alasan</th></tr></thead><tbody>{result.report.map((row,i)=><tr key={i}><td className="mono">{row.seq_id}</td><td className="mono">{row.accession||'—'}</td><td>{row.step}</td><td>{resultNames[row.result?.split(':')[0]]??row.result}</td><td>{row.reason}</td></tr>)}</tbody></table></div></section>:null}
  <LimitNotice/></div>;
}
