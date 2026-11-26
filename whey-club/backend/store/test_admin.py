from django.test import TestCase,override_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.utils import timezone
from .models import Product,Order,OrderItem,CheckoutDraft

class StoreAdminTests(TestCase):
    def setUp(self):
        cache.clear()
        self.owner=get_user_model().objects.create(username='admin-test',is_staff=True,is_superuser=True,password='!')
        self.customer=get_user_model().objects.create(username='customer-test',password='!')
        self.p=Product.objects.get(pk=1)
        self.p.is_active=True;self.p.save()
    def login(self):self.client.force_login(self.owner)
    def order(self,payment='paid',status='pending',quantity=3,reference='verified-test',paid_at=True):
        o=Order.objects.create(user=self.customer,address={'recipient':'test'},total=quantity*100,payment_status=payment,status=status,payment_reference=reference,paid_at=timezone.now() if paid_at else None)
        OrderItem.objects.create(order=o,product=self.p,product_name=self.p.name,quantity=quantity,unit_price=100)
        return o
    def test_anonymous_and_customers_cannot_access_admin(self):
        self.assertEqual(self.client.get('/admin/').status_code,302)
        self.client.force_login(self.customer)
        self.assertEqual(self.client.get('/admin/').status_code,302)
        self.assertEqual(self.client.get('/admin/store/product/add/').status_code,302)
    def test_dashboard_counts_only_verified_non_cancelled_sales(self):
        self.order();self.order(payment='unpaid',quantity=8,reference='',paid_at=False)
        self.order(status='cancelled',quantity=20);self.order(payment='refunded',quantity=2)
        self.order(reference='',quantity=7)
        CheckoutDraft.objects.create(user=self.customer,key='unpaid-test',items=[{'id':1,'quantity':99}],address={},total=1)
        self.login();r=self.client.get('/admin/');self.assertEqual(r.status_code,200)
        self.assertEqual(r.context['summary']['units'],3)
        self.assertEqual(r.context['summary']['sales_total'],300)
        self.assertEqual(r.context['active_orders'],1)
        self.assertEqual(r.context['unpaid_drafts'],1)
        p=next(p for p in r.context['product_sales'] if p.pk==self.p.pk)
        self.assertEqual((p.units_sold,p.sales_total),(3,300))
        self.p.price=999999;self.p.save()
        self.assertEqual(self.client.get('/admin/').context['summary']['sales_total'],300)
    def test_product_editor_adds_live_catalog_and_stock_validation(self):
        self.login();data={'name':'محصول تست','slug':'','brand':'TEST','protein_type':'isolate','flavor':'vanilla','flavor_name':'وانیل','package_size':'۱۰۰۰ گرم','price':'200000','protein_grams':'25','servings':'30','color':'lime','stock':'2','is_active':'on','nutrition':'{}'}
        r=self.client.post('/admin/store/product/add/',data);self.assertEqual(r.status_code,302)
        p=Product.objects.get(name='محصول تست');self.assertGreater(p.pk,6)
        self.assertTrue(p.slug)
        self.assertEqual(self.client.get('/api/products/'+p.slug+'/').status_code,200)
        self.assertEqual(self.client.get(p.get_absolute_url()).status_code,200)
        self.assertContains(self.client.get('/sitemap.xml'),p.get_absolute_url())
        p.is_active=False;p.save()
        self.assertEqual(self.client.get('/api/products/'+p.slug+'/').status_code,404)
        self.assertEqual(self.client.get(p.get_absolute_url()).status_code,404)
        self.assertNotContains(self.client.get('/sitemap.xml'),p.get_absolute_url())
    def test_admin_cannot_forge_payment_or_ship_unpaid_order(self):
        o=self.order(payment='unpaid',reference='',paid_at=False);self.login()
        inline={'lines-TOTAL_FORMS':'1','lines-INITIAL_FORMS':'1','lines-MIN_NUM_FORMS':'0','lines-MAX_NUM_FORMS':'1000','lines-0-id':str(o.lines.first().pk),'lines-0-order':str(o.pk)}
        r=self.client.post(f'/admin/store/order/{o.pk}/change/',{**inline,'status':'processing','tracking_code':'','staff_notes':''})
        self.assertEqual(r.status_code,200);o.refresh_from_db();self.assertEqual(o.status,'pending')
        r=self.client.post(f'/admin/store/order/{o.pk}/change/',{**inline,'status':'pending','tracking_code':'','staff_notes':'checked','payment_status':'paid','total':'1'})
        self.assertEqual(r.status_code,302);o.refresh_from_db();self.assertEqual(o.payment_status,'unpaid');self.assertEqual(o.total,300)
        self.assertEqual(self.client.get('/admin/store/order/add/').status_code,403)
    def test_product_only_staff_do_not_see_sales(self):
        staff=get_user_model().objects.create(username='editor-test',is_staff=True,password='!')
        staff.user_permissions.add(Permission.objects.get(codename='view_product'))
        self.order();self.client.force_login(staff)
        r=self.client.get('/admin/');self.assertFalse(r.context['can_report'])
        r=self.client.get('/admin/store/product/');self.assertEqual(r.status_code,200)
        self.assertIsNone(r.context['cl'].queryset.first().units_sold)
    def test_admin_requires_secure_transport_in_production(self):
        with override_settings(ACCOUNT_REQUIRE_HTTPS=True):
            self.assertEqual(self.client.get('/admin/login/').status_code,426)
            self.assertEqual(self.client.get('/admin/login/',secure=True).status_code,200)

class AdminBootstrapTests(TestCase):
    def test_new_separate_owner_private_credentials_and_no_reset(self):
        from django.core.management import call_command,CommandError
        from pathlib import Path
        from io import StringIO
        import tempfile
        customer=get_user_model().objects.create(username='existing-customer',password='!')
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'owner.txt';out=StringIO()
            call_command('bootstrap_store_admin',output=file,stdout=out)
            values=dict(line.split(': ',1) for line in file.read_text().splitlines() if ': ' in line)
            user=get_user_model().objects.get(username=values['Username'])
            self.assertTrue(user.is_staff and user.is_superuser)
            self.assertTrue(user.check_password(values['Password']))
            self.assertNotIn(values['Password'],out.getvalue())
            self.assertEqual(file.stat().st_mode&0o777,0o600)
            with self.assertRaises(CommandError):call_command('bootstrap_store_admin',output=file,stdout=StringIO())
            customer.refresh_from_db();self.assertFalse(customer.is_staff)

class CatalogCheckoutTests(TestCase):
    def test_live_stock_price_and_archiving_are_enforced(self):
        from .models import Address
        user=get_user_model().objects.create(username='stock-customer',password='!')
        address=Address.objects.create(user=user,recipient='test',phone='09123456789',province='test',city='test',postal_code='1234567890',street='test address')
        p=Product.objects.get(pk=1);p.is_active=True;p.stock=1;p.price=500000;p.save()
        self.client.force_login(user)
        def submit(key,quantity):return self.client.post('/api/checkout/',{'key':key,'address_id':address.pk,'items':[{'id':p.pk,'quantity':quantity,'price':1}]},content_type='application/json')
        self.assertEqual(submit('stock-limit-test',2).status_code,400)
        r=submit('stock-price-test',1);self.assertEqual(r.status_code,201);self.assertEqual(r.json()['total'],500000)
        p.is_active=False;p.save();self.assertEqual(submit('stock-archive-test',1).status_code,400)
