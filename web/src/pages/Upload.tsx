import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { ArrowRight, CircleCheck, FileText, FlaskConical, FolderUp, LoaderCircle, Trash2, UploadCloud, Waves } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ApiError, request, useResource } from '../api/client';
import type { HealthResponse, InspectResponse, RunCreated, ValidationReport, WaterbodyOption } from '../api/generated';
import { ErrorNotice, LimitNotice, SimulationBanner } from '../components/Common';

type Role='reads'|'metadata'|'fasta'|'taxonomy'|'site_context'|'unknown';
type Entry={id:string;file:File;role:Role;hint:string;needs:string[];waterbodies:WaterbodyOption[]};
const roles:Record<Role,string>={reads:'Tabel bacaan',metadata:'Metadata sampel',fasta:'Urutan ASV (FASTA)',taxonomy:'Taksonomi lab',site_context:'Konteks lokasi',unknown:'Pilih peran file'};
const MARKERS=['12S_MiFish_U','16S','COI'];
// Fallback when the API cannot inspect the file; the server (D-039) knows more synonyms.
function localRole(first:string,headers:string[]):Role{
  const keys=headers.map(h=>h.toLowerCase().replace(/[^0-9a-z]+/g,'_').replace(/^_+|_+$/g,''));
  const has=(names:string[])=>names.some(n=>keys.includes(n));
  if(first.startsWith('>')) return 'fasta';
  if(has(['pct_identity','identity','pident','percent_identity'])) return 'taxonomy';
  if(has(['sample_id','sample','sampel'])&&has(['sample_type','waterbody_id','waterbody','site_id','latitude','extraction_batch','marker'])) return 'metadata';
  if(has(['context_type'])) return 'site_context';
  return has(['asv_id','asv','otu_id','otu','zotu','feature_id'])?'reads':'unknown';
}
async function inspect(file:File):Promise<Entry>{
  const content=await file.slice(0,8192).text();
  const first=content.replace(/^\uFEFF/,'').trimStart();
  const headers=first.split(/\r?\n/)[0].split(/[\t,]/).map(s=>s.replaceAll('"','').trim());
  const size=`${new Intl.NumberFormat('id-ID',{maximumFractionDigits:1}).format(file.size/1024)} KB`;
  const entry:Entry={id:crypto.randomUUID(),file,role:localRole(first,headers),hint:size,needs:[],waterbodies:[]};
  if(entry.role==='fasta') return entry;
  try{
    const body=new FormData();body.append('file',file.slice(0,256*1024),file.name);
    const found=await request<InspectResponse>('/api/inputs/inspect',{method:'POST',body});
    return {...entry,role:(found.role in roles?found.role:'unknown') as Role,needs:found.needs,waterbodies:found.waterbodies};
  }catch{return entry;}
}
export default function Upload(){
  const [entries,setEntries]=useState<Entry[]>([]);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState('');
  const [validation,setValidation]=useState<ValidationReport|null>(null);
  const [waterbody,setWaterbody]=useState('');
  const [marker,setMarker]=useState('');
  const navigate=useNavigate();
  const health=useResource<HealthResponse>('/api/health');
  const onDrop=useCallback(async(files:File[])=>{
    const valid=files.filter(f=>f.size<=200*1024*1024&&/\.(csv|tsv|fasta|fa|fna)$/i.test(f.name));
    if(valid.length!==files.length) setError('File harus CSV/TSV/FASTA dan maksimal 200 MB.');else setError('');
    const inspected=await Promise.all(valid.map(inspect));
    setEntries(previous=>[...previous,...inspected]);setValidation(null);
  },[]);
  const {getRootProps,getInputProps,isDragActive,open}=useDropzone({onDrop,noClick:true,noKeyboard:true,disabled:busy});
  const counts=entries.reduce<Record<string,number>>((acc,e)=>{acc[e.role]=(acc[e.role]??0)+1;return acc;},{});
  const duplicate=Object.entries(counts).some(([role,count])=>role!=='unknown'&&count>1);
  // D-039: blank waterbody/marker in metadata are chosen here by the user, never guessed.
  const needs=(key:string)=>entries.some(e=>e.role==='metadata'&&e.needs.includes(key))||!!validation?.issues.some(i=>i.field===key);
  const needWaterbody=needs('waterbody_id'),needMarker=needs('marker');
  const options=entries.find(e=>e.waterbodies.length)?.waterbodies??[];
  const ready=!!counts.reads&&!!counts.metadata&&(!!counts.fasta||!!counts.taxonomy)&&!duplicate&&!counts.unknown&&(!needWaterbody||!!waterbody);
  const simulated=entries.length>0&&entries.every(e=>e.file.name.includes('SIMULASI'));
  async function start(demo:false|'sim'|'asli'=false){
    setBusy(true);setError('');setValidation(null);
    try{
      let result:RunCreated;
      if(demo) result=await request<RunCreated>(`/api/runs/demo/${demo==='asli'?'edna_asli_marwayana2022':'matano_sim_v3'}`,{method:'POST'});
      else{
        const body=new FormData();entries.forEach(e=>body.append(e.role,e.file));body.append('mode',simulated?'simulation':'normal');
        if(needWaterbody&&waterbody) body.append('waterbody_id',waterbody);
        if(needMarker&&marker) body.append('marker',marker);
        result=await request<RunCreated>('/api/runs',{method:'POST',body});
      }
      const flags=[demo==='asli'?'asli=marwayana2022':'',result.precomputed?'precomputed=1':''].filter(Boolean).join('&');
      navigate(`/runs/${result.run_id}${flags?`?${flags}`:''}`);
    }catch(cause){setError(cause instanceof Error?cause.message:'Analisis gagal.');if(cause instanceof ApiError)setValidation(cause.validation);}
    finally{setBusy(false);}
  }
  return <div className="upload-page">
    <h1>Periksa data eDNA Anda.</h1><p className="page-intro">Unggah hasil lab untuk melihat nama ikan mana yang aman dilaporkan.</p>
    {simulated?<SimulationBanner/>:null}
    <section className="card upload-card" aria-label="Unggah berkas analisis">
      <div className="card-heading"><div><h2>Unggah berkas</h2><p>Tabel bacaan, metadata sampel, dan FASTA atau taksonomi lab.</p></div></div>
      <div {...getRootProps()} className={`dropzone ${isDragActive?'drag-active':''}`}>
        <input {...getInputProps({'aria-label':'Pilih berkas analisis'})}/><div className="upload-icon"><UploadCloud size={30} strokeWidth={1.5}/></div>
        <h3>{isDragActive?'Lepaskan file di sini':'Tarik & lepas file di sini'}</h3><p>atau <button className="text-button" type="button" disabled={busy} onClick={open}>pilih file dari perangkat</button></p><small>.csv, .tsv, .fasta, .fa, .fna · maks. 200 MB per file</small>
      </div>
      {entries.length?<div className="file-list"><div className="section-label">FILE TERDETEKSI <span>{entries.length} file</span></div>{entries.map(e=><div className="file-row" key={e.id}><span className="file-icon"><FileText size={20}/></span><div className="file-description"><strong>{e.file.name}</strong><small>{e.hint}</small></div><select aria-label={`Peran ${e.file.name}`} value={e.role} disabled={busy} onChange={event=>setEntries(old=>old.map(x=>x.id===e.id?{...x,role:event.target.value as Role}:x))}>{Object.entries(roles).map(([key,label])=><option value={key} key={key}>{label}</option>)}</select><button className="icon-button" aria-label={`Hapus ${e.file.name}`} disabled={busy} onClick={()=>setEntries(old=>old.filter(x=>x.id!==e.id))}><Trash2 size={16}/></button></div>)}</div>:<div className="required-files"><span><CircleCheck size={15}/>Tabel bacaan</span><span><CircleCheck size={15}/>Metadata sampel</span><span><CircleCheck size={15}/>FASTA atau taksonomi lab</span></div>}
      {needWaterbody||needMarker?<div className="metadata-defaults"><div className="section-label">LENGKAPI DATA</div>
        <div className="metadata-defaults-fields">
          {needWaterbody?<label>Perairan sampel<select aria-label="Perairan sampel" value={waterbody} disabled={busy} onChange={event=>setWaterbody(event.target.value)}><option value="">Pilih perairan…</option>{options.map(o=><option key={o.waterbody_id} value={o.waterbody_id}>{o.name||o.waterbody_id}</option>)}</select></label>:null}
          {needMarker?<label>Marker<select aria-label="Marker" value={marker} disabled={busy} onChange={event=>setMarker(event.target.value)}><option value="">Pilih marker…</option>{MARKERS.map(m=><option key={m} value={m}>{m}</option>)}</select></label>:null}
        </div>
        <small className="muted">Metadata Anda belum mencantumkan ini.</small></div>:null}
      {duplicate?<ErrorNotice message="Setiap peran hanya boleh memiliki satu file. Hapus atau ubah peran file yang duplikat."/>:null}
      {error?<ErrorNotice message={error}/>:null}
      {validation?<ul className="validation-list">{validation.issues.filter(i=>i.level==='error').map((i,index)=><li key={index}>{i.message}</li>)}</ul>:null}
      {busy?<div className="processing" role="status"><LoaderCircle size={18} className="spinner"/><strong>Analisis sedang berjalan…</strong></div>:null}
      <div className="upload-actions"><button className="button primary" disabled={!ready||busy} onClick={()=>void start()}>{busy?<LoaderCircle size={16} className="spinner"/>:<FolderUp size={17}/>}Jalankan analisis<ArrowRight size={16}/></button></div>
      <div className="sample-actions"><span>Coba dengan data contoh:</span><button className="text-button" disabled={busy} onClick={()=>void start('asli')}><Waves size={15}/>Muat data eDNA asli Indonesia</button><button className="text-button" disabled={busy} onClick={()=>void start('sim')}><FlaskConical size={15}/>Muat data demo (SIMULASI)</button></div>
    </section>
    {!health.loading&&!health.data?.reference_ready?<div className="readiness-note"><span className="small-dot amber"/><span>Kamus Indonesia belum siap. Anda tetap dapat mencoba demo SIMULASI.</span></div>:null}
    <LimitNotice/>
  </div>;
}
