import React,{useEffect} from 'react';
import CategoryMenu from './CategoryMenu.jsx';
import homepage from './pages/index.html?raw';
import '../public/luxe.css';

const template = new DOMParser().parseFromString(homepage, 'text/html');
const header = template.querySelector('header');
header.querySelector('.cart-button').insertAdjacentHTML('beforebegin', '<a class="account-link" href="/account/">ورود / حساب من</a>');
const textHeader = header.cloneNode(true);
textHeader.querySelector('.logo').outerHTML = '<a class="logo" href="/">WHEY CLUB</a>';

export default function SiteLayout({children, textWordmark=false}) {
 useEffect(()=>{const update=()=>{try{const count=Object.values(JSON.parse(localStorage.getItem('wheyclub-cart')||'{}')).filter(n=>Number.isInteger(n)&&n>0&&n<=99).reduce((a,b)=>a+b,0);const badge=document.querySelector('#cartCount');if(badge)badge.textContent=count.toLocaleString('fa-IR')}catch{}};update();window.addEventListener('whey-cart-change',update);return()=>window.removeEventListener('whey-cart-change',update)});
 return <>
  <div className="trust-bar" role="note" dangerouslySetInnerHTML={{__html: template.querySelector('.trust-bar').innerHTML}}/>
  <header dangerouslySetInnerHTML={{__html: (textWordmark ? textHeader : header).innerHTML}}/>
  <CategoryMenu/>
  {children}
  <footer className="site-footer" dangerouslySetInnerHTML={{__html: template.querySelector('footer').innerHTML}}/>
 </>;
}
