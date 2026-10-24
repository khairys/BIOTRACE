import { useEffect, useState } from 'react';
import type { ValidationReport } from './generated';

export class ApiError extends Error {
  validation: ValidationReport | null;
  constructor(message:string, validation:ValidationReport|null=null){super(message);this.validation=validation;}
}
export async function request<T>(url:string, options?:RequestInit):Promise<T>{
  const response=await fetch(url,options);
  const body=await response.json() as T & {error?:{message?:string;validation?:ValidationReport}};
  if(!response.ok) throw new ApiError(body.error?.message??'Permintaan gagal. Coba kembali.',body.error?.validation??null);
  return body;
}
export function useResource<T>(url:string){
  const [state,setState]=useState<{data:T|null;error:string;loading:boolean}>({data:null,error:'',loading:true});
  useEffect(()=>{
    const controller=new AbortController();
    setState({data:null,error:'',loading:true});
    request<T>(url,{signal:controller.signal}).then(data=>setState({data,error:'',loading:false})).catch((error:unknown)=>{
      if(!controller.signal.aborted) setState({data:null,error:error instanceof Error?error.message:'Permintaan gagal.',loading:false});
    });
    return()=>controller.abort();
  },[url]);
  return state;
}
