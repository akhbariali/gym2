import React, {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import Account from './Account.jsx';
import ProductPage from './ProductPage.jsx';
import ShopPage from './ShopPage.jsx';
import HomeSlideshow from './HomeSlideshow.jsx';
import SiteLayout from './SiteLayout.jsx';
import CategoryMenu from './CategoryMenu.jsx';
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
 if(error)return <SiteLayout><main className="wrap"><h1>{error}</h1><a href="/">بازگشت به خانه</a></main></SiteLayout>;
 if(!page)return <SiteLayout><main className="wrap" role="status">در حال بارگذاری…</main></SiteLayout>;
 return <><div dangerouslySetInnerHTML={{__html:page}}/><CategoryMenu/>{location.pathname==='/'&&<HomeSlideshow/>}</>;
}
const journalContent = document.querySelector('#root .blog-main')?.outerHTML;

function Journal(){
 useEffect(()=>{
  if(!journalContent)return;
  const script=document.createElement('script');
  script.src='/blog.js';
  document.body.append(script);
  return()=>script.remove();
 },[]);
 return <SiteLayout textWordmark>{journalContent
  ? <div dangerouslySetInnerHTML={{__html:journalContent}}/>
  : <main className="wrap"><h1>مقاله پیدا نشد</h1><a href="/blog/">مجله وی کلاب</a></main>
 }</SiteLayout>;
}
createRoot(document.getElementById('root')).render((location.pathname.startsWith('/account')||location.pathname==='/checkout/')?<Account/>:location.pathname.startsWith('/shop')?<ShopPage/>:location.pathname.startsWith('/products/')?<ProductPage/>:location.pathname.startsWith('/blog')?<Journal/>:<Storefront/>);
