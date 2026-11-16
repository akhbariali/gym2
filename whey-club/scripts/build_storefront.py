#!/usr/bin/env python3
"""Generate real static shop/category/product/cart pages with canonical URLs."""
import argparse
import html
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
CATEGORY_NAMES={'isolate':'وی ایزوله','concentrate':'وی کنسانتره','blend':'وی ترکیبی'}

def build(output,origin):
    output=Path(output);origin=origin.rstrip('/')
    products=json.loads((ROOT/'content/products.json').read_text())
    template=(output/'index.html').read_text()
    esc=lambda x:html.escape(str(x),quote=True)
    nav='<header><div class="head wrap"><a class="logo" href="/" aria-label="وی کلاب؛ خانه"><b>W</b><div dir="ltr">WHEY<span>CLUB</span><small>TRAIN. EAT. GROW.</small></div></a><nav aria-label="منوی اصلی"><a href="/start/">از اینجا شروع کن</a><a href="/blog/">مجله تمرین و تغذیه</a><a href="/health-calculator/">ماشین حساب سلامت</a><a href="/shop/">مکمل\u200cها</a><a href="/about/">درباره ما</a></nav><a href="/cart/" class="cart-button">سبد خرید <span aria-hidden="true">♧</span><b id="cartCount">۰</b></a></div></header>'
    cart_dialog='''<dialog id="cartDialog"><button class="close" aria-label="بستن">×</button><h2>سبد خرید شما</h2><div id="cartItems"></div><div id="cartSummary"></div></dialog><div id="toast" role="status"></div>'''
    routes=['/','/shop/','/shop/whey-protein/','/guide/whey-protein/','/about/','/health-calculator/','/start/']
    def page(path,title,description,body,schema=None,noindex=False):
        canonical=origin+path
        data='' if not schema else '<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script>'
        if path=='/health-calculator/':data+='<link rel="stylesheet" href="/health-calculator.css">'
        if path=='/start/':data+='<link rel="stylesheet" href="/homepage.css">'
        content=f'''<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | وی کلاب</title><meta name="description" content="{esc(description)}"><meta name="theme-color" content="#719a73"><link rel="canonical" href="{esc(canonical)}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{esc(canonical)}">{'<meta name="robots" content="noindex,follow">' if noindex else ''}<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800;900&family=Barlow+Condensed:wght@700;800&display=swap" rel="stylesheet"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/blog.css">{data}</head><body><div class="announcement">بدنسازی طبیعی، با قدم‌های واقعی <span>✺</span> تمرین. تغذیه. تداوم.</div>{nav}<main class="wrap route-main">{body}</main><footer class="wrap"><span>© وی کلاب</span><a href="/shop/whey-protein/">فروشگاه</a><a href="/blog/">مجله وی کلاب</a><span>کاتالوگ نمایشی · پرداخت واقعی فعال نیست.</span></footer>{cart_dialog if path!='/cart/' else '<div id="toast" role="status"></div>'}<script src="/catalog.js"></script><script src="/app.js"></script></body></html>'''
        destination=output/path.lstrip('/')/'index.html';destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(content)
    def crumbs(parts):
        links=[('<a href="/">خانه</a>')]+[('<a href="'+url+'">'+esc(label)+'</a>') for label,url in parts]
        return '<div class="breadcrumbs">'+' / '.join(links)+'</div>'
    # Shared catalog layout retains real filtering and cart functionality.
    catalog=(ROOT/'content/storefront-catalog.html').read_text()
    guide=(ROOT/'content/whey-guide.html').read_text()
    for path,kind in [('/shop/whey-protein/',None)]+[('/shop/whey-protein/'+k+'/',k) for k in CATEGORY_NAMES]:
        title=CATEGORY_NAMES.get(kind,'پروتئین وی')
        heading='وقتشه '+('ویِ خودت رو پیدا کنی.' if not kind else title+' رو بهتر بشناسی.')
        desc='طعم مورد علاقه‌ات، فرمول مناسب تو. پروتئین‌ها رو مقایسه کن و آگاهانه انتخاب کن.'
        body=crumbs([('فروشگاه','/shop/')]+([(title,path)] if path!='/shop/' else []))+f'<section class="route-heading"><div class="kicker">FIND YOUR EVERYDAY FUEL</div><h1>{esc(heading)}</h1><p>{desc}</p><span class="route-sticker">LET’S GET STRONGER ✺</span></section>'
        tabs='<nav class="shop-categories"><a href="/shop/whey-protein/"'+(' class="selected"' if not kind else '')+'>همه پروتئین‌های وی</a>'+''.join('<a href="/shop/whey-protein/'+k+'/"'+(' class="selected"' if kind==k else '')+'>'+v+'</a>' for k,v in CATEGORY_NAMES.items())+'</nav>'
        filtered=catalog.replace('<section id="products">','<section id="products" data-initial-type="'+(kind or '')+'">').replace('ویِ مناسب تو، همین‌جاست','انتخاب‌های '+title)
        static_cards=''.join('<article class="card"><a class="visual" href="/products/'+q['slug']+'/"><img src="/assets/'+q['color']+'.svg" alt="'+esc(q['name'])+'"></a><div class="info"><a class="title" href="/products/'+q['slug']+'/">'+esc(q['name'])+'</a><div class="meta">'+q['size']+' · '+q['flavorName']+'</div><button class="add" data-add="'+str(q['id'])+'" aria-label="افزودن به سبد">+</button></div></article>' for q in products if not kind or q['type']==kind)
        filtered=filtered.replace('<div id="grid"></div>','<div id="grid">'+static_cards+'</div>')
        body+=tabs+'<div class="route-search search"><span>⌕</span><input id="search" type="search" placeholder="جستجو در پروتئین‌ها…" aria-label="جستجوی محصولات"></div>'+filtered
        page(path,'خرید '+title,desc,body)
        if kind:routes.append(path)
    page('/shop/','مکمل‌ها؛ انتخاب آگاهانه','مکمل در کنار تمرین، تغذیه و ریکاوری؛ مقایسه کاتالوگ فعلی پروتئین وی.',crumbs([('فروشگاه','/shop/')])+'<section class="route-heading"><div class="kicker">YOUR DAILY FUEL STARTS HERE</div><h1>انتخاب خوب، شروعِ خوب.</h1><p>کاتالوگ فعلی روی پروتئین وی متمرکز است. قبل از انتخاب، نیاز، ترکیبات و بودجه‌ات را مقایسه کن.</p></section><a class="shop-category-card" href="/shop/whey-protein/"><img src="/assets/lime.svg" alt="پروتئین وی"><div><span class="kicker">01 / WHEY PROTEIN</span><h2>پروتئین وی</h2><p>ایزوله، کنسانتره و ترکیبی؛ طعم مورد علاقه‌ات رو پیدا کن.</p><b>دیدن همه پروتئین‌های وی ←</b></div></a>')
    for p in products:
        path='/products/'+p['slug']+'/'
        product_crumbs=crumbs([('پروتئین وی','/shop/whey-protein/'),(CATEGORY_NAMES[p['type']],'/shop/whey-protein/'+p['type']+'/'),(p['name'],path)])
        related=[q for q in products if q['id']!=p['id']][:3]
        body=product_crumbs+f'''<section class="product-page"><div class="product-stage"><span class="route-sticker">YOUR NEXT GOOD HABIT ✺</span><img src="/assets/{p['color']}.svg" alt="{esc(p['name'])}"><span class="stage-caption">FUEL. TRAIN. FEEL GOOD.</span></div><div class="product-page-copy"><div class="kicker">{p['en']}</div><h1>{esc(p['name'])}</h1><p>برای روزهایی که جدی تمرین می‌کنی و می‌خوای تغذیه‌ات هم همراهت باشه.</p><div class="product-specs"><div><b>{p['protein']}</b><span>گرم پروتئین نمونه</span></div><div><b>{p['size']}</b><span>وزن بسته نمونه</span></div><div><b>{p['flavorName']}</b><span>طعم مورد علاقه‌ات</span></div></div><div class="product-buy"><div class="price">{p['price']:,} <small>تومان</small></div><button class="primary" data-add="{p['id']}">افزودن به سبد خرید +</button></div><div class="product-notice">محصول و قیمت نمایشی هستند. پرداخت و سفارش واقعی فعال نیست. حاوی مشتقات شیر است.</div><a class="compare-link" href="/shop/whey-protein/{p['type']}/">مقایسه با بقیه {CATEGORY_NAMES[p['type']]}‌ها ←</a></div></section><section class="product-description"><h2>همراه برنامه روزانه تو</h2><p>این صفحه نمونه‌ای از اطلاعات محصول در وی کلاب است. پیش از خرید واقعی، مقدار مصرف، جدول ارزش غذایی، آلرژن‌ها و مشخصات روی بسته‌بندی نهایی را بررسی کنید. مشخصات این کاتالوگ نمونه‌اند.</p><a href="/guide/whey-protein/">برای انتخاب وی، از اینجا شروع کن ←</a></section><section class="related"><div class="kicker">MEET YOUR NEXT FAVORITE</div><h2>این‌ها رو هم ببین</h2><div class="related-products">'''+''.join(f'<a href="/products/{q["slug"]}/"><img src="/assets/{q["color"]}.svg" alt="{esc(q["name"])}"><b>{esc(q["name"])}</b><span>جزئیات محصول ←</span></a>' for q in related)+'</div></section>'
        schema=[{'@context':'https://schema.org','@type':'Product','name':p['name'],'description':'محصول نمایشی پروتئین وی کلاب؛ فروش واقعی هنوز فعال نیست.','image':origin+'/assets/'+p['color']+'.svg','url':origin+path,'brand':{'@type':'Brand','name':'WHEY CLUB'}},{'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'خانه','item':origin+'/'},{'@type':'ListItem','position':2,'name':'پروتئین وی','item':origin+'/shop/whey-protein/'},{'@type':'ListItem','position':3,'name':p['name'],'item':origin+path}]}]
        page(path,p['name'],'مشخصات نمونه '+p['name']+'؛ مقایسه طعم، وزن و پروتئین در وی کلاب.',body,schema);routes.append(path)
    page('/guide/whey-protein/','راهنمای انتخاب پروتئین وی','با تفاوت انواع پروتئین وی آشنا شو و انتخاب آگاهانه‌تری داشته باش.',crumbs([('راهنمای انتخاب وی','/guide/whey-protein/')])+'<section class="route-heading"><div class="kicker">YOUR FIRST SCOOP STARTS HERE</div><h1>ویِ مناسب تو کدومه؟</h1><p>هدفت رو بشناس، برچسب رو بخون و انتخابی متناسب با برنامه‌ات داشته باش.</p></section>'+guide+'<div class="journal-end"><b>کنجکاوی، شروع خوبیه.</b><a href="/blog/">مقاله‌های کوتاه مجله رو بخون ←</a></div>')
    page('/about/','درباره وی کلاب','مسیر بدنسازی طبیعی؛ محتوای آموزشی، ابزارهای سلامت و انتخاب آگاهانه مکمل.',(ROOT/'content/about.html').read_text())
    page('/start/','شروع بدنسازی طبیعی','راهنمای شروع تمرین، تغذیه، عضله‌سازی طبیعی و کاهش چربی؛ قدم‌های عملی با منابع علمی.',(ROOT/'content/start.html').read_text())
    page('/health-calculator/','ماشین حساب سلامت','محاسبه کالری روزانه برای کاهش، حفظ و افزایش وزن، پروتئین مورد نیاز و BMI همراه با منابع علمی.',(ROOT/'content/health-calculator.html').read_text())
    page('/cart/','سبد خرید','محصولات انتخاب‌شده‌ات در وی کلاب را مدیریت کن.',crumbs([('سبد خرید','/cart/')])+'<section class="cart-page"><div class="kicker">YOUR GOOD-ENERGY KIT</div><h1>انتخاب‌های تو.</h1><div id="cartItems"></div><div id="cartSummary"></div><a class="continue-shop" href="/shop/whey-protein/">ادامه خرید ←</a></section>',noindex=True)
    # Product/catalog data is public; article drafts remain private.
    (output/'catalog.js').write_text('window.WHEY_PRODUCTS = '+json.dumps(products,ensure_ascii=False)+';\n')
    (output/'public-routes.json').write_text(json.dumps(routes))
    # Root metadata is updated without generating a duplicate document title.
    template=re.sub(r'<link rel="canonical"[^>]*>','',template)
    template=template.replace('</head>','<link rel="canonical" href="'+origin+'/"></head>')
    if 'src="/catalog.js"' not in template:template=template.replace('<script src="/app.js">','<script src="/catalog.js"></script><script src="/app.js">')
    (output/'index.html').write_text(template)
    return routes

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default=str(ROOT/'dist'));parser.add_argument('--origin',default='http://94.184.25.127:8088');args=parser.parse_args();build(args.output,args.origin)
