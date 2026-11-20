import React, {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import Account from './Account.jsx';
import ProductPage from './ProductPage.jsx';
import HomeSlideshow from './HomeSlideshow.jsx';
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
  const data=await response.json();window.WHEY_PRODUCTS=data.results;
  window.WHEY_SITE=site;
  const doc=new DOMParser().parseFromString(await pages[key](),'text/html');
  const cartLink=doc.querySelector('.cart-button');if(cartLink)cartLink.insertAdjacentHTML('beforebegin','<a class="account-link" href="/account/">ورود / حساب من</a>');
  document.title=doc.title;document.body.className=doc.body.className;
  window.__wheyPageScripts=[...doc.querySelectorAll('script')].filter(s=>s.type!=='application/ld+json'&&!new URL(s.src,location.origin).pathname.endsWith('/catalog.js')).map(s=>({src:s.getAttribute('src'),text:s.textContent}));
  doc.querySelectorAll('link[rel="stylesheet"]').forEach(link=>{const href=link.getAttribute('href');if(!document.querySelector(`link[href="${href}"]`)){const el=document.createElement('link');el.rel='stylesheet';el.href=href;document.head.append(el)}});
  doc.querySelectorAll('script').forEach(s=>s.remove());
  if(active)setPage(doc.body.innerHTML);
 }catch(e){if(active)setError(e.message)}}load();return()=>{active=false}},[]);
 useEffect(()=>{if(!page)return;let cancelled=false;const added=[];async function start(){for(const item of window.__wheyPageScripts||[]){if(cancelled)return;const script=document.createElement('script');added.push(script);if(item.src){script.src=item.src;await new Promise((resolve,reject)=>{script.onload=resolve;script.onerror=reject;document.body.append(script)})}else{script.textContent=item.text;document.body.append(script)}}}start().catch(console.error);return()=>{cancelled=true;added.forEach(s=>s.remove())}},[page]);
 if(error)return <main className="wrap"><h1>{error}</h1><a href="/">بازگشت به خانه</a></main>;
 if(!page)return <main className="wrap" role="status">در حال بارگذاری…</main>;
 return <><div dangerouslySetInnerHTML={{__html:page}}/>{location.pathname==='/'&&<HomeSlideshow/>}</>;
}
function Journal(){
 const [items,setItems]=useState(null),[error,setError]=useState('');
 const slug=location.pathname.split('/').filter(Boolean)[1];
 const isCategory=slug==='category';
 useEffect(()=>{fetch('/api/articles/'+(slug&&!isCategory?slug+'/':'')).then(r=>{if(!r.ok)throw new Error('مقاله پیدا نشد');return r.json()}) .then(data=>{if(isCategory){const categories={'whey-protein':'پروتئین وی','supplements':'کراتین و مکمل‌ها','sports-nutrition':'تغذیه ورزشی','training':'تمرین و عضله‌سازی','fitness-lifestyle':'اهداف و سبک زندگی','buying-guides':'راهنمای خرید و ایمنی'};const category=categories[location.pathname.split('/').filter(Boolean)[2]];data.results=data.results.filter(a=>a.category===category)}setItems(data)}).catch(e=>setError(e.message))},[]);
 if(error)return <main className="wrap"><h1>{error}</h1><a href="/blog/">مجله وی کلاب</a></main>;
 if(!items)return <p className="wrap">در حال بارگذاری…</p>;
 return <><header className="wrap blog-header"><a className="logo" href="/">WHEY CLUB</a><a href="/shop/">فروشگاه</a><a href="/blog/">مجله وی کلاب</a></header><main className="wrap blog-main">{items.results?<><h1>مجله وی کلاب</h1><div className="editorial-grid">{items.results.map(a=><a className="editorial-card editorial-body" key={a.slug} href={'/blog/'+(a.url_slug||a.slug)+'/'}><span>{a.category} · حدود ۲ دقیقه مطالعه</span><h2>{a.title}</h2><p>{a.meta_description}</p></a>)}</div></>:<article className="prose"><h1>{items.title}</h1><p>حدود ۲ دقیقه مطالعه · تحریریه وی کلاب</p>{items.content_markdown.split(/\n\n/).filter(p=>!p.startsWith('# ')).map((p,i)=>p.startsWith('##')?<h2 key={i}>{p.replace(/^#+ /,'')}</h2>:<p key={i}>{p}</p>)}<p className="editorial-disclosure">این مطلب آموزشی با کمک هوش مصنوعی تهیه شده و بازبینی تخصصی پزشکی نشده است.</p><h2>منابع</h2>{items.sources.map(s=><p key={s}><a href={s} rel="noopener noreferrer">{s}</a></p>)}</article>}</main></>;
}
createRoot(document.getElementById('root')).render((location.pathname.startsWith('/account')||location.pathname==='/checkout/')?<Account/>:location.pathname.startsWith('/products/')?<ProductPage/>:location.pathname.startsWith('/blog')?<Journal/>:<Storefront/>);
