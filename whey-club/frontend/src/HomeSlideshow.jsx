import React, {useEffect, useState} from 'react';
import {createPortal} from 'react-dom';
import './home-slideshow.css';

// Supply image URLs and descriptive alt text here when the final banners arrive.
const slides = [
  {title:'پروتئین وی، برای مسیر تو', text:'انتخاب مکمل متناسب با برنامه‌ات', href:'/shop/', image:null, alt:''},
  {title:'وی مناسب خودت را پیدا کن', text:'مقایسه انواع پروتئین وی', href:'/shop/whey-protein/', image:null, alt:''},
  {title:'با آگاهی انتخاب کن', text:'راهنمای انتخاب پروتئین وی', href:'/guide/whey-protein/', image:null, alt:''},
];
export default function HomeSlideshow(){
  const [mount,setMount]=useState(null), [current,setCurrent]=useState(0), [paused,setPaused]=useState(false), [hovered,setHovered]=useState(false);
  useEffect(()=>{
    const main=document.querySelector('main');
    if(!main)return;
    const container=document.createElement('div');
    main.prepend(container);setMount(container);
    return()=>container.remove();
  },[]);
  useEffect(()=>{
    if(paused||hovered||window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
    const timer=setInterval(()=>{if(!document.hidden)setCurrent(i=>(i+1)%slides.length)},6000);
    return()=>clearInterval(timer);
  },[paused,hovered]);
  if(!mount)return null;
  return createPortal(<section className="home-slideshow" aria-label="پیشنهادهای وی کلاب" aria-roledescription="اسلایدشو" onMouseEnter={()=>setHovered(true)} onMouseLeave={()=>setHovered(false)} onFocusCapture={()=>setPaused(true)} onKeyDown={e=>{if(e.key==='ArrowLeft'){e.preventDefault();setCurrent(i=>(i+1)%slides.length)}if(e.key==='ArrowRight'){e.preventDefault();setCurrent(i=>(i+slides.length-1)%slides.length)}}}>
    {slides.map((slide,i)=><div key={slide.title} className={`home-slide home-slide-${i}`} role="group" aria-roledescription="اسلاید" aria-label={`${i+1} از ${slides.length}`} hidden={i!==current}>
      {slide.image&&<img src={slide.image} alt={slide.alt}/>}
      <div className="home-slide-copy"><span>WHEY CLUB</span><h2>{slide.title}</h2><p>{slide.text}</p><a href={slide.href}>مشاهده و انتخاب ←</a></div>
    </div>)}
    <div className="home-slide-controls"><button type="button" aria-label="اسلاید قبلی" onClick={()=>setCurrent(i=>(i+slides.length-1)%slides.length)}>→</button>
      <div className="home-slide-dots">{slides.map((_,i)=><button key={i} type="button" aria-label={`نمایش اسلاید ${i+1}`} aria-pressed={i===current} onClick={()=>setCurrent(i)}/>)}</div>
      <button type="button" aria-label="اسلاید بعدی" onClick={()=>setCurrent(i=>(i+1)%slides.length)}>←</button>
      <button className="home-slide-pause" type="button" aria-label={paused?'شروع پخش خودکار':'توقف پخش خودکار'} onClick={()=>setPaused(p=>!p)}>{paused?'▶':'Ⅱ'}</button>
    </div>
  </section>,mount);
}
