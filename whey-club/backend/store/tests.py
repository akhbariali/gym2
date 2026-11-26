from django.test import TestCase
class ApiTests(TestCase):
    def test_catalog(self):
        response=self.client.get('/api/products/')
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json()['results']),8)
        self.assertFalse(any(p['is_demo'] for p in response.json()['results']))
        self.assertEqual(self.client.get('/products/creatine-monohydrate/').status_code,404)
        self.assertNotContains(self.client.get('/sitemap.xml'),'/products/creatine-monohydrate/')
    def test_unpublished_article_is_private(self):
        self.assertEqual(self.client.get('/api/articles/not-published/').status_code,404)
    def test_get_only(self):
        self.assertEqual(self.client.post('/api/products/').status_code,405)
