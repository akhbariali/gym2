import React,{useEffect,useRef,useState} from 'react';
import SiteLayout from './SiteLayout.jsx';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../public/luxe.css';
import './account.css';

async function request(path,body){
 let token;
 if(body!==undefined){const r=await fetch('/api/account/session/');if(!r.ok)throw new Error('ارتباط با فروشگاه برقرار نشد.');token=(await r.json()).csrfToken}
 const response=await fetch(path,{method:body===undefined?'GET':'POST',credentials:'same-origin',headers:body===undefined?{}:{'Content-Type':'application/json','X-CSRFToken':token},body:body===undefined?undefined:JSON.stringify(body)});
 let data;try{data=await response.json()}catch{throw new Error(response.status===403?'درخواست امنیتی معتبر نیست؛ صفحه را تازه‌سازی و دوباره تلاش کنید.':'ارتباط با فروشگاه برقرار نشد. دوباره تلاش کنید.')}if(!response.ok)throw new Error(data.error||'درخواست انجام نشد. دوباره تلاش کنید.');return data;
}
function PinMap({onChange}){
 const el=useRef(null);
 useEffect(()=>{const map=L.map(el.current).setView([35.6892,51.389],11);L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(map);let marker;
 const update=pos=>{onChange({latitude:pos.lat,longitude:pos.lng})};
 map.on('click',e=>{if(marker)marker.setLatLng(e.latlng);else{marker=L.marker(e.latlng,{draggable:true,icon:L.divIcon({className:'address-map-pin',html:'●',iconSize:[28,28],iconAnchor:[14,14]})}).addTo(map);marker.on('dragend',()=>update(marker.getLatLng()))}update(e.latlng)});
 return()=>map.remove();},[]);
 return <div ref={el} className="address-map" aria-label="برای انتخاب موقعیت روی نقشه کلیک کنید"/>;
}
const backLink=<a className="auth-back" href="/"><span dir="ltr">WHEY<span>CLUB</span></span><span>بازگشت به فروشگاه ←</span></a>;
function Shell({children,checkout=false}){return <SiteLayout textWordmark={checkout}><div className={checkout?undefined:"auth-page account-page"}><main className="wrap account-main">{!checkout&&backLink}{children}</main></div></SiteLayout>}
export default function Account(){
 const [session,setSession]=useState(null),[error,setError]=useState(''),[busy,setBusy]=useState(false),[addresses,setAddresses]=useState([]),[mapOpen,setMapOpen]=useState(false),[pin,setPin]=useState({latitude:null,longitude:null}),[notice,setNotice]=useState(''),[chosen,setChosen]=useState(''),[products,setProducts]=useState([]),[draft,setDraft]=useState(null);
 const path=location.pathname,register=path.includes('/register'),auth=register||path.includes('/login'),checkout=path==='/checkout/';
 const next=new URLSearchParams(location.search).get('next')==='/checkout/'?'/checkout/':'/account/';
 useEffect(()=>{document.title=checkout?'تکمیل خرید | وی کلاب':register?'ثبت‌نام | وی کلاب':auth?'ورود | وی کلاب':'حساب کاربری | وی کلاب';request('/api/account/session/').then(setSession).catch(e=>setError(e.message));},[]);
 useEffect(()=>{if(session?.user){request('/api/account/addresses/').then(d=>{setAddresses(d.results);if(d.results.length)setChosen(String(d.results[0].id))}).catch(e=>setError(e.message));if(checkout)request('/api/products/').then(d=>setProducts(d.results)).catch(e=>setError(e.message))}},[session]);
 let cart={};try{cart=JSON.parse(localStorage.getItem('wheyclub-cart')||'{}')}catch{}
 const cartItems=products.filter(p=>Number.isInteger(cart?.[p.id])&&cart[p.id]>0).map(p=>({...p,quantity:cart[p.id]}));
 async function submitAuth(e){e.preventDefault();setError('');setBusy(true);const f=Object.fromEntries(new FormData(e.currentTarget));if(register&&f.password!==f.confirm){setError('تکرار رمز عبور یکسان نیست.');setBusy(false);return}try{await request('/api/account/'+(register?'register/':'login/'),f);location.assign(next)}catch(e){setError(e.message)}finally{setBusy(false)}}
 async function saveAddress(e){e.preventDefault();setError('');setBusy(true);const form=e.currentTarget;try{const saved=await request('/api/account/addresses/',{...Object.fromEntries(new FormData(form)),...pin});setAddresses(a=>[saved,...a]);setChosen(String(saved.id));setNotice('نشانی شما ذخیره شد.');form.reset();setMapOpen(false);setPin({latitude:null,longitude:null});setDraft(null)}catch(e){setError(e.message)}finally{setBusy(false)}}
 async function removeAddress(id){if(!window.confirm('این نشانی حذف شود؟'))return;setError('');try{await request('/api/account/addresses/'+id+'/delete/',{});setAddresses(a=>a.filter(x=>x.id!==id));if(chosen===String(id))setChosen('');setDraft(null)}catch(e){setError(e.message)}}
 async function prepare(){setBusy(true);setError('');try{let key=sessionStorage.getItem('whey-checkout-key');if(!key){key=typeof crypto.randomUUID==='function'?crypto.randomUUID():'checkout-'+Date.now()+'-'+Math.random().toString(36).slice(2);sessionStorage.setItem('whey-checkout-key',key)}const data=await request('/api/checkout/',{key,address_id:Number(chosen),items:cartItems.map(p=>({id:p.id,quantity:p.quantity}))});setDraft(data);if(data.payment_available&&data.payment_url)location.assign(data.payment_url)}catch(e){setError(e.message);sessionStorage.removeItem('whey-checkout-key')}finally{setBusy(false)}}
 const addressForm=<section className="account-panel"><div className="kicker">DELIVER TO YOUR DOOR</div><h2>نشانی جدید</h2><p className="account-muted">برای ارسال، نشانی کامل شامل خیابان، کوچه، پلاک و واحد را وارد کنید.</p><form onSubmit={saveAddress} className="account-form address-form">{[['recipient','نام گیرنده','text',120],['phone','شماره موبایل گیرنده','tel',11],['province','استان','text',80],['city','شهر','text',80],['postal_code','کد پستی ۱۰ رقمی','text',10]].map(([name,label,type,max])=><label key={name}>{label}<input name={name} type={type} maxLength={max} required autoComplete={{recipient:'name',phone:'tel',province:'address-level1',city:'address-level2',postal_code:'postal-code'}[name]} inputMode={['phone','postal_code'].includes(name)?'numeric':undefined}/></label>)}<label className="wide">نشانی کامل<textarea name="street" maxLength={500} rows={3} required autoComplete="street-address"/></label><div className="wide map-options"><b>موقعیت روی نقشه (اختیاری)</b><p>نشانی نوشتاری کافی است. با باز کردن نقشه، نقشه‌های OpenStreetMap بارگذاری می‌شوند و محدوده نقشه برای آن سرویس ارسال می‌شود. موقعیت دستگاه شما خودکار خوانده نمی‌شود.</p>{!mapOpen?<button type="button" className="secondary" onClick={()=>setMapOpen(true)}>انتخاب موقعیت روی نقشه</button>:<><PinMap onChange={setPin}/><p>با جابه‌جایی نقشه، محل را پیدا و روی آن کلیک کنید؛ نشانگر قابل کشیدن است.</p>{pin.latitude!==null&&<p role="status">نقطه انتخاب شد: {pin.latitude.toFixed(5)}، {pin.longitude.toFixed(5)}</p>}<button type="button" className="secondary" onClick={()=>{setMapOpen(false);setPin({latitude:null,longitude:null})}}>حذف موقعیت و بستن نقشه</button></>}</div><button className="primary" disabled={busy}>ذخیره نشانی</button></form></section>;
 if(location.protocol!=='https:'&&!['localhost','127.0.0.1','[::1]'].includes(location.hostname))return <Shell checkout={checkout}><section className="account-intro"><h1>حساب امن، خرید مطمئن.</h1><p>ثبت‌نام، ورود، نشانی‌ها و تکمیل خرید آماده‌اند؛ برای حفظ امنیت اطلاعات شما، استفاده از آن‌ها پس از اتصال دامنه و فعال‌شدن HTTPS ممکن می‌شود.</p><a className="primary" href="/shop/whey-protein/">ادامه مشاهده محصولات ←</a></section></Shell>;
 if(auth)return <div className="auth-page">
  <main className="auth-main wrap">
   {backLink}
   <div className="auth-layout">
    <section className="auth-card" aria-labelledby="auth-title">
     <nav className="auth-tabs" aria-label="ورود یا ثبت‌نام">
      <a href={'/account/login/?next='+encodeURIComponent(next)} aria-current={!register?'page':undefined}>ورود به حساب</a>
      <a href={'/account/register/?next='+encodeURIComponent(next)} aria-current={register?'page':undefined}>ساخت حساب</a>
     </nav>
     <div className="auth-heading"><span className="auth-eyebrow">حساب کاربری وی کلاب</span><h1 id="auth-title">{register?'از اینجا شروع کنیم.':'خوش برگشتید.'}</h1><p>{register?'حساب بسازید تا نشانی‌ها و اطلاعات خریدتان یک‌جا در دسترس باشد.':'برای دسترسی به حساب و نشانی‌های خود وارد شوید.'}</p></div>
     {error&&<p className="account-error" role="alert">{error}</p>}
     {!session&&!error?<p role="status">در حال بارگذاری…</p>:<form className="account-form auth-form" onSubmit={submitAuth} aria-busy={busy}>
      {register&&<label>نام و نام خانوادگی<input name="name" required maxLength={120} autoComplete="name" placeholder="نام کامل شما"/></label>}
      <label>ایمیل<input name="email" type="email" required maxLength={150} autoComplete="username" dir="ltr" placeholder="you@example.com" autoCapitalize="none" spellCheck={false}/></label>
      <label>رمز عبور<input name="password" type="password" minLength={register?10:1} maxLength={128} required autoComplete={register?'new-password':'current-password'} dir="ltr" aria-describedby={register?'password-hint':undefined}/></label>
      {register&&<><label>تکرار رمز عبور<input name="confirm" type="password" minLength={10} required autoComplete="new-password" dir="ltr"/></label><p id="password-hint" className="auth-hint">حداقل ۱۰ کاراکتر؛ از رمز رایج یا فقط عدد استفاده نکنید.</p></>}
      <button type="submit" className="primary auth-submit" disabled={busy}>{busy?'در حال انجام…':register?'ساخت حساب':'ورود به حساب'}<span aria-hidden="true">←</span></button>
      {register&&<p className="auth-privacy">نام، ایمیل و نشانی‌های شما برای مدیریت حساب و ارسال ذخیره می‌شوند. ایمیل در این مرحله تأیید نمی‌شود.</p>}
     </form>}
     <p className="auth-switch">{register?'قبلاً حساب ساخته‌اید؟':'هنوز حساب ندارید؟'} <a href={'/account/'+(register?'login/':'register/')+'?next='+encodeURIComponent(next)}>{register?'وارد شوید':'ثبت‌نام کنید'} <span aria-hidden="true">←</span></a></p>
    </section>
    <aside className="auth-story" aria-label="درباره وی کلاب">
     <span className="auth-story-label" dir="ltr">WHEYCLUB / NUTRITION & WELLNESS</span>
     <div className="auth-story-copy"><p className="auth-slogan" dir="ltr">One more<br/><em>set.</em></p><h2>هر قدم، آگاهانه‌تر.</h2><p>اطلاعات روشن، انتخاب‌های سنجیده و همراهی در مسیر تغذیه و تمرین شما.</p></div>
     <div className="auth-principles"><span>شناخت بهتر</span><span>انتخاب آگاهانه</span><span>پیشرفت پیوسته</span></div>
    </aside>
   </div>
  </main>
 </div>;
 return <Shell checkout={checkout}><div className="account-intro"><div className="kicker">YOUR WHEY CLUB</div><h1>{checkout?'یک قدم تا تکمیل خرید.':register?'به وی کلاب خوش اومدی!':auth?'خوش برگشتی!':'حساب من، انتخاب‌های من.'}</h1><p>{checkout?'اول نشانی ارسال، بعد پرداخت امن؛ وقتی درگاه آماده شد.':'حساب بساز، نشانی‌ات رو ذخیره کن و خرید بعدی رو ساده‌تر انجام بده.'}</p></div>{error&&<p className="account-error" role="alert">{error}</p>}{notice&&<p className="account-success" role="status">{notice}</p>}{!session&&!error?<p role="status">در حال بارگذاری…</p>:!session?.user?<section className="account-panel"><h2>ابتدا وارد حساب خود شوید</h2><p>نشانی‌های ارسال فقط در حساب خودتان نمایش داده می‌شوند.</p><a className="primary" href={'/account/login/?next='+encodeURIComponent(checkout?'/checkout/':'/account/')}>ورود یا ثبت‌نام ←</a></section>:<><div className="account-welcome"><span>{session.user.name}، خوش اومدی!</span><button onClick={async()=>{await request('/api/account/logout/',{});location.assign('/account/login/')}}>خروج از حساب</button></div>{checkout&&<section className="account-panel"><h2>مرور سبد خرید</h2>{cartItems.length?cartItems.map(p=><div className="checkout-line" key={p.id}><span>{p.name} × {p.quantity.toLocaleString('fa-IR')}</span><b>{(p.price*p.quantity).toLocaleString('fa-IR')} تومان</b></div>):<p>سبد خرید خالی است. <a href="/shop/whey-protein/">انتخاب پروتئین ←</a></p>}<p>جمع کالاها: <b>{cartItems.reduce((s,p)=>s+p.price*p.quantity,0).toLocaleString('fa-IR')} تومان</b></p><p className="account-muted">محصولات و قیمت‌ها نمونه‌اند. هزینه و روش ارسال هنوز نهایی نشده‌اند؛ مبلغ بالا فقط جمع کالاهاست.</p></section>}<section className="account-panel"><h2>{checkout?'نشانی ارسال را انتخاب کنید':'نشانی‌های من'}</h2>{addresses.length?addresses.map(a=><div className={'saved-address '+(chosen===String(a.id)?'chosen':'')} key={a.id}><label><input type="radio" name="address" checked={chosen===String(a.id)} onChange={()=>{setChosen(String(a.id));setDraft(null);sessionStorage.removeItem('whey-checkout-key')}}/><span><b>{a.recipient} · {a.city}</b><p>{a.province}، {a.street}</p><small>کد پستی: {a.postal_code} · موبایل: {a.phone}</small>{a.latitude!==null&&<p className="account-muted">موقعیت نقشه ذخیره شده است.</p>}</span></label><button className="delete-address" onClick={()=>removeAddress(a.id)}>حذف</button></div>):<p className="account-muted">هنوز نشانی‌ای ذخیره نکردی. اولین نشانی رو همین پایین اضافه کن.</p>}</section>{addressForm}{checkout?<section className="account-panel payment-pending"><h2>درگاه پرداخت به‌زودی</h2><p>هنوز به درگاه پرداخت متصل نیستیم. در حال حاضر هیچ مبلغی دریافت و هیچ سفارش نهایی ثبت نمی‌شود.</p><button className="primary" disabled={busy||!chosen||!cartItems.length} onClick={prepare}>{busy?'در حال بررسی…':'بررسی سبد و نشانی'}</button>{draft&&<div role="status" className="account-success"><b>پیش‌نویس خرید شماره {draft.id.toLocaleString('fa-IR')}</b><p>{draft.message}</p><p>جمع کالاها: {draft.total.toLocaleString('fa-IR')} تومان</p><button disabled className="secondary">پرداخت آنلاین — به‌زودی</button></div>}</section>:<a className="primary" href="/checkout/">ادامه به تکمیل خرید ←</a>}</>}</Shell>;
}
