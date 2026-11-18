#!/usr/bin/env python3
"""Generate real static shop/category/product/kit/cart pages with canonical URLs."""
import argparse
import html
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
CATEGORY_NAMES={'isolate':'وی ایزوله','concentrate':'وی کنسانتره','blend':'وی ترکیبی'}
TYPE_LABELS={'isolate':'پروتئین وی ایزوله','concentrate':'پروتئین وی کنسانتره','blend':'پروتئین وی ترکیبی','creatine':'کراتین','shaker':'لوازم تمرین'}
GOAL_NAMES={'muscle':'عضله‌سازی','fatloss':'کاهش چربی','budget':'شروع اقتصادی','women':'بانوان'}
STYLE_VERSION='luxe5'
FA_DIGITS=str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹')

def esc(x):return html.escape(str(x),quote=True)
def fa(x):return str(x).translate(FA_DIGITS)
def money(n):return fa(f'{int(round(n)):,}'.replace(',','٬'))
def grams(x):
    x=float(x);return fa(int(x) if x.is_integer() else str(x).replace('.','٫'))

def per_serving(p):return round(p['price']/p['servings']/100)*100 if p.get('servings') else None
def per_25g(p):
    n=p.get('nutrition') or {}
    return round(p['price']/p['servings']/n['protein']*25/100)*100 if p.get('servings') and n.get('protein') else None

def chrome(site):
    """Shared trust strip, header and footer used on every page, homepage included."""
    trust=('<div class="trust-bar" role="note"><div class="wrap trust-inner">'
           '<span><i aria-hidden="true">✓</i>ضمانت اصالت کالا</span>'
           '<span><i aria-hidden="true">✓</i>ارسال همان‌روز در تهران</span>'
           '<span><i aria-hidden="true">✓</i>۷ روز ضمانت بازگشت</span>'
           f'<a href="tel:{esc(site["phoneHref"])}"><i aria-hidden="true">☏</i>مشاوره رایگان: <bdi>{esc(site["phone"])}</bdi></a>'
           '</div></div>')
    nav=('<header><div class="head wrap"><a class="logo" href="/" aria-label="وی کلاب؛ خانه"><b>W</b><div dir="ltr">WHEY<span>CLUB</span><small>TRAIN. EAT. GROW.</small></div></a>'
         '<nav aria-label="منوی اصلی"><a href="/shop/">فروشگاه</a><a href="/kits/">کیت‌های آماده</a><a href="/health-calculator/">ماشین حساب سلامت</a><a href="/start/">راهنمای شروع</a><a href="/blog/">مجله</a><a href="/coaches/">همکاری مربیان</a></nav>'
         '<a href="/cart/" class="cart-button">سبد خرید <span aria-hidden="true">♧</span><b id="cartCount">۰</b></a></div></header>')
    sample=' <small class="sample-tag">نمونه</small>' if site.get('sample') else ''
    footer=('<footer class="site-footer"><div class="wrap footer-grid">'
            '<div class="footer-brand"><a class="logo" href="/" aria-label="وی کلاب"><b>W</b><div dir="ltr">WHEY<span>CLUB</span></div></a>'
            '<p>مکمل اصل با کد اصالت قابل بررسی، قیمت شفاف به ازای هر وعده و راهنمای رایگان انتخاب؛ برای پیشرفت طبیعی و پایدار.</p></div>'
            '<div><h2>فروشگاه</h2><a href="/shop/whey-protein/">پروتئین وی</a><a href="/products/creatine-monohydrate/">کراتین</a><a href="/kits/">کیت‌های آماده</a><a href="/cart/">سبد خرید</a></div>'
            '<div><h2>راهنما</h2><a href="/health-calculator/">ماشین حساب سلامت</a><a href="/start/">راهنمای شروع</a><a href="/guide/whey-protein/">راهنمای انتخاب وی</a><a href="/blog/">مجله</a></div>'
            '<div><h2>وی کلاب</h2><a href="/about/">درباره ما</a><a href="/coaches/">همکاری مربیان</a>'
            f'<a href="tel:{esc(site["phoneHref"])}">تلفن: <bdi>{esc(site["phone"])}</bdi>{sample}</a><span>{esc(site["hours"])}</span><span>{esc(site["address"])}</span></div>'
            '</div><div class="wrap footer-trust">'
            '<div class="badge-slot" aria-label="جای نماد اعتماد الکترونیکی"><meta name="enamad" content="48512357" /><b>اینماد</b><span>جای نماد اعتماد</span></div>'
            '<div class="badge-slot"><b>شاپرک</b><span>پرداخت امن بانکی</span></div>'
            '<div class="badge-slot"><b>TTAC</b><span>اصالت قابل استعلام</span></div>'
            '<p>© ۱۴۰۵ وی کلاب · نسخه نمایشی؛ پرداخت آنلاین هنوز فعال نیست. مطالب آموزشی‌اند و جایگزین مشاوره فردی متخصص نیستند.</p>'
            '</div></footer>')
    return trust,nav,footer

def product_card(q):
    unit=per_serving(q)
    badge=f'<span class="badge">{fa(round((1-q["price"]/q["old"])*100))}٪ تخفیف</span>' if q.get('old') else ''
    return (f'<article class="card"><a class="visual" href="/products/{q["slug"]}/">{badge}<img src="/assets/{q["color"]}.svg" alt="{esc(q["name"])}" loading="lazy"></a>'
            f'<div class="info"><div class="brand">{esc(TYPE_LABELS.get(q["type"],""))}</div><a class="title" href="/products/{q["slug"]}/">{esc(q["name"])}</a>'
            f'<div class="meta">{esc(q["size"])} · {esc(q["flavorName"])}</div>'
            +(f'<div class="unit-price">هر وعده {money(unit)} تومان</div>' if unit else '')+
            f'<div class="card-bottom"><div class="price"><span class="old">{money(q["old"]) if q.get("old") else ""}</span>{money(q["price"])} <small>تومان</small></div>'
            f'<button class="add" data-add="{q["id"]}" aria-label="افزودن {esc(q["name"])} به سبد">+</button></div></div></article>')

def build(output,origin):
    output=Path(output);origin=origin.rstrip('/')
    read=lambda name:json.loads((ROOT/'content'/name).read_text(encoding='utf-8'))
    products=read('products.json');site=read('site.json');kits=read('kits.json')
    by_id={p['id']:p for p in products}
    whey=[p for p in products if p['category']=='whey']
    template=(output/'index.html').read_text(encoding='utf-8')
    trust,nav,footer=chrome(site)
    cart_dialog='''<dialog id="cartDialog"><button class="close" aria-label="بستن">×</button><h2>سبد خرید شما</h2><div id="cartItems"></div><div id="cartSummary"></div></dialog><div id="toast" role="status"></div>'''
    routes=['/','/shop/','/shop/whey-protein/','/guide/whey-protein/','/about/','/health-calculator/','/start/']
    def page(path,title,description,body,schema=None,noindex=False):
        canonical=origin+path
        data='' if not schema else '<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script>'
        if path=='/health-calculator/':data+='<link rel="stylesheet" href="/health-calculator.css">'
        if path in ('/start/','/kits/','/coaches/'):data+='<link rel="stylesheet" href="/homepage.css?v='+STYLE_VERSION+'">'
        content=f'''<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | وی کلاب</title><meta name="description" content="{esc(description)}"><meta name="theme-color" content="#0e1522"><link rel="canonical" href="{esc(canonical)}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{esc(canonical)}">{'<meta name="robots" content="noindex,follow">' if noindex else ''}<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&family=Barlow+Condensed:wght@700;800&display=swap" rel="stylesheet"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/blog.css">{data}<link rel="stylesheet" href="/luxe.css?v={STYLE_VERSION}"></head><body>{trust}{nav}<main class="wrap route-main">{body}</main>{footer}{cart_dialog if path!='/cart/' else '<div id="toast" role="status"></div>'}<script src="/catalog.js?v={STYLE_VERSION}"></script><script src="/app.js?v={STYLE_VERSION}"></script></body></html>'''
        destination=output/path.lstrip('/')/'index.html';destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(content,encoding='utf-8')
    def crumbs(parts):
        links=[('<a href="/">خانه</a>')]+[('<a href="'+url+'">'+esc(label)+'</a>') for label,url in parts]
        return '<nav class="breadcrumbs" aria-label="مسیر صفحه">'+' / '.join(links)+'</nav>'
    def heading(kicker,title,text):
        return f'<section class="route-heading"><div class="kicker">{kicker}</div><h1>{esc(title)}</h1><p>{text}</p></section>'

    # Shared catalog layout retains real filtering and cart functionality.
    catalog=(ROOT/'content/storefront-catalog.html').read_text(encoding='utf-8')
    guide=(ROOT/'content/whey-guide.html').read_text(encoding='utf-8')
    for path,kind in [('/shop/whey-protein/',None)]+[('/shop/whey-protein/'+k+'/',k) for k in CATEGORY_NAMES]:
        title=CATEGORY_NAMES.get(kind,'پروتئین وی')
        h='ویِ مناسب خودت را پیدا کن.' if not kind else title+' را بهتر بشناس.'
        desc='همه محصولات اصل با کد اصالت، جدول ارزش غذایی و قیمت هر وعده؛ کنار هم مقایسه کن و آگاهانه انتخاب کن.'
        body=crumbs([('فروشگاه','/shop/')]+([(title,path)] if path!='/shop/' else []))+heading('فروشگاه پروتئین وی',h,desc)
        tabs='<nav class="shop-categories" aria-label="نوع پروتئین"><a href="/shop/whey-protein/"'+(' class="selected"' if not kind else '')+'>همه پروتئین‌های وی</a>'+''.join('<a href="/shop/whey-protein/'+k+'/"'+(' class="selected"' if kind==k else '')+'>'+v+'</a>' for k,v in CATEGORY_NAMES.items())+'</nav>'
        filtered=catalog.replace('<section id="products">','<section id="products" data-initial-type="'+(kind or '')+'">').replace('ویِ مناسب تو، همین‌جاست','انتخاب‌های '+title)
        static_cards=''.join(product_card(q) for q in whey if not kind or q['type']==kind)
        filtered=filtered.replace('<div id="grid"></div>','<div id="grid">'+static_cards+'</div>')
        body+=tabs+'<div class="route-search search"><span>⌕</span><input id="search" type="search" placeholder="جستجو در پروتئین‌ها…" aria-label="جستجوی محصولات"></div>'+filtered
        page(path,'خرید '+title,desc,body)
        if kind:routes.append(path)

    shop_cards=[('/shop/whey-protein/','lime','پروتئین وی','ایزوله، کنسانتره و ترکیبی؛ با قیمت هر وعده کنار هم.','دیدن همه پروتئین‌های وی'),
                ('/products/creatine-monohydrate/','creatine','کراتین مونوهیدرات','پرشواهدترین مکمل برای قدرت؛ روزی ۵ گرم.','دیدن کراتین'),
                ('/kits/','shaker','کیت‌های آماده','بر اساس هدفت؛ همه با یک کلیک در سبد.','انتخاب کیت')]
    shop_body=crumbs([('فروشگاه','/shop/')])+heading('فروشگاه وی کلاب','انتخاب خوب، شروع خوب.','همه محصولات اصل‌اند و کد اصالت، سری ساخت و تاریخ انقضایشان روی صفحه محصول آمده است. اگر نمی‌دانی از کجا شروع کنی، از کیت‌های آماده یا ماشین حساب سلامت کمک بگیر.')
    shop_body+='<div class="shop-landing">'+''.join(f'<a class="shop-category-card" href="{u}"><img src="/assets/{img}.svg" alt="" loading="lazy"><div><h2>{t}</h2><p>{d}</p><b>{c} ←</b></div></a>' for u,img,t,d,c in shop_cards)+'</div>'
    page('/shop/','فروشگاه مکمل اصل','پروتئین وی، کراتین و کیت‌های آماده؛ مکمل اصل با کد اصالت و قیمت شفاف هر وعده.',shop_body)

    for p in products:
        path='/products/'+p['slug']+'/'
        if p['category']=='whey':
            trail=[('پروتئین وی','/shop/whey-protein/'),(CATEGORY_NAMES[p['type']],'/shop/whey-protein/'+p['type']+'/'),(p['name'],path)]
        else:
            trail=[('فروشگاه','/shop/'),(p['name'],path)]
        n=p.get('nutrition') or {}
        unit,unit25=per_serving(p),per_25g(p)
        facts=[]
        if n.get('protein'):facts.append((grams(n['protein'])+' گرم','پروتئین در هر وعده'))
        if n.get('creatine'):facts.append((grams(n['creatine'])+' گرم','کراتین در هر وعده'))
        if p.get('servings'):facts.append((fa(p['servings']),'وعده در هر بسته'))
        facts.append((p['size'],'وزن خالص' if p['category']!='accessory' else 'حجم'))
        facts.append((p['flavorName'],'طعم' if p['category']!='accessory' else 'رنگ'))
        old=f'<s>{money(p["old"])}</s><span class="save">{fa(round((1-p["price"]/p["old"])*100))}٪ تخفیف</span>' if p.get('old') else ''
        units=[]
        if unit:units.append(f'هر وعده <b>{money(unit)}</b> تومان')
        if unit25:units.append(f'هر ۲۵ گرم پروتئین <b>{money(unit25)}</b> تومان')
        support=esc(site['support'])
        body=crumbs(trail)+f'''<section class="pdp"><div class="pdp-media"><div class="pdp-stage"><img src="/assets/{p['color']}.svg" alt="{esc(p['name'])}" width="300" height="390"></div><ul class="pdp-badges"><li><i aria-hidden="true">✓</i>ضمانت اصالت</li><li><i aria-hidden="true">✓</i>سری ساخت قابل ردیابی</li><li><i aria-hidden="true">✓</i>انبار با دمای کنترل‌شده</li></ul></div>
<div class="pdp-info"><div class="kicker">{esc(TYPE_LABELS[p['type']])}</div><h1>{esc(p['name'])}</h1><p class="pdp-pitch">{esc(p['pitch'])}</p>
<dl class="pdp-facts">'''+''.join(f'<div><dt>{esc(b)}</dt><dd>{esc(fa(a))}</dd></div>' for a,b in facts)+f'''</dl>
<div class="pdp-buy"><div class="pdp-price">{old}<strong>{money(p['price'])} <small>تومان</small></strong></div>'''+(f'<p class="pdp-unit">{" · ".join(units)}</p>' if units else '')+f'''<button class="primary pdp-add" data-add="{p['id']}">افزودن به سبد خرید</button><a class="pdp-ask" href="{support}" rel="noopener">سؤال داری؟ از کارشناس ما بپرس ←</a><p class="pdp-demo">نسخه نمایشی: پرداخت آنلاین هنوز فعال نیست.</p></div>
<ul class="pdp-service"><li><b>ارسال</b><span>همان‌روز در تهران؛ ۲ تا ۴ روز کاری در سایر شهرها. بالای {money(site['freeShipping'])} تومان رایگان.</span></li><li><b>بازگشت</b><span>تا ۷ روز برای بسته باز‌نشده، بدون پرسش اضافه.</span></li><li><b>پرداخت</b><span>درگاه امن بانکی (شاپرک) یا پرداخت در محل در تهران.</span></li></ul></div></section>'''
        if p.get('irc'):
            body+=f'''<section class="pdp-auth" aria-labelledby="authTitle"><div><div class="kicker">اصالت کالا</div><h2 id="authTitle">خودت بررسی کن؛ لازم نیست فقط به ما اعتماد کنی.</h2><ol><li>کد IRC روی بسته را با کد همین صفحه مقایسه کن.</li><li>کد اصالت زیر برچسب را در <a href="https://www.ttac.ir/" rel="noopener">سامانه رسمی سازمان غذا و دارو (TTAC)</a> استعلام کن.</li><li>اگر کالا اصل نبود، کل مبلغ را برمی‌گردانیم و هزینه ارسال با ماست.</li></ol></div>
<dl class="auth-codes"><div><dt>کد IRC</dt><dd><bdi>{esc(fa(p['irc']))}</bdi></dd></div><div><dt>سری ساخت</dt><dd><bdi>{esc(p['batch'])}</bdi></dd></div><div><dt>تاریخ انقضا</dt><dd>{esc(p['expiry'])}</dd></div><p>مقادیر این بخش در نسخه نمایشی نمونه‌اند.</p></dl></section>'''
        details=''
        if n:
            rows=[('انرژی',grams(n['kcal'])+' کیلوکالری'),('پروتئین',grams(n['protein'])+' گرم'),('کربوهیدرات',grams(n['carbs'])+' گرم'),('قند',grams(n['sugar'])+' گرم'),('چربی',grams(n['fat'])+' گرم')]
            if n.get('creatine'):rows=[('کراتین مونوهیدرات',grams(n['creatine'])+' گرم')]+[r for r in rows if r[0]=='انرژی']
            details+=f'<article><h2>ارزش غذایی</h2><p class="muted">در هر وعده ({grams(n["scoop"])} گرم)</p><table class="nutrition-table"><tbody>'+''.join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a,b in rows)+'</tbody></table></article>'
        details+=f'<article><h2>ترکیبات</h2><p>{esc(p["ingredients"])}</p>'+(f'<p class="allergen"><b>هشدار آلرژی:</b> {esc(p["allergens"])}</p>' if p.get('allergens') else '')+'</article>'
        details+=f'<article><h2>{"روش مصرف" if p["category"]!="accessory" else "نگهداری"}</h2><p>{esc(p["usage"])}</p><a href="/guide/whey-protein/">راهنمای کامل انتخاب و مصرف ←</a></article>'
        body+=f'<section class="pdp-details">{details}</section>'
        related=[q for q in products if q['id']!=p['id'] and q['category']==p['category']][:3] or [q for q in whey][:3]
        body+='<section class="related"><div class="kicker">پیشنهاد بعدی</div><h2>این‌ها را هم ببین</h2><div class="related-products">'+''.join(f'<a href="/products/{q["slug"]}/"><img src="/assets/{q["color"]}.svg" alt="{esc(q["name"])}" loading="lazy"><b>{esc(q["name"])}</b><span>{money(q["price"])} تومان</span></a>' for q in related)+'</div></section>'
        body+=f'<div class="buy-bar" aria-hidden="true"><div><b>{esc(p["name"])}</b><span>{money(p["price"])} تومان</span></div><button class="primary" data-add="{p["id"]}" tabindex="-1">افزودن به سبد</button></div>'
        schema=[{'@context':'https://schema.org','@type':'Product','name':p['name'],'description':p['pitch'],'image':origin+'/assets/'+p['color']+'.svg','url':origin+path,'brand':{'@type':'Brand','name':'WHEY CLUB'}},{'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'خانه','item':origin+'/'}]+[{'@type':'ListItem','position':i+2,'name':label,'item':origin+url} for i,(label,url) in enumerate(trail)]}]
        page(path,p['name'],p['pitch'],body,schema);routes.append(path)

    kit_body=crumbs([('کیت‌های آماده','/kits/')])+heading('کیت‌های آماده','کیت مناسب هدفت را انتخاب کن.','هر کیت چند محصول است که کنار هم معنا دارند؛ با یک کلیک همه به سبدت اضافه می‌شوند. اگر هنوز نمی‌دانی چقدر پروتئین لازم داری، اول <a href="/health-calculator/">ماشین حساب سلامت</a> را امتحان کن.')
    for k in kits:
        items=[by_id[i] for i in k['items']]
        total=sum(q['price'] for q in items)
        kit_body+=(f'<section class="kit" id="{k["id"]}" aria-labelledby="kit-{k["id"]}"><div class="kit-copy"><span class="kit-goal">{GOAL_NAMES[k["id"]]}</span><h2 id="kit-{k["id"]}">{esc(k["name"])}</h2><p class="kit-who">{esc(k["who"])}</p><p>{esc(k["why"])}</p>'
                   f'<div class="kit-total"><span>جمع کیت</span><strong>{money(total)} <small>تومان</small></strong></div><button class="primary" data-add-kit="{",".join(map(str,k["items"]))}">افزودن کل کیت به سبد</button></div>'
                   '<ul class="kit-items">'+''.join(f'<li><a href="/products/{q["slug"]}/"><img src="/assets/{q["color"]}.svg" alt="" loading="lazy"><span><b>{esc(q["name"])}</b><small>{esc(q["size"])} · {money(q["price"])} تومان</small></span></a></li>' for q in items)+'</ul></section>')
    kit_body+='<p class="natural-demo-note">ترکیب کیت‌ها پیشنهاد عمومی است، نه نسخه فردی. مکمل جای غذا و تمرین را نمی‌گیرد.</p>'
    page('/kits/','کیت‌های آماده مکمل','کیت عضله‌سازی، کاهش چربی، شروع اقتصادی و بانوان؛ مکمل‌هایی که کنار هم معنا دارند.',kit_body);routes.append('/kits/')

    coach_body=crumbs([('همکاری مربیان','/coaches/')])+heading('همکاری مربیان','مربی هستی؟ شاگردانت را با خیال راحت به ما بسپار.','شاگردانت مکمل اصل با کد اصالت قابل بررسی می‌گیرند، تو کمیسیون هر خرید را دریافت می‌کنی و دیگر لازم نیست انبار و ارسال را خودت مدیریت کنی.')
    coach_body+=('<section class="coach-grid">'
        '<article><span>۰۱</span><h2>کد معرف اختصاصی</h2><p>یک کد و لینک به نام خودت؛ هر خرید با آن، به حساب تو ثبت می‌شود.</p></article>'
        '<article><span>۰۲</span><h2>کمیسیون از هر خرید</h2><p>درصد کمیسیون و تخفیف شاگردان را در اولین تماس با هم تعیین می‌کنیم.</p></article>'
        '<article><span>۰۳</span><h2>تخفیف برای شاگردان</h2><p>شاگردانت با کد تو ارزان‌تر می‌خرند؛ اعتمادشان به تو بیشتر می‌شود، نه کمتر.</p></article>'
        '<article><span>۰۴</span><h2>بدون دردسر انبار</h2><p>ارسال، پشتیبانی و بازگشت کالا با ماست؛ تو روی تمرین دادن تمرکز کن.</p></article>'
        '</section>'
        f'<section class="coach-cta"><div><h2>برای شروع همکاری تماس بگیر</h2><p>نام باشگاه و شهرت را بگو؛ ظرف یک روز کاری جواب می‌دهیم.</p></div><div class="coach-actions"><a class="primary" href="tel:{esc(site["phoneHref"])}">تماس: <bdi>{esc(site["phone"])}</bdi></a><a class="natural-text-link" href="{esc(site["support"])}" rel="noopener">پیام در پشتیبانی ←</a></div></section>'
        '<p class="natural-demo-note">برنامه همکاری پس از راه‌اندازی فروش واقعی فعال می‌شود.</p>')
    page('/coaches/','همکاری مربیان','برنامه همکاری مربیان و باشگاه‌ها با وی کلاب؛ کد معرف، کمیسیون و تخفیف برای شاگردان.',coach_body);routes.append('/coaches/')

    page('/guide/whey-protein/','راهنمای انتخاب پروتئین وی','با تفاوت انواع پروتئین وی آشنا شو و انتخاب آگاهانه‌تری داشته باش.',crumbs([('راهنمای انتخاب وی','/guide/whey-protein/')])+heading('راهنمای انتخاب','ویِ مناسب تو کدام است؟','هدفت را بشناس، برچسب را بخوان و انتخابی متناسب با برنامه‌ات داشته باش.')+guide+'<div class="journal-end"><b>کنجکاوی، شروع خوبی است.</b><a href="/blog/">مقاله‌های کوتاه مجله را بخوان ←</a></div>')
    page('/about/','درباره وی کلاب','فروشگاه مکمل وی کلاب، همراه با ابزارهای سلامت و راهنمای انتخاب آگاهانه مکمل.',(ROOT/'content/about.html').read_text(encoding='utf-8'))
    page('/start/','شروع بدنسازی طبیعی','راهنمای شروع تمرین، تغذیه، عضله‌سازی طبیعی و کاهش چربی؛ قدم‌های عملی با منابع علمی.',(ROOT/'content/start.html').read_text(encoding='utf-8'))
    page('/health-calculator/','ماشین حساب سلامت','محاسبه کالری روزانه برای کاهش، حفظ و افزایش وزن، پروتئین مورد نیاز و BMI همراه با منابع علمی.',(ROOT/'content/health-calculator.html').read_text(encoding='utf-8'))
    page('/cart/','سبد خرید','محصولات انتخاب‌شده‌ات در وی کلاب را مدیریت کن.',crumbs([('سبد خرید','/cart/')])+'<section class="cart-page"><div class="kicker">سبد خرید</div><h1>انتخاب‌های تو.</h1><div id="cartItems"></div><div id="cartSummary"></div><a class="continue-shop" href="/shop/">ادامه خرید ←</a></section>',noindex=True)
    # Product/catalog data is public; article drafts remain private.
    public_site={k:site[k] for k in ('phone','phoneHref','support','freeShipping')}
    (output/'catalog.js').write_text('window.WHEY_PRODUCTS = '+json.dumps(products,ensure_ascii=False)+';\nwindow.WHEY_SITE = '+json.dumps(public_site,ensure_ascii=False)+';\n',encoding='utf-8')
    (output/'public-routes.json').write_text(json.dumps(routes))
    # The homepage shares the same trust strip, header and footer.
    template=re.sub(r'<link rel="canonical"[^>]*>','',template)
    template=template.replace('</head>','<link rel="canonical" href="'+origin+'/"></head>')
    template=re.sub(r'<div class="(?:announcement|trust-bar)".*?</div>(?=\s*<header>)',lambda m:trust,template,count=1,flags=re.S)
    template=re.sub(r'<header>.*?</header>',lambda m:nav,template,count=1,flags=re.S)
    template=re.sub(r'<footer[ >].*?</footer>',lambda m:footer,template,count=1,flags=re.S)
    template=re.sub(r'<link rel="stylesheet" href="/luxe\.css[^"]*">','',template)
    template=template.replace('</head>','<link rel="stylesheet" href="/luxe.css?v='+STYLE_VERSION+'"></head>',1)
    template=re.sub(r'src="/catalog\.js[^"]*"','src="/catalog.js?v='+STYLE_VERSION+'"',template)
    template=re.sub(r'src="/app\.js[^"]*"','src="/app.js?v='+STYLE_VERSION+'"',template)
    if 'src="/catalog.js' not in template:template=template.replace('<script src="/app.js','<script src="/catalog.js?v='+STYLE_VERSION+'"></script><script src="/app.js',1)
    (output/'index.html').write_text(template,encoding='utf-8')
    return routes

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default=str(ROOT/'dist'));parser.add_argument('--origin',default='http://94.184.25.127:8088');args=parser.parse_args();build(args.output,args.origin)
