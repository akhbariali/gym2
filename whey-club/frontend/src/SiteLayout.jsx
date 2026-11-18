import React from 'react';
import homepage from './pages/index.html?raw';
import '../public/luxe.css';

const template = new DOMParser().parseFromString(homepage, 'text/html');
const header = template.querySelector('header');
header.querySelector('.cart-button').insertAdjacentHTML('beforebegin', '<a class="account-link" href="/account/">ورود / حساب من</a>');

export default function SiteLayout({children}) {
 let count = 0;
 try {
  count = Object.values(JSON.parse(localStorage.getItem('wheyclub-cart') || '{}')).filter(n => Number.isInteger(n) && n > 0 && n <= 99).reduce((sum, n) => sum + n, 0);
 } catch {}
 header.querySelector('#cartCount').textContent = count.toLocaleString('fa-IR');
 return <>
  <div className="trust-bar" role="note" dangerouslySetInnerHTML={{__html: template.querySelector('.trust-bar').innerHTML}}/>
  <header dangerouslySetInnerHTML={{__html: header.innerHTML}}/>
  {children}
  <footer className="site-footer" dangerouslySetInnerHTML={{__html: template.querySelector('footer').innerHTML}}/>
 </>;
}
