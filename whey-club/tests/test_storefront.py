import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('storefront',ROOT/'scripts/build_storefront.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.videos=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        attributes=dict(attrs)
        if tag=='video':self.videos.append(attributes)
        if 'id' in attributes:self.ids.add(attributes['id'])
        for k,v in attrs:
            if (tag,k) in [('a','href'),('img','src'),('script','src'),('link','href'),('source','src')]:self.links.append(v)
class StorefrontTests(unittest.TestCase):
    def test_routes_canonical_metadata_navigation_and_static_products(self):
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d);shutil.copy(ROOT/'dist/index.html',dest/'index.html')
            routes=builder.build(dest,'https://example.test');products=json.loads((ROOT/'content/products.json').read_text())
            self.assertEqual(len(routes),20)
            self.assertIn('/health-calculator/',routes)
            self.assertIn('/kits/',routes)
            self.assertIn('/coaches/',routes)
            for path in routes+['/cart/']:
                page=(dest/path.lstrip('/')/'index.html').read_text()
                self.assertIn('href="https://example.test'+path+'"',page)
                self.assertNotIn('href="#products"',page)
                self.assertNotIn('data-type=',page)
                self.assertEqual(len(re.findall('<h1[ >]',page)),1)
                self.assertIn('href="/health-calculator/"',page)
                self.assertIn('href="/start/"',page)
                parser=Links();parser.feed(page)
                for link in parser.links:
                    if not link.startswith('/') or link.startswith('/blog'):continue
                    target=dest/urlparse(link).path.lstrip('/')
                    if target.suffix:continue  # Shared assets checked against the real dist below.
                    self.assertTrue((target/'index.html').exists(),(path,link))
            isolate=(dest/'shop/whey-protein/isolate/index.html').read_text()
            self.assertIn('/products/whey-isolate-chocolate/',isolate)
            self.assertNotIn('href="/products/whey-concentrate-vanilla/"',isolate)
            self.assertIn('data-initial-type="isolate"',isolate)
            self.assertIn('noindex,follow',(dest/'cart/index.html').read_text())
            health=(dest/'health-calculator/index.html').read_text()
            self.assertIn('ماشین حساب سلامت',health)
            self.assertIn('src="/health-calculator.js"',health)
            self.assertIn('id="healthForm"',health)
            for product in products:
                text=(dest/'products'/product['slug']/'index.html').read_text()
                self.assertIn('application/ld+json',text)
                self.assertIn('BreadcrumbList',text)
                self.assertIn('data-add="'+str(product['id'])+'"',text)
    def test_homepage_starter_path_with_user_photo(self):
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d);shutil.copy(ROOT/'dist/index.html',dest/'index.html')
            routes=builder.build(dest,'https://example.test')
            self.assertIn('/start/',routes)
            home=(dest/'index.html').read_text();parser=Links();parser.feed(home)
            self.assertEqual(len(parser.videos),0)
            self.assertIn('/assets/training.webp',parser.links)
            self.assertNotIn('/homepage.js',parser.links)
            self.assertLess((ROOT/'dist/assets/training.webp').stat().st_size,500_000)
            self.assertIn('/start/',parser.links)
            self.assertIn('/shop/',parser.links)
            self.assertLess(home.index('id="supplementTitle"'),home.index('class="health-teaser"'))
            self.assertLess(home.index('href="/shop/"'),home.index('href="/start/"'))
            hero=home.split('class="natural-actions"',1)[1].split('</div>',1)[0]
            self.assertIn('class="primary" href="/shop/"',hero)
            self.assertNotIn('href="/start/"',hero)

            self.assertNotIn('id="products"',home)
            starter=Links();starter.feed((dest/'start/index.html').read_text())
            for anchor in ['build-muscle','lose-fat','get-consistent']:
                self.assertIn(anchor,starter.ids)
    def test_all_article_redirects_match_source(self):
        config=(ROOT/'deploy/nginx.conf').read_text()
        for a in json.loads((ROOT/'content/articles.json').read_text()):
            self.assertIn('/blog/'+a['slug']+'/ /blog/'+a['url_slug']+'/;',config)
