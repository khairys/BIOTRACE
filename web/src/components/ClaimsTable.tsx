import { useMemo, useState } from 'react';
import { flexRender, getCoreRowModel, getPaginationRowModel, getSortedRowModel, useReactTable, type ColumnDef, type SortingState } from '@tanstack/react-table';
import { ArrowUpDown, ChevronLeft, ChevronRight } from 'lucide-react';
import type { Claim } from '../api/generated';
import { labelNames, rankLabels } from '../i18n/id';
import { DecisionBadge, EmptyState, GradeBadge } from './Common';

export default function ClaimsTable({claims,onSelect}:{claims:Claim[];onSelect:(c:Claim)=>void}){
  const [sorting,setSorting]=useState<SortingState>([]);
  const columns=useMemo<ColumnDef<Claim>[]>(()=>[
    {accessorKey:'site_id',header:'Lokasi',cell:info=><span className="location-cell"><strong>{String(info.getValue())}</strong><small>{info.row.original.asv_id}</small></span>},
    {accessorKey:'taxon_lab',header:'Nama dari lab',cell:info=><i className="muted">{String(info.getValue())||'Tidak tersedia'}</i>},
    {accessorKey:'reported_name',header:'Nama aman',cell:info=><span className="name-cell"><i>{String(info.getValue())}</i><small>{rankLabels[info.row.original.reported_rank]}</small></span>},
    {accessorKey:'grade',header:'Nilai',cell:info=><GradeBadge grade={info.row.original.grade}/>},
    {accessorKey:'decision',header:'Keputusan',cell:info=><DecisionBadge decision={info.row.original.decision}/>},
    {id:'labels',header:'Label',cell:info=><div className="label-list">{info.row.original.labels.length?info.row.original.labels.map(label=><span className="taxon-label" key={label}>{labelNames[label]??label}</span>):<span className="muted">—</span>}</div>},
  ],[]);
  const table=useReactTable({data:claims,columns,state:{sorting},onSortingChange:setSorting,getCoreRowModel:getCoreRowModel(),getSortedRowModel:getSortedRowModel(),getPaginationRowModel:getPaginationRowModel(),initialState:{pagination:{pageSize:12}}});
  if(!claims.length)return <EmptyState message="Tidak ada klaim yang cocok dengan filter."/>;
  return <><div className="table-scroll"><table className="claims-table"><thead>{table.getHeaderGroups().map(group=><tr key={group.id}>{group.headers.map(header=><th key={header.id}><button disabled={!header.column.getCanSort()} onClick={header.column.getToggleSortingHandler()}>{flexRender(header.column.columnDef.header,header.getContext())}{header.column.getCanSort()?<ArrowUpDown size={11}/>:null}</button></th>)}</tr>)}</thead><tbody>{table.getRowModel().rows.map(row=><tr key={row.id} tabIndex={0} role="button" aria-label={`Buka bukti ${row.original.asv_id} ${row.original.site_id}`} onClick={()=>onSelect(row.original)} onKeyDown={event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();onSelect(row.original);}}}>{row.getVisibleCells().map(cell=><td key={cell.id}>{flexRender(cell.column.columnDef.cell,cell.getContext())}</td>)}</tr>)}</tbody></table></div><div className="table-pagination"><span>{claims.length} klaim · Halaman {table.getState().pagination.pageIndex+1} dari {table.getPageCount()}</span><div><button className="icon-button" aria-label="Halaman sebelumnya" disabled={!table.getCanPreviousPage()} onClick={()=>table.previousPage()}><ChevronLeft size={17}/></button><button className="icon-button" aria-label="Halaman berikutnya" disabled={!table.getCanNextPage()} onClick={()=>table.nextPage()}><ChevronRight size={17}/></button></div></div></>;
}
