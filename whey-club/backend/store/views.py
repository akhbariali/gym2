import json
from django.conf import settings
from django.db import connection, DatabaseError
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET

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
    return JsonResponse({'results': load('products.json')})

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
