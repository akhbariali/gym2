import React,{useEffect,useState} from 'react';
import SiteLayout from './SiteLayout.jsx';
import './categories.css';
import LoadingPage from './LoadingPage.jsx';
const money=n=>Number(n).toLocaleString('fa-IR');
export default function ShopPage(){
 const [data,setData]=useState(null),[error,setError]=useState(''),[query,setQuery]=useState(''),[sort,setSort]=useState('featured'),[notice,setNotice]=useState('');
 useEffect(()=>{Promise.all(['/api/categories/','/api/products/'].map(url=>fetch(url,{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error('دریافت اطلاعات فروشگاه ممکن نشد');return r.json()}))).then(([categories,products])=>setData({categories:categories.results,products:products.results})).catch(e=>setError(e.message))},[]);
 const path=location.pathname.replace(/\/?$/,'/');
 const category=data?.categories.find(c=>c.url===path);
 const invalid=data&&path!=='/shop/'&&!category;
 const title=category?.name||'همه محصولات';
 useEffect(()=>{if(data){document.title=title+' | وی کلاب';let canonical=document.querySelector('link[rel=canonical]');if(!canonical){canonical=document.createElement('link');canonical.rel='canonical';document.head.append(canonical)}canonical.href=location.origin+path}},[data,title,path]);
 if(error||invalid)return <SiteLayout><main className="wrap route-main"><h1>{error||'دسته پیدا نشد'}</h1><a href="/shop/">همه محصولات</a></main></SiteLayout>;
 if(!data)return <SiteLayout><LoadingPage label="در حال بارگذاری محصولات…"/></SiteLayout>;
 const chain=[];let node=category;while(node){chain.unshift(node);node=data.categories.find(c=>c.id===node.parent_id)}
 const ids=new Set(category?[category.id]:data.categories.map(c=>c.id));let changed=true;while(changed){changed=false;for(const c of data.categories)if(ids.has(c.parent_id)&&!ids.has(c.id)){ids.add(c.id);changed=true}}
 let products=data.products.filter(p=>!p.is_demo&&(!category||ids.has(p.category_id))&&p.name.includes(query.trim()));
 products=[...products].sort((a,b)=>sort==='low'?a.price-b.price:sort==='high'?b.price-a.price:a.id-b.id);
 function add(p){try{const cart=JSON.parse(localStorage.getItem('wheyclub-cart')||'{}');const quantity=Number.isInteger(cart[p.id])?cart[p.id]:0;const max=Number.isInteger(p.stock)?Math.min(p.stock,99):99;if(quantity>=max){setNotice('بیشتر از موجودی قابل انتخاب نیست.');return}cart[p.id]=quantity+1;localStorage.setItem('wheyclub-cart',JSON.stringify(cart));setNotice(p.name+' به سبد خرید اضافه شد.');window.dispatchEvent(new Event('whey-cart-change'))}catch{setNotice('ذخیره سبد خرید ممکن نشد.')}}
 const categoryBranch=parent=>data.categories.filter(c=>c.parent_id===parent).map(c=><li key={c.id}><a href={c.url} aria-current={c.id===category?.id?'page':undefined}>{c.name}</a>{data.categories.some(x=>x.parent_id===c.id)&&<ul>{categoryBranch(c.id)}</ul>}</li>);
 return <SiteLayout><main className="wrap category-shop"><nav className="breadcrumbs" aria-label="مسیر دسته"><a href="/shop/">همه محصولات</a>{chain.map(c=><React.Fragment key={c.id}><span aria-hidden="true"> / </span><a href={c.url} aria-current={c.id===category?.id?'page':undefined}>{c.name}</a></React.Fragment>)}</nav><h1>{title}</h1><div className="category-shop-layout"><aside className="shop-category-nav"><h2>دسته‌های محصولات</h2><a href="/shop/" aria-current={!category?'page':undefined}>همه محصولات</a><ul>{categoryBranch(null)}</ul></aside><section className="category-products" aria-label={title}><div className="category-children">{data.categories.filter(c=>c.parent_id===(category?.id??null)).map(c=><a key={c.id} href={c.url}>{c.name} ←</a>)}</div><div className="category-tools"><label>جستجو در این دسته<input type="search" value={query} onChange={e=>setQuery(e.target.value)}/></label><label>مرتب‌سازی<select value={sort} onChange={e=>setSort(e.target.value)}><option value="featured">پیشنهاد ما</option><option value="low">ارزان‌ترین</option><option value="high">گران‌ترین</option></select></label></div><p role="status">{money(products.length)} محصول</p><div className="category-product-grid">{products.map(p=><article className="category-product" key={p.id}><a href={'/products/'+p.slug+'/'}><img src={p.image_url||'/assets/'+p.color+'.svg'} alt={p.name} loading="lazy"/><h2>{p.name}</h2></a><p>{p.size}</p><div><strong>{money(p.price)} تومان</strong><button type="button" disabled={!p.available} onClick={()=>add(p)} aria-label={'افزودن '+p.name+' به سبد'}>{p.available?'+':'ناموجود'}</button></div></article>)}</div>{!products.length&&<p>محصولی با این مشخصات یافت نشد.</p>}<p role="status">{notice}</p></section></div></main></SiteLayout>;
}
