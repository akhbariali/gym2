from django.conf import settings
from django.db import models
from .categories import Category, CategoryRoute

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recipient = models.CharField(max_length=120)
    phone = models.CharField(max_length=11)
    province = models.CharField(max_length=80)
    city = models.CharField(max_length=80)
    postal_code = models.CharField(max_length=10)
    street = models.CharField(max_length=500)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

class CheckoutDraft(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    key = models.CharField(max_length=80)
    items = models.JSONField()
    address = models.JSONField()
    total = models.PositiveBigIntegerField()
    status = models.CharField(max_length=30, default='awaiting_gateway')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','key'], name='unique_checkout_key')]
        verbose_name='پیش‌نویس خرید'
        verbose_name_plural='پیش‌نویس‌های خرید'
    def __str__(self):return f'پیش‌نویس {self.pk}'

class PricingSettings(models.Model):
    id=models.PositiveSmallIntegerField(primary_key=True,default=1,editable=False)
    aed_rate=models.PositiveIntegerField('قیمت هر درهم (تومان)',default=77000)
    class Meta:
        verbose_name='تنظیمات قیمت درهم'
        verbose_name_plural='تنظیمات قیمت درهم'
        constraints=[models.CheckConstraint(condition=models.Q(id=1),name='single_pricing_settings'),models.CheckConstraint(condition=models.Q(aed_rate__gt=0),name='positive_aed_rate')]
    def __str__(self):return 'نرخ درهم و قیمت محصولات'
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.aed_rate:raise ValidationError({'aed_rate':'نرخ درهم باید بیشتر از صفر باشد.'})

class Product(models.Model):
    class ProteinType(models.TextChoices):
        ISOLATE='isolate','وی ایزوله'
        CONCENTRATE='concentrate','وی کنسانتره'
        BLEND='blend','وی ترکیبی'
        CREATINE='creatine','کراتین'
        SHAKER='shaker','شیکر / لوازم جانبی'
    category_node=models.ForeignKey(Category,on_delete=models.PROTECT,null=True,blank=True,related_name='products',verbose_name='دسته محصول')
    name=models.CharField('نام محصول',max_length=180)
    slug=models.SlugField('نشانی انگلیسی محصول',max_length=180,unique=True,blank=True,help_text='اختیاری؛ اگر خالی باشد نشانی یکتا ساخته می‌شود. بعد از ثبت ثابت می‌ماند.')
    brand=models.CharField('برند',max_length=100,default='WHEY CLUB')
    brand_line=models.CharField('عنوان برند / سری محصول (اختیاری)',max_length=180,blank=True)
    goals=models.JSONField('برچسب‌های هدف (اختیاری)',default=list,blank=True)
    protein_type=models.CharField('نوع محصول',max_length=20,choices=ProteinType.choices)
    flavor=models.CharField('شناسه طعم',max_length=30,choices=[('chocolate','شکلات'),('vanilla','وانیل'),('strawberry','توت‌فرنگی'),('coffee','قهوه'),('plain','بدون طعم'),('none','بدون طعم / لوازم جانبی'),('other','سایر')])
    flavor_name=models.CharField('نام طعم',max_length=80)
    package_size=models.CharField('وزن بسته',max_length=80)
    price=models.PositiveBigIntegerField('قیمت (تومان)')
    reference_aed_rate=models.PositiveIntegerField('نرخ درهم مبنای قیمت (تومان)',null=True,blank=True,help_text='خالی: قیمت ثابت. قیمت فعلی = قیمت مبنا × نرخ روز ÷ نرخ مبنا؛ گرد به نزدیک‌ترین ۱۰٬۰۰۰ تومان.')
    shipping_weight_grams=models.PositiveIntegerField('وزن ارسال با بسته‌بندی (گرم)',null=True,blank=True)
    compare_at_price=models.PositiveBigIntegerField('قیمت قبل از تخفیف (تومان)',null=True,blank=True)
    protein_grams=models.PositiveSmallIntegerField('پروتئین در هر وعده (گرم)')
    servings=models.PositiveIntegerField('تعداد وعده در بسته',default=30)
    description=models.TextField('توضیحات',blank=True)
    nutrition=models.JSONField('اطلاعات تغذیه در هر وعده',default=dict,blank=True,help_text='اختیاری؛ مقادیر عددی مانند {"scoop":30,"kcal":110,"carbs":1,"fat":0.5,"sugar":0.5}')
    ingredients=models.TextField('ترکیبات',blank=True)
    allergens=models.CharField('آلرژن‌ها',max_length=300,blank=True)
    usage=models.TextField('روش مصرف روی برچسب',blank=True)
    irc_code=models.CharField('کد IRC روی بسته',max_length=80,blank=True)
    batch=models.CharField('سری ساخت',max_length=80,blank=True)
    expiry=models.CharField('تاریخ انقضا روی بسته',max_length=80,blank=True)
    is_demo=models.BooleanField('محصول آزمایشی',default=False)
    image_url=models.URLField('آدرس HTTPS تصویر محصول',max_length=1000,blank=True)
    color=models.CharField('تصویر پیش‌فرض بسته',max_length=20,default='lime',choices=[(x,x) for x in ['lime','cream','pink','brown','coffee','white','creatine','shaker']])
    stock=models.PositiveIntegerField('موجودی (خالی = کنترل موجودی غیرفعال)',null=True,blank=True)
    is_active=models.BooleanField('نمایش در فروشگاه',default=False)
    popular=models.BooleanField('محصول محبوب',default=False)
    updated_at=models.DateTimeField('آخرین تغییر',auto_now=True)
    class Meta:
        verbose_name='محصول'
        verbose_name_plural='محصولات'
        ordering=['id']
        constraints=[models.CheckConstraint(condition=models.Q(price__gt=0),name='product_positive_price'),models.CheckConstraint(condition=(models.Q(protein_type__in=['shaker','creatine'])|models.Q(servings__gt=0)),name='product_positive_servings')]
    def __str__(self):return self.name
    def save(self,*args,**kwargs):
        if not self.slug:
            from uuid import uuid4
            from django.utils.text import slugify
            self.slug=(slugify(self.name) or slugify(self.brand) or 'whey')[:150]+'-'+uuid4().hex[:10]
        return super().save(*args,**kwargs)
    def get_absolute_url(self):return '/products/'+self.slug+'/'
    def clean(self):
        from django.core.exceptions import ValidationError
        errors={}
        if self.price and self.price>1000000000000:errors['price']='قیمت واردشده بیش از محدوده مجاز است.'
        if not self.price:errors['price']='قیمت باید بیشتر از صفر باشد.'
        if self.protein_type in ['isolate','concentrate','blend'] and (not self.protein_grams or self.protein_grams>100):errors['protein_grams']='پروتئین هر وعده باید بین ۱ تا ۱۰۰ گرم باشد.'
        if self.protein_type not in ['shaker','creatine'] and not self.servings:errors['servings']='تعداد وعده باید بیشتر از صفر باشد.'
        if self.compare_at_price is not None and self.compare_at_price<=self.price:errors['compare_at_price']='قیمت قبلی باید بیشتر از قیمت فعلی باشد.'
        if self.image_url and not self.image_url.startswith('https://'):errors['image_url']='تصویر باید از آدرس HTTPS بارگذاری شود.'
        if self.goals is None:self.goals=[]
        import re
        if not isinstance(self.goals,list) or len(self.goals)>30 or any(not isinstance(v,str) or not re.fullmatch(r'[a-z][a-z0-9_-]{0,30}',v) for v in self.goals):errors['goals']='برچسب‌ها باید فهرستی از شناسه‌های انگلیسی کوتاه باشند.'
        if self.nutrition is None:self.nutrition={}
        import math
        if not isinstance(self.nutrition,dict) or any(k not in ['scoop','kcal','protein','carbs','fat','sugar','creatine'] or type(v) not in (int,float) or not math.isfinite(v) or v<0 for k,v in self.nutrition.items()):errors['nutrition']='مقادیر تغذیه باید عددی و نامنفی باشند و فقط کلیدهای scoop، kcal، protein، carbs، fat، sugar مجازند.'
        if self.reference_aed_rate==0:errors['reference_aed_rate']='نرخ مبنا باید بیشتر از صفر باشد.'
        if self.shipping_weight_grams==0:errors['shipping_weight_grams']='وزن ارسال باید بیشتر از صفر باشد.'
        if errors:raise ValidationError(errors)
    @property
    def selling_price(self):
        return self.convert_price(self.price)
    def convert_price(self,value):
        if not value or not self.reference_aed_rate:return value
        from decimal import Decimal, ROUND_HALF_UP
        rate=PricingSettings.objects.values_list('aed_rate',flat=True).get(pk=1)
        return max(10000,int((Decimal(value)*rate/self.reference_aed_rate/10000).quantize(Decimal('1'),rounding=ROUND_HALF_UP))*10000)
    def as_catalog(self):
        return {'id':self.pk,'category_id':self.category_node_id,'slug':self.slug,'name':self.name,'en':self.brand_line or self.brand,'goals':self.goals,'brand':self.brand,'type':self.protein_type,'flavor':self.flavor,'flavorName':self.flavor_name,'color':self.color,'size':self.package_size,'price':self.selling_price,'old':self.convert_price(self.compare_at_price) or 0,'protein':self.protein_grams,'servings':self.servings,'popular':self.popular,'description':self.description,'image_url':self.image_url,'stock':self.stock,'shipping_weight_grams':self.shipping_weight_grams,'available':self.stock is None or self.stock>0,'category':('accessory' if self.protein_type=='shaker' else 'creatine' if self.protein_type=='creatine' else 'whey'),'nutrition':dict(self.nutrition or {},protein=self.protein_grams),'ingredients':self.ingredients,'allergens':self.allergens,'usage':self.usage,'irc':self.irc_code,'batch':self.batch,'expiry':self.expiry,'pitch':self.description,'is_demo':self.is_demo}

class OrderQuerySet(models.QuerySet):
    def verified_sales(self):
        return self.filter(payment_status='paid',paid_at__isnull=False).exclude(payment_reference='').exclude(status='cancelled')

class Order(models.Model):
    PAYMENT_CHOICES=[('unpaid','پرداخت نشده'),('paid','پرداخت تأیید شده'),('refunded','مسترد شده')]
    STATUS_CHOICES=[('pending','جدید'),('processing','در حال آماده‌سازی'),('shipped','ارسال شده'),('delivered','تحویل شده'),('cancelled','لغو شده')]
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,verbose_name='خریدار')
    source_draft=models.OneToOneField(CheckoutDraft,on_delete=models.PROTECT,null=True,blank=True,verbose_name='پیش‌نویس اولیه')
    address=models.JSONField('نشانی ارسال ثبت‌شده')
    total=models.PositiveBigIntegerField('مبلغ سفارش (تومان)')
    payment_status=models.CharField('وضعیت پرداخت',max_length=20,choices=PAYMENT_CHOICES,default='unpaid')
    payment_reference=models.CharField('شناسه تأیید پرداخت',max_length=160,blank=True)
    paid_at=models.DateTimeField('زمان تأیید پرداخت',null=True,blank=True)
    status=models.CharField('وضعیت ارسال',max_length=20,choices=STATUS_CHOICES,default='pending')
    tracking_code=models.CharField('کد رهگیری مرسوله',max_length=120,blank=True)
    staff_notes=models.TextField('یادداشت داخلی',blank=True)
    created_at=models.DateTimeField('زمان ایجاد',auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects=OrderQuerySet.as_manager()
    class Meta:
        verbose_name='سفارش'
        verbose_name_plural='سفارش‌ها'
        ordering=['-created_at']
    def __str__(self):return f'WC-{self.pk:06d}' if self.pk else 'سفارش جدید'
    @property
    def verified_paid(self):return self.payment_status=='paid' and bool(self.payment_reference) and self.paid_at is not None
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.status in ['processing','shipped','delivered'] and not self.verified_paid:
            raise ValidationError({'status':'سفارش بدون پرداخت تأییدشده قابل آماده‌سازی یا ارسال نیست.'})

class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='lines')
    product=models.ForeignKey(Product,on_delete=models.PROTECT,related_name='order_lines',verbose_name='محصول')
    product_name=models.CharField('نام محصول هنگام خرید',max_length=180)
    quantity=models.PositiveIntegerField('تعداد')
    unit_price=models.PositiveBigIntegerField('قیمت واحد هنگام خرید (تومان)')
    class Meta:
        verbose_name='قلم سفارش'
        verbose_name_plural='اقلام سفارش'
        constraints=[models.CheckConstraint(condition=models.Q(quantity__gt=0),name='order_item_positive_quantity')]
    def __str__(self):return self.product_name
