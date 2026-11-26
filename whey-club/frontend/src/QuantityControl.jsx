import React,{useEffect,useState} from 'react';
import './quantity-control.css';

function readCart(){
 try{
  const cart=JSON.parse(localStorage.getItem('wheyclub-cart')||'{}');
  return cart&&typeof cart==='object'&&!Array.isArray(cart)?cart:{};
 }catch{return {}}
}

export default function QuantityControl({product,fullLabel=false}){
 const [cart,setCart]=useState(readCart),[error,setError]=useState('');
 useEffect(()=>{
  const sync=()=>setCart(readCart());
  window.addEventListener('whey-cart-change',sync);
  window.addEventListener('storage',sync);
  return()=>{window.removeEventListener('whey-cart-change',sync);window.removeEventListener('storage',sync)};
 },[]);
 const quantity=Number.isInteger(cart[product.id])&&cart[product.id]>0?cart[product.id]:0;
 const max=Number.isInteger(product.stock)?Math.min(product.stock,99):99;
 function change(delta){
  try{
   const next=readCart();
   const current=Number.isInteger(next[product.id])&&next[product.id]>0?next[product.id]:0;
   if(delta>0&&(!product.available||current>=max))return;
   const updated=Math.max(0,current+delta);
   if(updated)next[product.id]=updated;else delete next[product.id];
   localStorage.setItem('wheyclub-cart',JSON.stringify(next));
   setCart(next);setError('');
   window.dispatchEvent(new Event('whey-cart-change'));
  }catch{setError('ذخیره سبد خرید ممکن نشد.')}
 }
 return <div className="quantity-control-wrap">
  <div className={'quantity-control'+(quantity?' quantity-control-active':'')} role="group" aria-label={'تعداد '+product.name+' در سبد خرید'}>
   {quantity>0&&<><button type="button" onClick={()=>change(-1)} aria-label={(quantity===1?'حذف ':'کاهش تعداد ')+product.name}>{quantity===1?<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true"><path d="M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7M14 10v7"/></svg>:'−'}</button><output aria-live="polite" aria-label="تعداد در سبد خرید">{quantity.toLocaleString('fa-IR')}</output></>}
   <button type="button" disabled={!product.available||quantity>=max} onClick={()=>change(1)} aria-label={'افزودن '+product.name+' به سبد'}>{!product.available?'ناموجود':!quantity&&fullLabel?'افزودن به سبد خرید +':'+'}</button>
  </div>
  {error&&<span className="quantity-error" role="alert">{error}</span>}
 </div>;
}
