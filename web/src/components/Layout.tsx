import { BookOpen, Dna, FileCheck2, Fingerprint, FlaskConical, FlaskRound, LockKeyhole, Plus, Waves } from 'lucide-react';
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom';

export default function Layout(){
  const location=useLocation();
  return <div className="app-layout">
    <aside className="sidebar">
      <Link to="/" className="brand"><span className="brand-icon"><Dna size={25}/></span><span>BioTrace<small>INDONESIA</small></span></Link>
      <nav aria-label="Navigasi utama">
        <NavLink to="/" end><Plus size={18}/>Analisis baru</NavLink>
        {location.pathname.startsWith('/runs/')?<NavLink to={location.pathname}><FileCheck2 size={18}/>Hasil verifikasi</NavLink>:null}
        <NavLink to="/verify"><Fingerprint size={18}/>Verifikasi laporan</NavLink>
      </nav>
      <div className="workspace-label">UNTUK PENELITI</div>
      <nav aria-label="Navigasi peneliti" className="secondary-nav">
        <NavLink to="/methods"><BookOpen size={16}/>Metode & aturan</NavLink>
        <NavLink to="/validation"><FlaskConical size={16}/>Validasi & dataset</NavLink>
        <NavLink to="/reference/propose"><FlaskRound size={16}/>Usulan sekuens</NavLink>
      </nav>
      <div className="sidebar-bottom"><p><LockKeyhole size={14}/>Diproses di perangkat ini.</p></div>
    </aside>
    <div className="main-shell"><header className="topbar"><span><Waves size={17}/>Verifikasi biodiversitas perairan</span></header><main id="main-content"><Outlet/></main><footer className="app-footer"><span>BioTrace Indonesia</span><span>Ambang usulan tim, belum dikalibrasi ahli.</span></footer></div>
  </div>;
}
