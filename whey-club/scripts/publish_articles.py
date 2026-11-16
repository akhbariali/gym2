#!/usr/bin/env python3
"""Publish at most one queued article per 48 hours; dependency-free and restart-safe."""
import argparse
import fcntl
import html
import json
import os
from pathlib import Path
import re
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

INTERVAL = timedelta(hours=48)
CATEGORY_SLUGS = {'پروتئین وی':'whey-protein','کراتین و مکمل\u200cها':'supplements','تغذیه ورزشی':'sports-nutrition','تمرین و عضله\u200cسازی':'training','اهداف و سبک زندگی':'fitness-lifestyle','راهنمای خرید و ایمنی':'buying-guides'}

def article_path(article):
    return '/blog/'+article.get('url_slug',article['slug'])+'/'

def category_path(category):
    return '/blog/category/'+CATEGORY_SLUGS[category]+'/'


def esc(value):
    return html.escape(str(value), quote=True)

def atomic(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(content, encoding='utf-8')
    os.chmod(temp, 0o644)
    os.replace(temp, path)

def inline(text):
    safe = esc(text)
    safe = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', safe)
    return re.sub(r'https://[^\s<>]+', lambda m: '<a href="'+m[0]+'" rel="noopener noreferrer" target="_blank">'+esc(urlparse(html.unescape(m[0])).netloc)+'</a>', safe)

def markdown(text):
    out, paragraph, bullets, toc = [], [], [], []
    def flush():
        if paragraph:
            out.append('<p>'+inline(' '.join(paragraph))+'</p>'); paragraph.clear()
        if bullets:
            out.append('<ul>'+''.join('<li>'+inline(x)+'</li>' for x in bullets)+'</ul>'); bullets.clear()
    for line in text.splitlines():
        if line.startswith('# '):
            continue
        if not line.strip():
            flush(); continue
        if line.startswith('## ' ) or line.startswith('### '):
            flush(); label=line.lstrip('# ').strip(); ident='section-'+str(len(toc)+1)
            toc.append((ident,label)); out.append('<h2 id="'+ident+'">'+esc(label)+'</h2>')
        elif line.startswith('- '):
            if paragraph: flush()
            bullets.append(line[2:])
        else:
            if bullets: flush()
            paragraph.append(line)
    flush()
    return '\n'.join(out), toc

def shell(title, description, body, origin, path, schema=None):
    canonical=origin.rstrip('/')+path
    structured='' if schema is None else '<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script>'
    return f'''<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="theme-color" content="#719a73"><link rel="canonical" href="{esc(canonical)}"><meta property="og:type" content="{'article' if schema and schema.get('@type')=='Article' else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{esc(canonical)}"><link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800;900&family=Barlow+Condensed:wght@700;800&display=swap" rel="stylesheet"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/blog.css">{structured}</head><body><div class="announcement">دانش بیشتر. انتخاب آگاهانه‌تر. <span>✦</span> مجله وی کلاب</div><header class="blog-header wrap"><a class="logo" href="/"><b>W</b><div dir="ltr">WHEY<span>CLUB</span><small>TRAIN. EAT. GROW.</small></div></a><nav><a href="/start/">از اینجا شروع کن</a><a href="/blog/" class="active">مجله تمرین و تغذیه</a><a href="/health-calculator/">ماشین حساب سلامت</a><a href="/shop/">مکمل‌ها</a></nav><a class="back-shop" href="/shop/whey-protein/">پروتئینت رو پیدا کن ↙</a></header><main class="wrap blog-main">{body}</main><footer class="wrap"><span>© وی کلاب · دانش، پیش از انتخاب</span><span>مطالب آموزشی‌اند و جایگزین توصیه فردی متخصص سلامت نیستند.</span><a href="/">بازگشت به فروشگاه ←</a></footer><script src="/blog.js" defer></script></body></html>'''

def card(article, date):
    return f'''<a class="editorial-card" href="{esc(article_path(article))}" data-category="{esc(article['category'])}"><div class="editorial-art art-{int(article['id'])%4}"><span>WHEY CLUB JOURNAL</span><b>{int(article['id']):02d}</b><i>↗</i></div><div class="editorial-body"><div class="article-category">{esc(article['category'])} <span>حدود ۲ دقیقه مطالعه</span></div><h2>{esc(article['title'])}</h2><p>{esc(article['meta_description'])}</p><div class="read-link"><time datetime="{esc(date)}">{esc(date[:10])}</time><span>مطالعه مقاله ←</span></div></div></a>'''

def render(articles, published, output, origin):
    lookup={a['slug']:a for a in articles}
    chosen=[(lookup[p['slug']],p['published_at']) for p in published]
    output=Path(output)
    for article, date in chosen:
        content,toc=markdown(article['content_markdown'])
        path=article_path(article)
        related=sorted([(a,d) for a,d in chosen if a['slug']!=article['slug']],key=lambda pair:pair[0]['category']!=article['category'])[:3]
        related_html='<section class="related"><div class="kicker">KEEP LEARNING</div><h2>یک قدم بیشتر بدان</h2><div class="editorial-grid">'+''.join(card(a,d) for a,d in related)+'</div></section>' if related else ''
        body=f'''<div class="breadcrumbs"><a href="/">خانه</a> / <a href="/blog/">مجله وی کلاب</a> / <a href="{category_path(article['category'])}">{esc(article['category'])}</a></div><header class="article-heading"><div class="kicker">THE TWO-MINUTE READ</div><div class="article-category">{esc(article['category'])}</div><h1>{esc(article['title'])}</h1><div class="article-byline">تحریریه وی کلاب <span>·</span> <time datetime="{esc(date)}">{esc(date[:10])}</time><span>·</span> حدود ۲ دقیقه مطالعه</div></header><div class="article-layout"><article class="prose">{content}<div class="editorial-disclosure">درباره این مطلب: متن آموزشی تهیه‌شده با کمک هوش مصنوعی است و بازبینی تخصصی پزشکی نشده است. منابع برای مطالعه بیشتر هستند.</div><a class="article-return" href="/blog/">← همه مقاله‌های مجله</a></article><aside class="article-aside"><div class="kicker">IN THIS ARTICLE</div><h3>در این مقاله می‌خوانید</h3>{''.join('<a href="#'+ident+'">'+esc(label)+'</a>' for ident,label in toc)}<div class="reading-cta"><b>انتخاب آگاهانه، تمرین بهتر.</b><p>انواع پروتئین وی رو مقایسه کن.</p><a href="/shop/whey-protein/">دیدن پروتئین‌های وی ←</a></div></aside></div>{related_html}'''
        schema={'@context':'https://schema.org','@type':'Article','headline':article['title'],'description':article['meta_description'],'inLanguage':'fa','datePublished':date,'dateModified':date,'author':{'@type':'Organization','name':'تحریریه وی کلاب'},'publisher':{'@type':'Organization','name':'WHEY CLUB'},'mainEntityOfPage':origin+path,'citation':article['sources'],'timeRequired':'PT2M'}
        atomic(output/path.lstrip('/')/'index.html',shell(article['seo_title'],article['meta_description'],body,origin,path,schema))
    categories=list(dict.fromkeys(a['category'] for a,d in chosen))
    body='''<section class="journal-hero"><div><div class="kicker">THE WHEY CLUB JOURNAL</div><h1>تمرین کن. یاد بگیر.<br><em>طبیعی ادامه بده.</em></h1><p>راهنماهای کوتاه برای تمرین قابل اجرا، تغذیه روزمره و انتخاب آگاهانه مکمل؛ همراه مسیر بدنسازی طبیعی.</p><div class="journal-promise"><span>◷ حدود ۲ دقیقه مطالعه</span><span>↗ هر دو روز، یک مقاله تازه</span></div></div><div class="journal-graphic" dir="ltr"><span>LESS GUESSWORK.</span><b>MORE<br>KNOW<br>HOW<span>↗</span></b><small>READ. LEARN. GROW.</small></div></section>'''
    body+='<section class="journal-list"><div class="section-heading"><div><div class="kicker">SMALL READS. BIG DIFFERENCE.</div><h2>برای یک قدم جلوتر بودن<span>.</span></h2></div><label class="article-search">⌕ <input id="articleSearch" type="search" placeholder="جستجو در مقاله‌ها…" aria-label="جستجوی مقاله‌ها"></label></div><div class="category-tabs"><a class="selected" href="/blog/">همه مقاله‌ها</a>'+''.join('<a href="'+category_path(c)+'">'+esc(c)+'</a>' for c in categories)+'</div><p id="articleCount">'+str(len(chosen))+' مقاله منتشرشده</p><div class="editorial-grid">'+''.join(card(a,d) for a,d in reversed(chosen))+'</div><p id="noArticles" hidden>مقاله‌ای با این جستجو پیدا نشد.</p></section><div class="journal-end"><b>دانش بیشتر، انتخاب بهتر.</b><span>مقاله بعدی، دو روز پس از آخرین انتشار به مجله اضافه می‌شود.</span><a href="/shop/whey-protein/">رفتن به فروشگاه ←</a></div>'
    atomic(output/'blog/index.html',shell('مجله وی کلاب | بدنسازی طبیعی، تمرین و تغذیه','راهنماهای دو دقیقه‌ای فارسی درباره پروتئین وی، مکمل‌های ورزشی، تغذیه و بدنسازی؛ هر دو روز یک مقاله تازه.',body,origin,'/blog/'))
    for category in categories:
        subset=[(a,d) for a,d in reversed(chosen) if a['category']==category]
        category_body='<div class="breadcrumbs"><a href="/">خانه</a> / <a href="/blog/">مجله وی کلاب</a> / '+esc(category)+'</div><section class="route-heading"><div class="kicker">LEARN. TRAIN. REPEAT.</div><h1>مقاله‌های '+esc(category)+'</h1><p>راهنماهای کوتاه، برای انتخاب‌های بهتر هر روز.</p></section><section class="journal-list"><div class="section-heading"><a href="/blog/">همه مقاله‌ها ←</a><label class="article-search">⌕ <input id="articleSearch" type="search" placeholder="جستجو در این دسته…" aria-label="جستجوی مقاله‌ها"></label></div><p id="articleCount">'+str(len(subset))+' مقاله منتشرشده</p><div class="editorial-grid">'+''.join(card(a,d) for a,d in subset)+'</div><p id="noArticles" hidden>مقاله‌ای با این جستجو پیدا نشد.</p></section>'
        path=category_path(category)
        atomic(output/path.lstrip('/')/'index.html',shell('مقاله‌های '+category+' | مجله وی کلاب','راهنماهای دو دقیقه‌ای درباره '+category,category_body,origin,path))
    atomic(output/'blog/articles.json',json.dumps([{'title':a['title'],'category':a['category'],'description':a['meta_description'],'url':article_path(a),'published_at':d,'id':a['id']} for a,d in reversed(chosen)],ensure_ascii=False))
    urls=json.loads((output/'public-routes.json').read_text()) if (output/'public-routes.json').exists() else ['/']
    urls+=['/blog/']+[category_path(c) for c in categories]+[article_path(a) for a,d in chosen]
    atomic(output/'sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+esc(origin+u)+'</loc></url>' for u in urls)+'</urlset>')
    atomic(output/'robots.txt','User-agent: *\nAllow: /\nSitemap: '+origin+'/sitemap.xml\n')

def publish(source, output, state_dir, origin, now=None, rebuild=False):
    now=now or datetime.now(timezone.utc)
    state_dir=Path(state_dir);state_dir.mkdir(parents=True,exist_ok=True)
    with (state_dir/'publisher.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        articles=json.loads(Path(source).read_text())
        assert len({a['slug'] for a in articles})==len(articles), 'Duplicate slugs'
        assert len({a.get('url_slug',a['slug']) for a in articles})==len(articles), 'Duplicate URL slugs'
        for a in articles:
            assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',a['slug']), 'Invalid slug'
            assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',a.get('url_slug',a['slug'])), 'Invalid URL slug'
            assert a['title'] and a['content_markdown'] and a['sources'], 'Incomplete article'
        state_path=state_dir/'publication.json'
        state=json.loads(state_path.read_text()) if state_path.exists() else {'published':[]}
        published=state['published'];known={a['slug'] for a in articles}
        assert all(p['slug'] in known for p in published), 'Published article missing from queue'
        existing={p['slug'] for p in published}
        pending=[a for a in articles if a['slug'] not in existing]
        due=not published or now>=datetime.fromisoformat(published[-1]['published_at'])+INTERVAL
        changed=False
        if due and pending:
            published.append({'slug':pending[0]['slug'],'published_at':now.isoformat()})
            changed=True
        if changed or rebuild:
            render(articles,published,output,origin.rstrip('/'))
            atomic(state_path,json.dumps(state,ensure_ascii=False,indent=2))
        print(json.dumps({'published':len(published),'queued':len(articles)-len(published),'new_article':published[-1]['slug'] if changed else None,'next_publication':(datetime.fromisoformat(published[-1]['published_at'])+INTERVAL).isoformat() if pending and published and len(published)<len(articles) else None}))
        return state

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--state-dir',required=True)
    parser.add_argument('--origin',required=True)
    parser.add_argument('--rebuild',action='store_true',help='Re-render published pages without advancing the schedule unless due')
    args=parser.parse_args()
    publish(args.source,args.output,args.state_dir,args.origin,rebuild=args.rebuild)
