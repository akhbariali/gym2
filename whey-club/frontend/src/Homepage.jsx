import React,{useEffect,useRef,useState} from 'react';
import SiteLayout from './SiteLayout.jsx';
import LoadingPage from './LoadingPage.jsx';
import QuantityControl from './QuantityControl.jsx';
import './homepage-store.css';

const money=value=>Number(value).toLocaleString('fa-IR');
const brandAssets={
 'FA Nutrition':{name:'FA NUTRITION',file:'fa.png'},
 'Zoomad Labs':{name:'ZOOMAD LABS',file:null},
 'TruFuel':{name:'TRUFUEL',file:'trufuel.png',dark:true},
 'Cellucor':{name:'CELLUCOR',file:null},
 'Weider':{name:'WEIDER',file:'weider.png'},
 'Nutrend':{name:'NUTREND',file:'nutrend.svg',dark:true},
 'ALLMAX':{name:'ALLMAX',file:'allmax.png'},
 'Allmax':{name:'ALLMAX',file:'allmax.png'},
 'MuscleTech':{name:'MUSCLETECH',file:'muscletech.png'},
};
function BrandLogo({brand}){
 const asset=brandAssets[brand];
 const [failed,setFailed]=useState(false);
 return asset?.file&&!failed?<img className={asset.dark?'brand-logo-light':''} src={'/assets/brands/'+asset.file} alt={brand} loading="lazy" onError={()=>setFailed(true)}/>:<span className="brand-name" dir="ltr">{asset?.name||brand}</span>;
}
const weight=p=>Number(p.size?.replace(/[۰-۹]/g,c=>'۰۱۲۳۴۵۶۷۸۹'.indexOf(c)).match(/\d+/)?.[0]||0);
export default function Homepage(){
 const [products,setProducts]=useState(null),[error,setError]=useState(''),[brand,setBrand]=useState('all'),[group,setGroup]=useState('all'),[sort,setSort]=useState('featured'),[articles,setArticles]=useState([]);
 const productSection=useRef(null);
 useEffect(()=>{
  const controller=new AbortController();
  document.title='وی کلاب | کراتین‌های موجود، برندهای معتبر، انتخاب آگاهانه';
  document.body.className='store-home';
  fetch('/api/products/',{signal:controller.signal,cache:'no-cache'}).then(r=>{if(!r.ok)throw Error('دریافت محصولات ممکن نشد. دوباره تلاش کنید.');return r.json()}).then(d=>setProducts(d.results.filter(p=>!p.is_demo))).catch(e=>{if(e.name!=='AbortError')setError(e.message)});
  fetch('/api/articles/',{signal:controller.signal}).then(r=>r.ok?r.json():{results:[]}).then(d=>setArticles(d.results.slice(0,3))).catch(()=>{});
  return()=>controller.abort();
 },[]);
 function selectBrand(value,kind='all'){
  setBrand(value);setGroup(kind);
  productSection.current?.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});
 }
 if(error)return <SiteLayout><main className="wrap landing-error"><h1>ارتباط با فروشگاه برقرار نشد.</h1><p role="alert">{error}</p><button className="landing-button" onClick={()=>location.reload()}>تلاش دوباره</button></main></SiteLayout>;
 if(!products)return <SiteLayout><LoadingPage label="در حال آماده‌سازی فروشگاه…"/></SiteLayout>;
 const brands=[...new Set(products.map(p=>p.brand))];
 const find=slug=>products.find(p=>p.slug===slug);
 const hero=[find('muscletech-platinum-creatine-450g'),find('fa-ice-creatine-300g'),find('zoomad-one-raw-creatine-strawberry-300g')].filter(Boolean);
 let visible=products.filter(p=>(brand==='all'||p.brand===brand)&&(group!=='large'||weight(p)>=400));
 visible=[...visible].sort((a,b)=>sort==='low'?a.price-b.price:sort==='high'?b.price-a.price:products.indexOf(a)-products.indexOf(b));
 const large=products.find(p=>weight(p)>=400);
 const flavored=find('fa-ice-creatine-300g');
 return <SiteLayout><main className="landing-store">
  <div className="landing-quicklinks wrap" aria-label="بخش‌های فروشگاه"><a href="#landing-products">خرید کراتین</a><a href="#landing-brands">خرید بر اساس برند</a><a href="/health-calculator/">ماشین حساب سلامت</a><a href="/blog/">مجله وی کلاب</a></div>
  <section className="landing-hero" aria-labelledby="landing-title"><div className="landing-hero-inner wrap">
   <div className="landing-hero-copy"><span className="landing-eyebrow" dir="ltr">THE CREATINE EDIT / WHEYCLUB</span><h1 id="landing-title">برای ست بعدی،<br/><em>آماده‌تر باش.</em></h1><p>کراتین‌های موجود را از برندهای مختلف ببین؛ وزن، طعم و قیمت را مقایسه کن و انتخاب خودت را بساز.</p><div className="landing-hero-actions"><a className="landing-button" href="#landing-products">مشاهده کراتین‌ها <span aria-hidden="true">↙</span></a><a className="landing-simple-link" href="#landing-brands">برندها را ببین ←</a></div><span className="landing-hero-note">{money(products.length)} کراتین · از {money(brands.length)} برند</span></div>
   <div className="landing-hero-art"><span className="landing-art-word" aria-hidden="true">CREATINE</span><div className="landing-hero-products">{hero.map((p,index)=><a className={'landing-hero-item hero-item-'+index} key={p.id} href={'/products/'+p.slug+'/'} aria-label={p.name}><img src={p.image_url} alt={p.name} fetchPriority={index===1?'high':'auto'}/></a>)}</div><div className="landing-art-caption"><span dir="ltr">YOUR BRAND. YOUR ROUTINE.</span><span>مونوهیدرات، با انتخاب تو.</span></div></div>
  </div></section>
  <div className="landing-benefits wrap"><div><span aria-hidden="true">↗</span><p><b>ارسال به انتخاب تو</b><small>پست پیشتاز یا تیپاکس</small></p></div><div><span aria-hidden="true">≋</span><p><b>مقایسه قبل از خرید</b><small>برند، وزن و مشخصات روشن</small></p></div><div><span aria-hidden="true">↻</span><p><b>قیمت به‌روز</b><small>مبلغ نهایی در صفحه محصول</small></p></div></div>
  <section id="landing-brands" className="landing-section wrap"><div className="landing-section-heading"><div><span className="landing-eyebrow" dir="ltr">SHOP BY BRAND</span><h2>برندت را پیدا کن.</h2></div><span className="landing-muted">برندهای موجود در وی کلاب</span></div><div className="landing-brand-grid">{brands.map(name=><button key={name} className={brandAssets[name]?.dark?'brand-tile brand-tile-dark':'brand-tile'} type="button" onClick={()=>selectBrand(name)} aria-label={'نمایش محصولات '+name}><BrandLogo brand={name}/></button>)}</div></section>
  <section id="landing-products" className="landing-section wrap" ref={productSection}><div className="landing-section-heading"><div><span className="landing-eyebrow" dir="ltr">FIND YOUR NEXT FAVOURITE</span><h2>{brand==='all'?'کراتین‌های موجود':brand}</h2></div><a className="landing-simple-link" href="/shop/creatine/">همه محصولات ←</a></div><div className="landing-product-tools"><div className="landing-filter-status"><button type="button" aria-pressed={brand==='all'&&group==='all'} onClick={()=>{setBrand('all');setGroup('all')}}>همه برندها</button>{(brand!=='all'||group!=='all')&&<span>{group==='large'?'بسته‌های ۴۰۰ گرم به بالا':brand} <button type="button" aria-label="حذف فیلتر برند" onClick={()=>{setBrand('all');setGroup('all')}}>×</button></span>}<small role="status">{money(visible.length)} محصول</small></div><label>مرتب‌سازی<select value={sort} onChange={e=>setSort(e.target.value)}><option value="featured">پیشنهاد فروشگاه</option><option value="low">ارزان‌ترین</option><option value="high">گران‌ترین</option></select></label></div>
   <div className="landing-product-grid">{visible.map(p=><article className="landing-product-card" key={p.id}><a className="landing-product-image" href={'/products/'+p.slug+'/'}><span>{p.available?'موجود':'ناموجود'}</span><img src={p.image_url||'/assets/'+p.color+'.svg'} alt={p.name} loading="lazy"/></a><div className="landing-card-copy"><span className="landing-card-brand" dir="auto">{p.brand}</span><h3><a href={'/products/'+p.slug+'/'}>{p.name}</a></h3><p>{p.size} · {p.flavorName}</p><div className="landing-card-price">{money(p.price)} <small>تومان</small></div><div className="landing-card-actions"><QuantityControl product={p}/><a href={'/products/'+p.slug+'/'}>جزئیات ←</a></div></div></article>)}</div>{!visible.length&&<p>محصولی با این مشخصات موجود نیست.</p>}
  </section>
  <section className="landing-editorial wrap" aria-label="انتخاب کراتین">{flavored&&<article className="landing-promo landing-promo-lime"><div><span className="landing-eyebrow" dir="ltr">A FRESH ADDITION</span><h2>یک انتخاب<br/>طعم‌دار.</h2><p>آیس اف‌ای؛ کراتین مونوهیدرات در بسته ۳۰۰ گرمی.</p><a className="landing-button" href={'/products/'+flavored.slug+'/'}>مشاهده آیس اف‌ای ←</a></div><img src={flavored.image_url} alt={flavored.name} loading="lazy"/></article>}{large&&<article className="landing-promo landing-promo-sand"><div><span className="landing-eyebrow" dir="ltr">GO A LITTLE BIGGER</span><h2>بسته‌های<br/>بزرگ‌تر را ببین.</h2><p>گزینه‌های ۴۰۰ و ۴۵۰ گرمی را کنار هم مقایسه کن.</p><button className="landing-button" onClick={()=>selectBrand('all','large')}>مقایسه بسته‌ها ←</button></div><img src={large.image_url} alt={large.name} loading="lazy"/></article>}</section>
  <section className="landing-guide wrap"><div><span className="landing-eyebrow" dir="ltr">KNOW YOUR NEEDS</span><h2>انتخاب خوب،<br/>از شناخت شروع می‌شود.</h2><p>نیاز روزانه‌ات را بهتر بشناس و راهنماها را قبل از انتخاب مکمل بخوان.</p></div><a href="/health-calculator/"><span aria-hidden="true">↗</span><strong>ماشین حساب سلامت</strong><p>برآورد کالری و پروتئین روزانه</p></a><a href="/start/#supplements"><span aria-hidden="true">↗</span><strong>از کجا شروع کنم؟</strong><p>نقش تغذیه، تمرین و مکمل</p></a></section>
  {articles.length>0&&<section className="landing-section landing-journal wrap"><div className="landing-section-heading"><div><span className="landing-eyebrow" dir="ltr">THE WHEYCLUB JOURNAL</span><h2>قبل از انتخاب، بخوان.</h2></div><a className="landing-simple-link" href="/blog/">همه مقاله‌ها ←</a></div><div className="landing-journal-grid">{articles.map((a,index)=><a key={a.slug} href={'/blog/'+(a.url_slug||a.slug)+'/'}><span className="landing-article-number" aria-hidden="true">0{index+1}</span><small>{a.category}</small><h3>{a.title}</h3><p>{a.meta_description}</p><span>مطالعه مقاله ←</span></a>)}</div></section>}
  <section className="landing-faq wrap"><h2>پیش از خرید بدان.</h2><div><details><summary>هزینه ارسال چطور محاسبه می‌شود؟</summary><p>هزینه پست پیشتاز بر اساس وزن بسته و مقصد به مبلغ خرید اضافه می‌شود. هزینه حمل تیپاکس را گیرنده پرداخت می‌کند.</p></details><details><summary>آیا پرداخت آنلاین فعال است؟</summary><p>درگاه پرداخت هنوز فعال نیست. می‌توانی محصولات و سبد خرید را بررسی کنی، اما در این مرحله مبلغی دریافت نمی‌شود.</p></details></div></section>
 </main></SiteLayout>;
}
