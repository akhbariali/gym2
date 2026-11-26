import React from 'react';
import '../public/loading.css';
export default function LoadingPage({label='در حال آماده‌سازی صفحه…',compact=false}){
 return <div className={'page-loading'+(compact?' page-loading-compact':'')} role="status" aria-live="polite"><span className="loading-mark" aria-hidden="true">W</span><span className="loading-brand" dir="ltr">WHEYCLUB</span><span className="loading-spinner" aria-hidden="true"/><p>{label}</p><span className="loading-hint">یک لحظه همراه ما باشید</span></div>;
}
