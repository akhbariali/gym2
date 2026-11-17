#!/usr/bin/env python3
"""Keep searchable HTML for existing routes while booting React on each page."""
import json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
build=root/'frontend/build'
entry_html=(build/'index.html').read_text()
entry=re.search(r'<script[^>]+src="([^"]+)"',entry_html).group(1)
styles=[re.search(r'href="([^"]+)"',tag).group(1) for tag in re.findall(r'<link[^>]+>',entry_html) if 'rel="stylesheet"' in tag and 'href="/assets/' in tag]
style_links=''.join('<link rel="stylesheet" href="'+href+'">' for href in styles)
(build/'react-entry.json').write_text(json.dumps({'src':entry,'styles':styles}))
for source in (root/'dist').rglob('index.html'):
    if 'blog' in source.relative_to(root/'dist').parts:continue
    text=source.read_text()
    text=text.replace('</head>',style_links+'</head>')
    text=re.sub(r'<script\b[^>]*>.*?</script>','',text,flags=re.S)
    text=re.sub(r'(<body\b[^>]*>)',r'\1<div id="root">',text).replace('</body>','</div><script type="module" src="'+entry+'"></script></body>')
    target=build/source.relative_to(root/'dist');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)

for route,title in [('account','حساب کاربری'),('account/login','ورود به حساب'),('account/register','ثبت‌نام'),('account/addresses','نشانی‌های من'),('checkout','تکمیل خرید')]:
    target=build/route/'index.html';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text('<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+title+' | وی کلاب</title><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/blog.css"><link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">'+style_links+'</head><body><div id="root"></div><script type="module" src="'+entry+'"></script></body></html>')
