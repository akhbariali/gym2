const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)],num=n=>n.toLocaleString('fa-IR');
const products=window.WHEY_PRODUCTS||[],site=window.WHEY_SITE||{};
const wheyTypes=['isolate','concentrate','blend'],typeLabels={isolate:'پروتئین وی ایزوله',concentrate:'پروتئین وی کنسانتره',blend:'پروتئین وی ترکیبی'};
const unitPrice=p=>p.servings?Math.round(p.price/p.servings/100)*100:0;
const normalize=s=>s.replace(/ي/g,'ی').replace(/ك/g,'ک').replace(/\u200c/g,' ').toLowerCase();
let tab='all',cart={};
try{const saved=JSON.parse(localStorage.getItem('wheyclub-cart')||'{}');for(const p of products)if(Number.isInteger(saved[p.id])&&saved[p.id]>0)cart[p.id]=Math.min(saved[p.id],99)}catch{}
function render(){
 if(!$('#grid'))return;
 const types=$$('input[name=type]:checked').map(x=>x.value),flavors=$$('input[name=flavor]:checked').map(x=>x.value),q=normalize($('#search')?.value.trim()||'');
 let list=products.filter(p=>wheyTypes.includes(p.type)&&(!types.length||types.includes(p.type))&&(!flavors.length||flavors.includes(p.flavor))&&p.price<=Number($('#price').value)&&normalize(p.name+' '+p.en).includes(q)&&(tab!=='popular'||p.popular)&&(tab!=='sale'||p.old));
 const sort=$('#sort').value;if(sort==='unit')list.sort((a,b)=>a.price/a.servings/a.protein-b.price/b.servings/b.protein);if(sort==='low')list.sort((a,b)=>a.price-b.price);if(sort==='high')list.sort((a,b)=>b.price-a.price);if(sort==='protein')list.sort((a,b)=>b.protein-a.protein);
 $('#priceValue').textContent=num(Number($('#price').value));$('#resultCount').textContent=num(list.length)+' محصول برای انتخاب شما';$('#empty').hidden=!!list.length;
 $('#grid').innerHTML=list.map(p=>`<article class="card"><a class="visual" href="/products/${p.slug}/" aria-label="مشاهده ${p.name}">${p.old?`<span class="badge">${num(Math.round((1-p.price/p.old)*100))}٪ تخفیف</span>`:p.popular?'<span class="badge neutral">انتخاب روزانه</span>':''}<img src="/assets/${p.color}.svg" alt="${p.name}" loading="lazy"></a><div class="info"><div class="brand">${typeLabels[p.type]||''}</div><a class="title" href="/products/${p.slug}/">${p.name}</a><div class="meta">${p.size} <span>·</span> طعم ${p.flavorName}</div><div class="unit-price">${num(p.protein)} گرم پروتئین · هر وعده ${num(unitPrice(p))} تومان</div><div class="card-bottom"><div class="price"><span class="old">${p.old?num(p.old):''}</span>${num(p.price)} <small>تومان</small></div><button class="add" data-add="${p.id}" aria-label="افزودن ${p.name} به سبد">+</button></div></div></article>`).join('');
}
function reset(){if(!$('#grid'))return;tab='all';$$('aside input[type=checkbox]').forEach(x=>x.checked=false);const initial=$('#products')?.dataset.initialType;if(initial){const input=$(`input[name=type][value=${initial}]`);if(input)input.checked=true;$$('input[name=type]').forEach(x=>x.disabled=true)}$('#price').value=4000000;if($('#search'))$('#search').value='';$('#sort').value='featured';$$('[data-tab]').forEach(x=>x.classList.toggle('selected',x.dataset.tab==='all'));render()}
function updateCart(){
 const count=Object.values(cart).reduce((a,b)=>a+b,0);if($('#cartCount'))$('#cartCount').textContent=num(count);try{localStorage.setItem('wheyclub-cart',JSON.stringify(cart))}catch{}
 if(!$('#cartItems'))return;const items=products.filter(p=>cart[p.id]);
 $('#cartItems').innerHTML=items.length?items.map(p=>`<div class="cart-row"><a href="/products/${p.slug}/"><img src="/assets/${p.color}.svg" alt="${p.name}"></a><div><a href="/products/${p.slug}/"><h3>${p.name}</h3></a><p>${num(p.price)} تومان · ${p.size}</p></div><div class="quantity"><button data-change="${p.id}" data-delta="-1" aria-label="کاهش تعداد">−</button><span>${num(cart[p.id])}</span><button data-change="${p.id}" data-delta="1" aria-label="افزایش تعداد">+</button></div></div>`).join(''):'<p class="cart-empty">سبدت منتظر اولین انتخابته.<br><a href="/shop/whey-protein/">بیا پروتئین مورد علاقه‌ات رو پیدا کنیم ←</a></p>';
 const total=items.reduce((s,p)=>s+p.price*cart[p.id],0),free=site.freeShipping||0,left=Math.max(0,free-total);
 $('#cartSummary').innerHTML=items.length?`${free?`<div class="ship-progress"><p>${left?`فقط ${num(left)} تومان تا <b>ارسال رایگان</b>`:'<b>ارسال رایگان</b> برای این سفارش فعال شد ✓'}</p><span style="--fill:${Math.min(100,Math.round(total/free*100))}%"></span></div>`:''}<div class="total"><span>جمع سبد خرید</span><span>${num(total)} تومان</span></div><ul class="cart-trust"><li>ضمانت اصالت کالا</li><li>۷ روز ضمانت بازگشت</li><li>پرداخت امن بانکی</li></ul><div class="checkout-note">نسخه نمایشی: پرداخت و ثبت سفارش واقعی هنوز فعال نیست.</div><a href="/checkout/" class="checkout-link">ادامه خرید و انتخاب نشانی ←</a>`:'';
}
let toastTimer;
function toast(text){if(!$('#toast'))return;$('#toast').textContent=text;$('#toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').classList.remove('show'),2200)}
function addKit(ids){const valid=ids.filter(id=>products.some(p=>p.id===id));for(const id of valid)cart[id]=Math.min((cart[id]||0)+1,99);if(!valid.length)return;updateCart();toast('کل کیت به سبدت اضافه شد ✓')}
function add(id){if(!products.some(p=>p.id===id))return;cart[id]=Math.min((cart[id]||0)+1,99);updateCart();toast('به سبد خریدت اضافه شد ✓')}
document.addEventListener('click',e=>{
 const k=e.target.closest('[data-add-kit]');if(k)addKit(k.dataset.addKit.split(',').map(Number));
 const a=e.target.closest('[data-add]'),c=e.target.closest('[data-change]'),t=e.target.closest('[data-tab]');
 if(a)add(Number(a.dataset.add));
 if(c){const id=c.dataset.change;if(!cart[id])return;cart[id]=Math.max(0,Math.min(99,cart[id]+Number(c.dataset.delta)));if(!cart[id])delete cart[id];updateCart()}
 if(t){tab=t.dataset.tab;$$('[data-tab]').forEach(x=>x.classList.toggle('selected',x===t));render()}
 if(e.target.closest('.close'))e.target.closest('dialog').close();
});
$('#search')?.addEventListener('input',render);$$('aside input').forEach(x=>x.addEventListener('input',render));$('#sort')?.addEventListener('change',render);if($('#reset'))$('#reset').onclick=reset;if($('#emptyReset'))$('#emptyReset').onclick=reset;
reset();updateCart();
// Only published summaries are exposed; never request the private article queue.
if($('#latestArticles'))fetch('/api/articles/',{cache:'no-cache'}).then(r=>{if(!r.ok)throw new Error('Journal not published');return r.json().then(data=>data.results.map(a=>({...a,url:"/blog/"+(a.url_slug||a.slug)+"/",description:a.meta_description})))}).then(items=>{const el=$('#latestArticles');if(!items.length)return;const safe=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));el.innerHTML=items.slice(0,3).map(a=>`<a class="editorial-card" href="${safe(a.url)}"><div class="editorial-art art-${Number(a.id)%4}"><span>WHEY CLUB JOURNAL</span><b>${String(a.id).padStart(2,'0')}</b><i>↗</i></div><div class="editorial-body"><div class="article-category">${safe(a.category)}<span>حدود ۲ دقیقه مطالعه</span></div><h2>${safe(a.title)}</h2><p>${safe(a.description)}</p><div class="read-link"><span>مطالعه مقاله ←</span></div></div></a>`).join('')}).catch(()=>{});
