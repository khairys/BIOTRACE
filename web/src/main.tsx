import React, { lazy, Suspense } from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import '@fontsource/inter/latin-400.css';
import '@fontsource/inter/latin-500.css';
import '@fontsource/inter/latin-600.css';
import '@fontsource/inter/latin-700.css';
import '@fontsource/inter/latin-400-italic.css';
import '@fontsource/jetbrains-mono/latin-400.css';
import Layout from './components/Layout';
import { Loading } from './components/Common';
import Upload from './pages/Upload';
import './styles.css';

const Results=lazy(()=>import('./pages/Results'));
const Methods=lazy(()=>import('./pages/Methods'));
const Validation=lazy(()=>import('./pages/Validation'));
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><BrowserRouter><Suspense fallback={<Loading/>}><Routes><Route element={<Layout/>}><Route index element={<Upload/>}/><Route path="runs/:id" element={<Results/>}/><Route path="methods" element={<Methods/>}/><Route path="validation" element={<Validation/>}/><Route path="*" element={<Navigate to="/" replace/>}/></Route></Routes></Suspense></BrowserRouter></React.StrictMode>);
