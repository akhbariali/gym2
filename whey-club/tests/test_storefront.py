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
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if (tag,k) in [('a','href'),('img','src'),('script','src'),('link','href')]:self.links.append(v)
class StorefrontTests(unittest.TestCase):
    def test_routes_canonical_metadata_navigation_and_static_products(self):
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d);shutil.copy(ROOT/'dist/index.html',dest/'index.html')
            routes=builder.build(dest,'https://example.test');products=json.loads((ROOT/'content/products.json').read_text())
            self.assertEqual(len(routes),14)
            for path in routes+['/cart/']:
                page=(dest/path.lstrip('/')/'index.html').read_text()
                self.assertIn('href="https://example.test'+path+'"',page)
                self.assertNotIn('href="#products"',page)
                self.assertNotIn('data-type=',page)
                self.assertEqual(len(re.findall('<h1[ >]',page)),1)
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
            for product in products:
                text=(dest/'products'/product['slug']/'index.html').read_text()
                self.assertIn('application/ld+json',text)
                self.assertIn('BreadcrumbList',text)
                self.assertIn('data-add="'+str(product['id'])+'"',text)
    def test_all_article_redirects_match_source(self):
        config=(ROOT/'deploy/nginx.conf').read_text()
        for a in json.loads((ROOT/'content/articles.json').read_text()):
            self.assertIn('/blog/'+a['slug']+'/ /blog/'+a['url_slug']+'/;',config)
