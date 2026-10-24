import { BookOpen, CircleDot, Dna, FileCheck2, Fingerprint, FlaskConical, FlaskRound, LockKeyhole, Plus, Waves } from 'lucide-react';
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom';

export default function Layout(){
  const location=useLocation();
  return <div className="app-layout">
    <aside className="sidebar">
      <Link to="/" className="brand"><span className="brand-icon"><Dna size={25}/></span><span>BioTrace<small>INDONESIA</small></span></Link>
      <div className="workspace-label">RUANG KERJA</div>
      <nav aria-label="Navigasi utama">
        <NavLink to="/" end><Plus size={18}/>Analisis baru</NavLink>
        {location.pathname.startsWith('/runs/')?<NavLink to={location.pathname}><FileCheck2 size={18}/>Hasil verifikasi</NavLink>:null}
        <NavLink to="/methods"><BookOpen size={18}/>Metode & aturan</NavLink>
        <NavLink to="/validation"><FlaskConical size={18}/>Validasi & dataset</NavLink>
        <NavLink to="/verify"><Fingerprint size={18}/>Verifikasi laporan</NavLink>
        <NavLink to="/reference/propose"><FlaskRound size={18}/>Usulan sekuens</NavLink>
      </nav>
      <div className="sidebar-bottom"><div className="local-state"><CircleDot size={12}/>Lingkungan lokal</div><p><LockKeyhole size={14}/>Data diproses di perangkat ini.</p><small>Prototipe MVP · v0.1.1</small></div>
    </aside>
    <div className="main-shell"><header className="topbar"><span><Waves size={17}/>Verifikasi biodiversitas perairan</span><span className="topbar-tag">Laporan verifikasi pendukung</span></header><main id="main-content"><Outlet/></main><footer className="app-footer"><span>BioTrace Indonesia</span><span>Usulan tim, belum dikalibrasi ahli.</span></footer></div>
  </div>;
}
