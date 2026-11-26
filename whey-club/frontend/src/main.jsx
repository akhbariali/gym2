import React, {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import Account from './Account.jsx';
import ProductPage from './ProductPage.jsx';
import ShopPage from './ShopPage.jsx';
import SiteLayout from './SiteLayout.jsx';
import LoadingPage from './LoadingPage.jsx';
import Homepage from './Homepage.jsx';
import site from '../../content/site.json';
// Preserve the existing page markup while React owns rendering and API loading.
const pages = import.meta.glob('./pages/**/index.html', {query:'?raw',import:'default'});
function Storefront(){
 const [page,setPage]=useState(null),[error,setError]=useState('');
 useEffect(()=>{let active=true;async function load(){try{
  const path=location.pathname.replace(/\/?$/, '/');
  const key='./pages'+(path==='/'?'/index.html':path+'index.html');
  if(!pages[key])throw new Error('صفحه پیدا نشد');
  const response=await fetch('/api/products/');if(!response.ok)throw new Error('ارتباط با فروشگاه برقرار نشد');
  const data=await response.json();window.WHEY_PRODUCTS=data.results.filter(p=>!p.is_demo);
  window.WHEY_SITE=site;
  const doc=new DOMParser().parseFromString(await pages[key](),'text/html');
  doc.querySelectorAll('body > :is(.trust-bar,header,footer)').forEach(element=>element.remove());
  if(path==='/kits/'){
   doc.querySelectorAll('.kit,.natural-demo-note').forEach(el=>el.remove());
   const heading=doc.querySelector('.route-heading');
   if(heading)heading.innerHTML='<div class="kicker">کیت‌های آماده</div><h1>کیت‌های جدید در راه‌اند.</h1><p>در حال حاضر کیت آماده‌ای برای خرید موجود نیست. محصولات موجود را در فروشگاه ببینید.</p><a class="primary" href="/shop/">مشاهده محصولات موجود ←</a>';
  }
  doc.querySelectorAll('a[href^="/products/"]').forEach(a=>{if(!window.WHEY_PRODUCTS.some(p=>a.getAttribute('href')==='/products/'+p.slug+'/'))a.setAttribute('href','/shop/')});
  document.title=doc.title;document.body.className=doc.body.className;
  window.__wheyPageScripts=[...doc.querySelectorAll('script')].filter(s=>s.type!=='application/ld+json'&&!new URL(s.src,location.origin).pathname.endsWith('/catalog.js')).map(s=>({src:s.getAttribute('src'),text:s.textContent}));
  doc.querySelectorAll('link[rel="stylesheet"]').forEach(link=>{const href=link.getAttribute('href');if(!document.querySelector(`link[href="${href}"]`)){const el=document.createElement('link');el.rel='stylesheet';el.href=href;document.head.append(el)}});
  doc.querySelectorAll('script').forEach(s=>s.remove());
  if(active)setPage(doc.body.innerHTML);
 }catch(e){if(active)setError(e.message)}}load();return()=>{active=false}},[]);
 useEffect(()=>{if(!page)return;let cancelled=false;const added=[];async function start(){for(const item of window.__wheyPageScripts||[]){if(cancelled)return;const script=document.createElement('script');added.push(script);if(item.src){script.src=item.src;await new Promise((resolve,reject)=>{script.onload=resolve;script.onerror=reject;document.body.append(script)})}else{script.textContent=item.text;document.body.append(script)}}}start().catch(console.error);return()=>{cancelled=true;added.forEach(s=>s.remove())}},[page]);
 if(error)return <SiteLayout><main className="wrap"><h1>{error}</h1><a href="/">بازگشت به خانه</a></main></SiteLayout>;
 if(!page)return <SiteLayout><LoadingPage/></SiteLayout>;
 return <SiteLayout><div dangerouslySetInnerHTML={{__html:page}}/></SiteLayout>;
}
const journalContent = document.querySelector('#root .blog-main')?.outerHTML;

function Journal(){
 const [data,setData]=useState(null),[error,setError]=useState('');
 const parts=location.pathname.split('/').filter(Boolean),slug=parts[1],isCategory=slug==='category';
 const categoryNames={'whey-protein':'پروتئین وی','supplements':'کراتین و مکمل‌ها','sports-nutrition':'تغذیه ورزشی','training':'تمرین و عضله‌سازی','fitness-lifestyle':'اهداف و سبک زندگی','buying-guides':'راهنمای خرید و ایمنی'};
 useEffect(()=>{
  if(journalContent){const script=document.createElement('script');script.src='/blog.js';document.body.append(script);return()=>script.remove()}
  const controller=new AbortController();
  fetch('/api/articles/'+(slug&&!isCategory?slug+'/':''),{signal:controller.signal}).then(r=>{if(!r.ok)throw Error('مقاله پیدا نشد');return r.json()}).then(value=>{if(isCategory)value.results=value.results.filter(a=>a.category===categoryNames[parts[2]]);setData(value)}).catch(e=>{if(e.name!=='AbortError')setError(e.message)});
  return()=>controller.abort();
 },[]);
 return <SiteLayout>{journalContent?<div dangerouslySetInnerHTML={{__html:journalContent}}/>:error?<main className="wrap blog-main"><h1>{error}</h1><a href="/blog/">مجله وی کلاب</a></main>:!data?<LoadingPage label="در حال بارگذاری مجله…"/>:<main className="wrap blog-main">{data.results?<><h1>{isCategory?'مقاله‌های '+(categoryNames[parts[2]]||'مجله'):'مجله وی کلاب'}</h1><div className="editorial-grid">{data.results.map(a=><a className="editorial-card editorial-body" key={a.slug} href={'/blog/'+(a.url_slug||a.slug)+'/'}><span>{a.category}</span><h2>{a.title}</h2><p>{a.meta_description}</p></a>)}</div>{!data.results.length&&<p>هنوز مقاله‌ای در این دسته منتشر نشده است.</p>}</>:<article className="prose"><h1>{data.title}</h1>{data.content_markdown.split(/\n\n/).filter(p=>!p.startsWith('# ')).map((p,i)=>p.startsWith('##')?<h2 key={i}>{p.replace(/^#+ /,'')}</h2>:<p key={i}>{p}</p>)}<h2>منابع</h2>{data.sources?.map(source=><p key={source}><a href={source} rel="noopener noreferrer">{source}</a></p>)}</article>}</main>}</SiteLayout>;
}
createRoot(document.getElementById('root')).render(location.pathname==='/'?<Homepage/>:(location.pathname.startsWith('/account')||location.pathname==='/checkout/')?<Account/>:location.pathname.startsWith('/shop')?<ShopPage/>:location.pathname.startsWith('/products/')?<ProductPage/>:location.pathname.startsWith('/blog')?<Journal/>:<Storefront/>);
