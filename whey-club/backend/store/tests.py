from django.test import TestCase
class ApiTests(TestCase):
    def test_catalog(self):
        response=self.client.get('/api/products/')
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json()['results']),8)
    def test_unpublished_article_is_private(self):
        self.assertEqual(self.client.get('/api/articles/not-published/').status_code,404)
    def test_get_only(self):
        self.assertEqual(self.client.post('/api/products/').status_code,405)
