import React,{useEffect,useState} from 'react';
import {createPortal} from 'react-dom';
export default function HomeCatalog({products}){
 const [mount,setMount]=useState(null);
 useEffect(()=>setMount(document.getElementById('homepage-products')),[]);
 if(!mount)return null;
 return createPortal(<div className="category-product-grid">{products.filter(p=>!p.is_demo).slice(0,3).map(p=><article className="category-product" key={p.id}><a href={'/products/'+p.slug+'/'}><img src={p.image_url||'/assets/'+p.color+'.svg'} alt={p.name} loading="lazy"/><h2>{p.name}</h2><p>{p.size}</p><strong>{p.price.toLocaleString('fa-IR')} تومان</strong><span className="home-product-link">مشاهده محصول ←</span></a></article>)}</div>,mount);
}
