import React,{useEffect,useState} from 'react';
import SiteLayout from './SiteLayout.jsx';
import QuantityControl from './QuantityControl.jsx';
import './product-page.css';
import LoadingPage from './LoadingPage.jsx';

const number=n=>Number(n).toLocaleString('fa-IR');
const categoryInfo={whey:['پروتئین وی','/shop/whey-protein/'],creatine:['کراتین','/shop/creatine/'],accessory:['لوازم جانبی','/shop/accessories/']};
const nutrients=[['scoop','اندازه وعده (گرم)'],['kcal','انرژی (کیلوکالری)'],['protein','پروتئین (گرم)'],['carbs','کربوهیدرات (گرم)'],['fat','چربی (گرم)'],['sugar','قند (گرم)'],['creatine','کراتین (گرم)']];

export default function ProductPage(){
 const [product,setProduct]=useState(null),[error,setError]=useState('');
 useEffect(()=>{
  const controller=new AbortController();
  const slug=location.pathname.split('/').filter(Boolean)[1];
  fetch('/api/products/'+encodeURIComponent(slug)+'/',{signal:controller.signal,cache:'no-cache'})
   .then(async r=>{if(!r.ok)throw new Error('محصول پیدا نشد یا دیگر در فروشگاه نمایش داده نمی‌شود.');return r.json()})
   .then(p=>{setProduct(p);document.title=p.name+' | وی کلاب'})
   .catch(e=>{if(e.name!=='AbortError')setError(e.message)});
  return()=>controller.abort();
 },[]);
 const [categoryName,categoryUrl]=categoryInfo[product?.category]||['فروشگاه','/shop/'];
 const nutrition=nutrients.filter(([key])=>typeof product?.nutrition?.[key]==='number');
 return <SiteLayout><main className="wrap route-main product-detail">
  {error?<section className="product-empty"><h1>{error}</h1><a href="/shop/">بازگشت به محصولات ←</a></section>:!product?<LoadingPage label="در حال بارگذاری محصول…"/>:<>
   <nav className="product-breadcrumbs" aria-label="مسیر صفحه"><a href="/">خانه</a><span>/</span><a href={categoryUrl}>{categoryName}</a><span>/</span><span aria-current="page">{product.name}</span></nav>
   <section className="product-overview" aria-labelledby="product-title">
    <div className="product-gallery"><span className="product-category-tag">{categoryName}</span><img src={product.image_url||'/assets/'+product.color+'.svg'} alt={product.name} fetchPriority="high"/><span className="product-image-caption">{product.brand} · {product.size}</span></div>
    <div className="product-summary">
     <div className="product-brand" dir="auto">{product.brand}</div>
     <h1 id="product-title">{product.name}</h1>
     <p className={'product-availability'+(!product.available?' unavailable':'')}><span aria-hidden="true"/>{product.available?'موجود در فروشگاه':'فعلاً ناموجود'}</p>
     <div className="product-package"><div><span>وزن / اندازه بسته</span><strong>{product.size}</strong></div><div><span>طعم</span><strong>{product.flavorName}</strong></div></div>
     {(product.servings>0||product.category==='whey')&&<div className="product-facts">{product.category==='whey'&&<span><b>{number(product.protein)}</b> گرم پروتئین در وعده</span>}{product.servings>0&&<span><b>{number(product.servings)}</b> وعده در بسته</span>}</div>}
     <div className="product-purchase"><div className="product-price-line"><span>قیمت محصول</span>{product.old>product.price&&<del>{number(product.old)} تومان</del>}</div><div className="product-current-price">{number(product.price)} <small>تومان</small></div><QuantityControl product={product} fullLabel/><a className="product-view-cart" href="/cart/">مشاهده سبد خرید ←</a></div>
     <div className="product-delivery"><span aria-hidden="true">↗</span><div><b>انتخاب روش ارسال در تکمیل خرید</b><p>پست پیشتاز با پرداخت هزینه ارسال همراه خرید؛ تیپاکس با پرداخت هزینه حمل توسط گیرنده.</p></div></div>
     <p className="product-payment-note">{product.is_demo&&'محصول آزمایشی؛ مشخصات و قیمت‌ها نمونه‌اند. '}درگاه پرداخت هنوز فعال نیست؛ در این مرحله پرداختی دریافت نمی‌شود.</p>
    </div>
   </section>
   <section className="product-information" aria-label="اطلاعات محصول"><div className="product-information-heading"><span dir="ltr">THE DETAILS</span><h2>بیشتر بشناس، بهتر انتخاب کن.</h2></div><div className="product-accordions">
    {product.description&&<details open><summary>درباره این محصول</summary><div className="product-detail-content"><p>{product.description}</p></div></details>}
    {nutrition.length>0&&product.category!=='accessory'&&<details><summary>اطلاعات تغذیه در هر وعده</summary><div className="product-detail-content"><dl className="product-nutrition">{nutrition.map(([key,label])=><div key={key}><dt>{label}</dt><dd>{number(product.nutrition[key])}</dd></div>)}</dl></div></details>}
    {product.ingredients&&<details><summary>ترکیبات و آلرژن‌ها</summary><div className="product-detail-content"><p>{product.ingredients}</p>{product.allergens&&<p><b>آلرژن‌ها: </b>{product.allergens}</p>}</div></details>}
    {product.usage&&<details><summary>روش مصرف روی برچسب</summary><div className="product-detail-content"><p>{product.usage}</p></div></details>}
    {(product.irc||product.batch||product.expiry)&&<details><summary>مشخصات روی بسته</summary><div className="product-detail-content">{product.irc&&<p>IRC: {product.irc}</p>}{product.batch&&<p>سری ساخت: {product.batch}</p>}{product.expiry&&<p>انقضا: {product.expiry}</p>}</div></details>}
   </div></section>
   <a className="product-back-category" href={categoryUrl}>مشاهده همه محصولات {categoryName} ←</a>
  </>}
 </main></SiteLayout>;
}
