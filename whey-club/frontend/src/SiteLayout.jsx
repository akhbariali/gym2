import React,{useEffect,useRef,useState} from 'react';
import homepage from './pages/index.html?raw';
import '../public/luxe.css';
import './mobile.css';

const template=new DOMParser().parseFromString(homepage,'text/html');
const header=template.querySelector('header');
const links=[...header.querySelectorAll('nav>a')].map(a=>({href:a.getAttribute('href'),label:a.textContent}));
const icon=(path)=><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={path}/></svg>;
export default function SiteLayout({children}){
 const [open,setOpen]=useState(false),[count,setCount]=useState(0),[categories,setCategories]=useState([]);
 const menuButton=useRef(null),siteHeader=useRef(null);
 useEffect(()=>{
  const update=()=>{try{setCount(Object.values(JSON.parse(localStorage.getItem('wheyclub-cart')||'{}')).filter(n=>Number.isInteger(n)&&n>0&&n<=99).reduce((a,b)=>a+b,0))}catch{setCount(0)}};
  update();window.addEventListener('whey-cart-change',update);window.addEventListener('storage',update);
  fetch('/api/categories/',{cache:'no-cache'}).then(r=>r.ok?r.json():{results:[]}).then(d=>setCategories(d.results)).catch(()=>{});
  return()=>{window.removeEventListener('whey-cart-change',update);window.removeEventListener('storage',update)};
 },[]);
 useEffect(()=>{
  if(!open)return;
  const close=e=>{if(!siteHeader.current?.contains(e.target))setOpen(false)};
  const escape=e=>{if(e.key==='Escape'){setOpen(false);menuButton.current?.focus()}};
  const resize=()=>{if(window.innerWidth>760)setOpen(false)};
  document.addEventListener('pointerdown',close);document.addEventListener('keydown',escape);window.addEventListener('resize',resize);
  return()=>{document.removeEventListener('pointerdown',close);document.removeEventListener('keydown',escape);window.removeEventListener('resize',resize)};
 },[open]);
 return <>
  <div className="trust-bar" role="note" dangerouslySetInnerHTML={{__html:template.querySelector('.trust-bar').innerHTML}}/>
  <header className="site-header" ref={siteHeader}><div className="head wrap">
   <a className="logo" href="/" aria-label="وی کلاب؛ خانه" dangerouslySetInnerHTML={{__html:header.querySelector('.logo').innerHTML}}/>
   <nav className="desktop-navigation" aria-label="منوی اصلی">{links.map(a=>a.href==='/shop/'?<details className="desktop-category-menu" key={a.href} onKeyDown={e=>{if(e.key==='Escape'){e.currentTarget.open=false;e.currentTarget.querySelector('summary').focus()}}}><summary>فروشگاه <span aria-hidden="true">⌄</span></summary><div className="desktop-category-panel"><a href="/shop/">همه محصولات ←</a>{categories.filter(c=>c.parent_id===null).map(c=><div key={c.id}><a href={c.url}>{c.name}</a>{categories.filter(child=>child.parent_id===c.id).map(child=><a key={child.id} href={child.url}>{child.name}</a>)}</div>)}</div></details>:<a key={a.href} href={a.href}>{a.label}</a>)}</nav>
   <a className="account-link" href="/account/" aria-label="حساب کاربری">{icon('M20 21v-2a7 7 0 0 0-14 0v2 M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0')}<span>حساب من</span></a>
   <a className="cart-button" href="/cart/" aria-label={'سبد خرید، '+count.toLocaleString('fa-IR')+' کالا'}>{icon('M3 5h2l2 11h12l2-8H6 M9 21h.01 M18 21h.01')}<span className="cart-label">سبد خرید</span><b id="cartCount">{count.toLocaleString('fa-IR')}</b></a>
   <button className="mobile-menu-button" ref={menuButton} type="button" aria-label={open?'بستن منو':'باز کردن منو'} aria-expanded={open} aria-controls="mobile-navigation" onClick={()=>setOpen(v=>!v)}>{icon(open?'M6 6l12 12 M6 18L18 6':'M4 6h16 M4 12h16 M4 18h16')}</button>
  </div><nav id="mobile-navigation" className="mobile-navigation" aria-label="منوی موبایل" hidden={!open}>
   <a href="/shop/">همه محصولات ←</a>{categories.filter(c=>c.parent_id===null).map(c=><a key={c.id} href={c.url}>{c.name}</a>)}
   {links.filter(a=>a.href!=='/shop/').map(a=><a key={a.href} href={a.href}>{a.label}</a>)}<a href="/account/">حساب کاربری</a>
  </nav></header>
  {children}
  <footer className="site-footer" dangerouslySetInnerHTML={{__html:template.querySelector('footer').innerHTML.replaceAll('/products/creatine-monohydrate/','/shop/creatine/')}}/>
 </>;
}
