import type { Claim } from '../api/generated';

export type Decision = Claim['decision'];
export const decisions: Decision[] = ['safe','with_note','must_verify','do_not_use'];
export const decisionLabels: Record<Decision,string> = {safe:'Aman dilaporkan',with_note:'Dengan catatan',must_verify:'Wajib verifikasi',do_not_use:'Jangan dipakai'};
export const decisionColors: Record<Decision,string> = {safe:'#15803D',with_note:'#1D4ED8',must_verify:'#C2410C',do_not_use:'#B91C1C'};
export const rankLabels: Record<Claim['reported_rank'],string> = {species:'Spesies',complex:'Kompleks',genus:'Genus',family:'Famili',order:'Ordo',unknown:'Tidak dikenal',hybrid_alias:'Alias hibrida'};
export const labelNames: Record<string,string> = {endemic:'Endemik',threatened:'Terancam',invasive:'Invasif',hybrid_alias:'Alias hibrida',possible_unreferenced_endemic:'Kemungkinan endemik tanpa referensi',possible_endemic:'Kemungkinan endemik/terancam'};
export const causeNames: Record<string,string> = {reference:'Kamus belum lengkap',marker:'Sulit dibedakan',sample:'Sampel lemah',location:'Tidak lazim di lokasi'};
export const warningNames: Record<string,string> = {single_replicate:'Hanya satu replikat',genus_not_in_checklist:'Genus belum tercatat dalam checklist',no_single_genus_for_coverage:'Cakupan per genus tidak dapat ditentukan',voucher_V3_without_physical_catalog:'V3: spesimen paper tanpa katalog voucher',candidate_taxonomy_unavailable:'Taksonomi kandidat belum tersedia',specimen_outside_indonesia:'Referensi hanya dari spesimen luar Indonesia atau asal tidak diketahui',checklist_secondary_source:'Checklist dari sumber sekunder yang belum diverifikasi'};
export const limitNotice='Deteksi DNA bukan bukti pasti ikan hidup di lokasi.';
export const formatNumber=(value:number) => new Intl.NumberFormat('id-ID').format(value);
export const percent=(value:number|null) => value===null?'Belum tersedia':new Intl.NumberFormat('id-ID',{style:'percent',maximumFractionDigits:1}).format(value);
