import React,{useEffect,useState} from 'react';
import {createPortal} from 'react-dom';
import './categories.css';
export default function CategoryMenu(){
 const [mount,setMount]=useState(null),[categories,setCategories]=useState([]),[open,setOpen]=useState(false);
 useEffect(()=>{const link=document.querySelector('header nav a[href="/shop/"]');if(!link)return;const el=document.createElement('span');el.className='category-menu-mount';link.replaceWith(el);setMount(el);fetch('/api/categories/',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error();return r.json()}).then(d=>setCategories(d.results)).catch(()=>{});const close=e=>{if(!el.contains(e.target))setOpen(false)};document.addEventListener('pointerdown',close);return()=>{document.removeEventListener('pointerdown',close);el.replaceWith(link)}},[]);
 if(!mount)return null;
 const branch=(parent)=>categories.filter(c=>c.parent_id===parent).map(c=><li key={c.id}><a href={c.url}>{c.name}</a>{categories.some(x=>x.parent_id===c.id)&&<ul>{branch(c.id)}</ul>}</li>);
 return createPortal(<div className="category-hover-menu" onPointerEnter={e=>{if(e.pointerType==='mouse')setOpen(true)}} onPointerLeave={e=>{if(e.pointerType==='mouse')setOpen(false)}} onBlur={e=>{if(!e.currentTarget.contains(e.relatedTarget))setOpen(false)}} onKeyDown={e=>{if(e.key==='Escape'){setOpen(false);e.currentTarget.querySelector('button').focus()}}}>
  <button type="button" aria-expanded={open} aria-controls="shop-category-menu" onClick={e=>setOpen(v=>e.nativeEvent.pointerType==='mouse'?true:!v)}>فروشگاه</button>
  <nav id="shop-category-menu" className="category-popover" aria-label="دسته‌های محصولات" hidden={!open}><a className="category-all" href="/shop/">همه محصولات ←</a><ul className="category-tree">{branch(null)}</ul>{!categories.length&&<p><a href="/shop/">مشاهده محصولات ←</a></p>}</nav>
 </div>,mount);
}
