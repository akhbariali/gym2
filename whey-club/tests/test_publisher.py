import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from contextlib import redirect_stdout
import io

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('publisher',ROOT/'scripts/publish_articles.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.output=Path(self.temp.name)/'site';self.state=Path(self.temp.name)/'state'
        self.now=datetime(2026,11,15,12,tzinfo=timezone.utc)
    def run_publish(self,now=None,rebuild=False):
        with redirect_stdout(io.StringIO()):
            return p.publish(ROOT/'content/articles.json',self.output,self.state,'https://example.test',now=now or self.now,rebuild=rebuild)
    def test_cadence_retries_downtime_and_future_privacy(self):
        state=self.run_publish();self.assertEqual(len(state['published']),1)
        self.assertFalse((self.output/'blog/whey-concentrate-vs-isolate/index.html').exists())
        self.assertNotIn('whey-concentrate-vs-isolate',(self.output/'sitemap.xml').read_text())
        self.assertEqual(len(self.run_publish()['published']),1)
        self.assertEqual(len(self.run_publish(self.now+timedelta(hours=47,minutes=59))['published']),1)
        state=self.run_publish(self.now+timedelta(hours=48));self.assertEqual(len(state['published']),2)
        self.assertTrue((self.output/'blog/whey-concentrate-vs-isolate/index.html').exists())
        state=self.run_publish(self.now+timedelta(days=30));self.assertEqual(len(state['published']),3)
        self.assertEqual(len(self.run_publish(self.now+timedelta(days=30))['published']),3)
        self.assertEqual(len(self.run_publish(self.now-timedelta(days=1))['published']),3)
    def test_all_articles_render_and_queue_stops(self):
        for day in range(0,200,2):
            state=self.run_publish(self.now+timedelta(days=day))
        self.assertEqual(len(state['published']),100)
        self.assertEqual(len(list((self.output/'blog').glob('*/index.html'))),100)
        self.assertEqual(len(self.run_publish(self.now+timedelta(days=300))['published']),100)
        summaries=json.loads((self.output/'blog/articles.json').read_text());self.assertEqual(len(summaries),100)
        article=(self.output/'blog/what-is-whey-protein/index.html').read_text()
        self.assertIn('href="/health-calculator/"',article)
        self.assertIn('href="/start/"',article)
        self.assertIn('application/ld+json',article);self.assertIn('rel="canonical"',article)
        self.assertIn('pmc.ncbi.nlm.nih.gov',article);self.assertIn('datePublished',article)
        self.assertIn('/blog/what-is-whey-protein/',(self.output/'sitemap.xml').read_text())
        self.assertTrue((self.output/'blog/category/whey-protein/index.html').exists())
        self.assertNotIn('content_markdown',(self.output/'blog/articles.json').read_text())
    def test_rebuild_preserves_dates_and_safe_markdown(self):
        state=self.run_publish();self.assertEqual(state,self.run_publish(rebuild=True))
        body,toc=p.markdown('# Title\n\n## Heading\n\n<script>alert(1)</script>\n\n- https://example.com/a')
        self.assertNotIn('<script>',body);self.assertIn('&lt;script&gt;',body)
        self.assertIn('href="https://example.com/a"',body);self.assertEqual(len(toc),1)

if __name__=='__main__':unittest.main()
