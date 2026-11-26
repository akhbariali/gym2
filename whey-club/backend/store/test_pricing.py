from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Product,PricingSettings,Address,CheckoutDraft
from .shipping import postage

class PricingShippingTests(TestCase):
    def test_import_rate_rounding_and_checkout(self):
        from importlib import import_module
        rows=import_module('store.migrations.0010_seed_supplier_creatines').PRODUCTS
        products=Product.objects.filter(slug__in=[row['slug'] for row in rows])
        self.assertEqual(products.count(),8)
        p=products.get(slug='fa-ice-creatine-300g')
        self.assertEqual(p.selling_price,4050000)
        settings=PricingSettings.objects.get(pk=1);settings.aed_rate=80000;settings.save()
        self.assertEqual(p.selling_price,4210000)
        p.price=105000;p.reference_aed_rate=80000;p.save()
        self.assertEqual(p.selling_price,110000) # Half rounds up, not banker's rounding.
        user=get_user_model().objects.create_user(username='pricing-buyer')
        address=Address.objects.create(user=user,recipient='test',phone='09123456789',province='تهران',city='تهران',postal_code='1234567890',street='test')
        self.client.force_login(user)
        payload={'key':'pricing-post-test','address_id':address.pk,'shipping_method':'post','items':[{'id':p.pk,'quantity':1,'price':1}]}
        response=self.client.post('/api/checkout/',payload,content_type='application/json')
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json()['total'],330000)
        self.assertEqual(response.json()['shipping']['fee'],220000)
        self.assertEqual(self.client.post('/api/checkout/',payload,content_type='application/json').status_code,200)
        self.assertEqual(CheckoutDraft.objects.get(key=payload['key']).address['shipping']['method'],'post')
        payload['shipping_method']='tipax'
        self.assertEqual(self.client.post('/api/checkout/',payload,content_type='application/json').status_code,409)

    def test_tariffs_and_missing_weights(self):
        self.assertEqual(postage('tipax','تهران',[(None,1)]),0)
        self.assertEqual(postage('post','تهران',[(450,2)]),220000)
        self.assertEqual(postage('post','شهریار',[(450,1)]),200000)
        for weight,fee in [(1000,250000),(2000,330000),(3000,400000),(4000,470000),(5000,550000),(6000,610000),(6900,610000)]:
            self.assertEqual(postage('post','تهران',[(weight,1)]),fee)
        for weight in [None,7000]:
            with self.assertRaises(ValueError):postage('post','تهران',[(weight,1)])
