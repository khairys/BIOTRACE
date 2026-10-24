import { useState } from 'react';
import { BadgeCheck, Fingerprint, SearchCheck, ShieldAlert } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { VerifyResponse } from '../api/generated';
import { ApiError, request } from '../api/client';
import { ErrorNotice, LimitNotice } from '../components/Common';

export default function Verify(){
  const [code,setCode]=useState('');
  const [result,setResult]=useState<VerifyResponse|null>(null);
  const [error,setError]=useState('');
  const [busy,setBusy]=useState(false);
  const submit=async(event:React.FormEvent)=>{event.preventDefault();setBusy(true);setError('');setResult(null);try{setResult(await request<VerifyResponse>('/api/verify',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({report_fingerprint:code.trim()})}));}catch(e){setError(e instanceof ApiError?e.message:'Verifikasi gagal.');}finally{setBusy(false);}};
  return <div className="document-page"><div className="eyebrow"><Fingerprint size={15}/>VERIFIKASI LAPORAN</div><h1>Periksa keaslian laporan.</h1><p className="page-intro">Masukkan kode verifikasi dari kaki halaman PDF (12 karakter) atau sidik jari laporan lengkap (64 karakter). Pemeriksaan hanya mencakup run yang tersimpan di perangkat ini, lalu menghitung ulang seluruh hash masukan dan keluaran.</p>
  <form className="card verify-form" onSubmit={e=>void submit(e)}><label htmlFor="verify-code">Kode verifikasi</label><div><input id="verify-code" className="text-input mono" value={code} onChange={e=>setCode(e.target.value)} placeholder="mis. 3acf028538d4" autoComplete="off" spellCheck={false}/><button className="button primary" disabled={busy||code.trim().length<12}><SearchCheck size={16}/>{busy?'Memeriksa…':'Periksa'}</button></div></form>
  {error?<ErrorNotice message={error}/>:null}
  {result?<section className="card verify-result">{!result.found?<div className="verify-status bad"><ShieldAlert size={22}/><div><h2>Kode tidak ditemukan</h2><p>Tidak ada run dengan kode ini di perangkat ini. Laporan mungkin dibuat di perangkat lain atau kodenya keliru.</p></div></div>:result.valid?<div className="verify-status good"><BadgeCheck size={22}/><div><h2>Laporan cocok dan utuh</h2><p>Seluruh hash masukan dan keluaran sama dengan saat laporan dibuat.</p></div></div>:<div className="verify-status bad"><ShieldAlert size={22}/><div><h2>Run ditemukan tetapi berubah</h2><p>Berkas tersimpan tidak lagi cocok dengan sidik jarinya: {result.errors.join(', ')}.</p></div></div>}
  {result.found?<dl className="evidence-facts"><div><dt>Run</dt><dd><Link className="text-button" to={`/runs/${result.run_id}`}>{result.run_id}</Link></dd></div><div><dt>Sidik jari laporan</dt><dd className="mono">{result.report_fingerprint}</dd></div><div><dt>Kamus</dt><dd>{result.reference_version}</dd></div><div><dt>Aturan</dt><dd>{result.rules_version}</dd></div><div><dt>Engine</dt><dd>{result.engine_version}</dd></div><div><dt>Dibuat</dt><dd>{result.started_at?.slice(0,19).replace('T',' ')}</dd></div><div><dt>Data</dt><dd>{result.is_simulated?<span className="simulation-tag">SIMULASI</span>:'Data pengguna'}</dd></div></dl>:null}</section>:null}
  <LimitNotice/></div>;
}
