from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Category,CategoryRoute,Product

class CategoryTests(TestCase):
    def test_seeded_routes_and_filter(self):
        categories=self.client.get('/api/categories/').json()['results']
        self.assertEqual(len(categories),3)
        whey=Category.objects.get(slug='whey-protein')
        self.assertFalse(whey.children.exists())
        for slug in ['isolate','concentrate','blend']:
            self.assertRedirects(self.client.get('/shop/whey-protein/'+slug+'/'),'/shop/whey-protein/',status_code=301)
        self.assertFalse(Product.objects.filter(protein_type__in=['isolate','concentrate','blend']).exclude(category_node=whey).exists())
        self.assertEqual(self.client.get('/shop/not-a-category/').status_code,404)
        self.assertEqual(self.client.get('/shop/whey-protein/').status_code,200)
        self.assertContains(self.client.get('/shop/creatine/'),'کراتین مونوهیدرات')
        self.assertNotContains(self.client.get('/shop/creatine/'),'پروتئین وی ایزوله شکلات')
        self.assertEqual(Product.objects.filter(category_node=None).count(),0)
    def test_parent_rename_and_move_redirect_descendants(self):
        whey=Category.objects.get(slug='whey-protein');child=Category.objects.create(name='test child',slug='test-child',parent=whey)
        old=child.get_absolute_url();whey.slug='whey';whey.save();child.refresh_from_db()
        self.assertEqual(child.get_absolute_url(),'/shop/whey/test-child/')
        response=self.client.get(old+'?sort=low')
        self.assertEqual(response.status_code,301);self.assertEqual(response['Location'],'/shop/whey/test-child/?sort=low')
        supplements=Category.objects.create(name='مکمل‌ها',slug='supplements')
        whey.parent=supplements;whey.save();child.refresh_from_db()
        self.assertEqual(child.get_absolute_url(),'/shop/supplements/whey/test-child/')
        self.assertEqual(self.client.get(old)['Location'],child.get_absolute_url())
        sitemap=self.client.get('/sitemap.xml').content.decode()
        self.assertIn(child.get_absolute_url(),sitemap);self.assertNotIn(old,sitemap)
    def test_cycles_duplicates_and_historical_collisions_rejected(self):
        whey=Category.objects.get(slug='whey-protein');child=Category.objects.create(name='test child',slug='test-child',parent=whey)
        whey.parent=child
        with self.assertRaises(ValidationError):whey.save()
        with self.assertRaises(ValidationError):Category.objects.create(name='duplicate',slug='creatine')
        whey.refresh_from_db();whey.slug='new-whey';whey.save()
        with self.assertRaises(ValidationError):Category.objects.create(name='reuse',slug='whey-protein')
    def test_category_assignment_and_admin(self):
        from django.contrib.auth import get_user_model
        owner=get_user_model().objects.create_superuser('category-owner','owner@example.test','a-long-secret-test-password')
        self.client.force_login(owner)
        self.assertEqual(self.client.get('/admin/store/category/').status_code,200)
        p=Product.objects.filter(is_active=True).first();c=Category.objects.get(slug='creatine');p.category_node=c;p.save()
        self.assertEqual(next(x for x in self.client.get('/api/products/').json()['results'] if x['id']==p.pk)['category_id'],c.pk)
