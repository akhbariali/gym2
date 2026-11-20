import json
from django.conf import settings
from django.db import connection, DatabaseError
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404, render
from django.utils.safestring import mark_safe
from .models import Product

def load(name):
    return json.loads((settings.CONTENT_DIR / name).read_text())

def published():
    if not settings.PUBLICATION_STATE.exists():
        return []
    state = json.loads(settings.PUBLICATION_STATE.read_text())
    dates = {p['slug']: p['published_at'] for p in state['published']}
    return sorted([dict(a, published_at=dates[a['slug']]) for a in load('articles.json') if a['slug'] in dates], key=lambda a: a['published_at'], reverse=True)

@require_GET
def products(request):
    response=JsonResponse({'results': [p.as_catalog() for p in Product.objects.filter(is_active=True)]})
    response['Cache-Control']='no-cache'
    return response

@require_GET
def articles(request):
    return JsonResponse({'results': [{k: v for k, v in a.items() if k != 'content_markdown'} for a in published()]})

@require_GET
def article(request, slug):
    for a in published():
        if slug == a.get('url_slug', a['slug']):
            return JsonResponse(a)
    raise Http404('Article not published')

@require_GET
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM django_migrations')
            cursor.fetchone()
    except DatabaseError:
        return JsonResponse({'status': 'unavailable'}, status=503)
    return JsonResponse({'status': 'ok'})

@require_GET
def product_detail(request,slug):
    response=JsonResponse(get_object_or_404(Product,is_active=True,slug=slug).as_catalog())
    response['Cache-Control']='no-cache'
    return response

@require_GET
def product_page(request,slug):
    product=get_object_or_404(Product,is_active=True,slug=slug)
    entry_file=settings.FRONTEND_ROOT/'react-entry.json'
    entry=json.loads(entry_file.read_text()) if entry_file.exists() else {'src':'','styles':[]}
    canonical=request.build_absolute_uri(product.get_absolute_url())
    schema={'@context':'https://schema.org','@type':'Product','name':product.name,'description':product.description,'url':canonical,'brand':{'@type':'Brand','name':product.brand}}
    return render(request,'store/product_shell.html',{'product':product,'entry':entry,'canonical':canonical,'schema':mark_safe(json.dumps(schema,ensure_ascii=False).replace('<','\\u003c'))})

@require_GET
def sitemap(request):
    from xml.etree import ElementTree as ET
    from urllib.parse import urlsplit
    from django.http import HttpResponse
    paths=['/','/shop/','/shop/whey-protein/','/blog/']
    routes=settings.FRONTEND_ROOT/'public-routes.json'
    if routes.exists():
        paths.extend(p for p in json.loads(routes.read_text()) if isinstance(p,str) and p.startswith('/') and not p.startswith(('/products/','/account/','/admin/','/cart/','/checkout/','//')))
    existing=settings.FRONTEND_ROOT/'sitemap.xml'
    if existing.exists():
        try:paths.extend(urlsplit(n.text).path for n in ET.parse(existing).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc') if n.text and urlsplit(n.text).path.startswith('/blog/'))
        except ET.ParseError:pass
    paths.extend(p.get_absolute_url() for p in Product.objects.filter(is_active=True))
    ns='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',ns)
    root=ET.Element('{'+ns+'}urlset')
    for path in dict.fromkeys(paths):
        url=ET.SubElement(root,'{'+ns+'}url');ET.SubElement(url,'{'+ns+'}loc').text=request.build_absolute_uri(path)
    response=HttpResponse(ET.tostring(root,encoding='utf-8',xml_declaration=True),content_type='application/xml')
    response['Cache-Control']='no-cache'
    return response
