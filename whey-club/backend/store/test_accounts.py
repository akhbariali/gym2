from django.test import TestCase,Client,override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .models import Address,CheckoutDraft

class AccountsTests(TestCase):
    def setUp(self):
        cache.clear();self.u=get_user_model().objects.create_user('first@example.com','first@example.com','VeryGood-Password-938!')
        self.other=get_user_model().objects.create_user('other@example.com','other@example.com','Other-Good-Pass-32!')
        self.address={'recipient':'کاربر آزمایشی','phone':'09123456789','province':'تهران','city':'تهران','postal_code':'1234567890','street':'خیابان آزمایشی پلاک ۱۲','latitude':35.7,'longitude':51.4}
    def post(self,path,data):return self.client.post(path,data,content_type='application/json')
    def test_registration_login_logout_and_password_hash(self):
        r=self.post('/api/account/register/',{'name':'کاربر تست','email':'NEW@example.com','password':'A-Strong-Password-982!'})
        self.assertEqual(r.status_code,201)
        u=get_user_model().objects.get(username='new@example.com');self.assertTrue(u.check_password('A-Strong-Password-982!'));self.assertNotEqual(u.password,'A-Strong-Password-982!')
        self.assertEqual(self.client.get('/api/account/session/').json()['user']['id'],u.pk)
        self.post('/api/account/logout/',{});self.assertIsNone(self.client.get('/api/account/session/').json()['user'])
        self.assertEqual(self.post('/api/account/login/',{'email':'new@example.com','password':'A-Strong-Password-982!'}).status_code,200)
        self.assertEqual(self.post('/api/account/register/',{'name':'تست','email':'bad@example.com','password':'123'}).status_code,400)
    def test_address_ownership_and_validation(self):
        self.assertEqual(self.client.get('/api/account/addresses/').status_code,401)
        self.client.force_login(self.u);r=self.post('/api/account/addresses/',self.address);self.assertEqual(r.status_code,201);pk=r.json()['id']
        self.assertEqual(self.post('/api/account/addresses/',dict(self.address,latitude=999)).status_code,400)
        self.assertEqual(self.post('/api/account/addresses/',dict(self.address,postal_code='x')).status_code,400)
        self.client.force_login(self.other);self.assertEqual(self.client.get('/api/account/addresses/').json()['results'],[])
        self.assertEqual(self.post(f'/api/account/addresses/{pk}/delete/',{}).status_code,404)
        self.assertTrue(Address.objects.filter(pk=pk).exists())
    def test_checkout_server_totals_idempotency_and_no_payment(self):
        from .models import Product
        Product.objects.filter(pk=1).update(is_active=True)
        self.client.force_login(self.u);pk=self.post('/api/account/addresses/',self.address).json()['id']
        data={'key':'unique-test-key-1','address_id':pk,'items':[{'id':1,'quantity':2,'price':1}]}
        r=self.post('/api/checkout/',data);self.assertEqual(r.status_code,201)
        self.assertEqual(r.json()['total'],5780000);self.assertFalse(r.json()['payment_available']);self.assertIsNone(r.json()['payment_url'])
        self.assertEqual(self.post('/api/checkout/',data).status_code,200);self.assertEqual(CheckoutDraft.objects.count(),1)
        self.assertEqual(self.post('/api/checkout/',dict(data,items=[{'id':1,'quantity':-1}])).status_code,400)
        self.client.force_login(self.other);self.assertEqual(self.post('/api/checkout/',data).status_code,400)
    def test_csrf_and_secure_transport(self):
        client=Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/api/account/register/',{},content_type='application/json').status_code,403)
        with override_settings(ACCOUNT_REQUIRE_HTTPS=True):
            self.assertEqual(self.client.get('/api/account/session/').status_code,426)
            self.assertEqual(self.client.get('/api/account/session/',secure=True).status_code,200)
    def test_auth_throttle(self):
        for i in range(20):self.post('/api/account/login/',{'email':'missing@example.com','password':'wrong'})
        self.assertEqual(self.post('/api/account/login/',{'email':'missing@example.com','password':'wrong'}).status_code,429)
