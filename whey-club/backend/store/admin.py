from datetime import timedelta
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.admin.forms import AdminAuthenticationForm
from .accounts import limited
from django.db.models import Sum,Count,Q,F,Value,BigIntegerField,ExpressionWrapper
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.html import format_html
from .models import Product,Order,OrderItem,CheckoutDraft,Category,PricingSettings

admin.site.site_header='مدیریت وی کلاب'
admin.site.site_title='وی کلاب'
admin.site.index_title='نمای کلی فروشگاه'
admin.site.index_template='admin/store_dashboard.html'

class RateLimitedAdminForm(AdminAuthenticationForm):
    def clean(self):
        if self.request and limited(self.request,prefix='admin'):
            raise forms.ValidationError('تلاش‌های ورود زیاد است؛ چند دقیقه دیگر تلاش کنید.')
        return super().clean()
admin.site.login_form=RateLimitedAdminForm

# Customer account management is a separate planned task; do not expose the default user editor.
for model in [get_user_model(),Group]:
    if admin.site.is_registered(model):admin.site.unregister(model)

def sales_condition(prefix=''):
    return Q(**{prefix+'payment_status':'paid',prefix+'paid_at__isnull':False})&~Q(**{prefix+'payment_reference':''})&~Q(**{prefix+'status':'cancelled'})

def product_report(queryset):
    return queryset.annotate(
        units_sold=Coalesce(Sum('order_lines__quantity',filter=sales_condition('order_lines__order__')),0),
        sales_total=Coalesce(Sum(ExpressionWrapper(F('order_lines__quantity')*F('order_lines__unit_price'),output_field=BigIntegerField()),filter=sales_condition('order_lines__order__')),0,output_field=BigIntegerField()))

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=('name','brand','protein_type','selling_price','stock','is_active','units_sold','sales_total')
    list_filter=('is_active','category_node','protein_type','flavor','brand')
    search_fields=('name','slug','brand')
    fieldsets=(
        ('مشخصات اصلی',{'fields':('name','slug','brand','category_node','protein_type','flavor','flavor_name','package_size','shipping_weight_grams','price','reference_aed_rate','selling_price','compare_at_price','protein_grams','servings')}),
        ('تصویر، موجودی و نمایش',{'fields':('image_url','color','stock','is_active','popular','is_demo')}),
        ('اطلاعات تکمیلی',{'fields':('description','nutrition','ingredients','allergens','usage','irc_code','batch','expiry','brand_line','goals'),'classes':('collapse',)}),
        ('زمان تغییر',{'fields':('updated_at',),'classes':('collapse',)}),
    )
    readonly_fields=('updated_at','selling_price')
    list_per_page=30
    def get_readonly_fields(self,request,obj=None):
        return ('updated_at','selling_price','slug') if obj else ('updated_at','selling_price')
    def get_queryset(self,request):
        qs=super().get_queryset(request)
        if request.user.has_perm('store.view_order'):return product_report(qs)
        return qs.annotate(units_sold=Value(None,output_field=BigIntegerField()),sales_total=Value(None,output_field=BigIntegerField()))
    @admin.display(description='تعداد فروش تأییدشده',ordering='units_sold')
    def units_sold(self,obj):return obj.units_sold if obj.units_sold is not None else '—'
    @admin.display(description='فروش کالا (تومان)',ordering='sales_total')
    def sales_total(self,obj):return f'{obj.sales_total:,}' if obj.sales_total is not None else '—'
    def has_delete_permission(self,request,obj=None):
        # Archive published products instead of breaking carts and historical order links.
        return False

class OrderItemInline(admin.TabularInline):
    model=OrderItem
    fields=('product','product_name','quantity','unit_price')
    readonly_fields=fields
    extra=0
    can_delete=False
    def has_add_permission(self,request,obj=None):return False
    def has_change_permission(self,request,obj=None):return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=('__str__','user','payment_status','status','total','created_at','tracking_code')
    list_filter=('payment_status','status','created_at')
    search_fields=('=id','user__email','user__username','tracking_code','payment_reference')
    date_hierarchy='created_at'
    readonly_fields=('user','source_draft','shipping_address','total','payment_status','payment_reference','paid_at','created_at','updated_at')
    fields=readonly_fields+('status','tracking_code','staff_notes')
    inlines=[OrderItemInline]
    list_select_related=('user',)
    @admin.display(description='نشانی ارسال')
    def shipping_address(self,obj):
        a=obj.address if isinstance(obj.address,dict) else {}
        return format_html('<div style="line-height:2"><strong>{}</strong><br>{}، {}<br>{}<br>موبایل: {}<br>کد پستی: {}</div>',a.get('recipient','—'),a.get('province','—'),a.get('city','—'),a.get('street','—'),a.get('phone','—'),a.get('postal_code','—'))
    def has_add_permission(self,request):return False
    def has_delete_permission(self,request,obj=None):return False

@admin.register(CheckoutDraft)
class CheckoutDraftAdmin(admin.ModelAdmin):
    list_display=('id','user','total','status','created_at')
    list_filter=('status','created_at')
    search_fields=('=id','user__email','user__username')
    readonly_fields=('user','key','items','address','total','status','created_at')
    fields=readonly_fields
    list_select_related=('user',)
    def has_add_permission(self,request):return False
    def has_change_permission(self,request,obj=None):return False
    def has_delete_permission(self,request,obj=None):return False

_original_index=admin.site.index
def dashboard(request,extra_context=None):
    context=dict(extra_context or {})
    period=request.GET.get('period','all');period=period if period in ['7','30','all'] else 'all'
    context.update({'sales_period':period,'can_report':request.user.has_perm('store.view_order'),'can_products':request.user.has_perm('store.view_product')})
    if context['can_report']:
        orders=Order.objects.verified_sales()
        if period!='all':orders=orders.filter(paid_at__gte=timezone.now()-timedelta(days=int(period)))
        context['summary']=orders.aggregate(sales_total=Coalesce(Sum('total'),0),paid_orders=Count('id'))
        context['summary']['units']=OrderItem.objects.filter(order__in=orders).aggregate(n=Coalesce(Sum('quantity'),0))['n']
        context['active_orders']=Order.objects.verified_sales().filter(status__in=['pending','processing','shipped']).count()
        context['recent_orders']=Order.objects.select_related('user').order_by('-created_at')[:8]
        if context['can_products']:
            condition=sales_condition('order_lines__order__')
            if period!='all':condition&=Q(order_lines__order__paid_at__gte=timezone.now()-timedelta(days=int(period)))
            context['product_sales']=Product.objects.annotate(units_sold=Coalesce(Sum('order_lines__quantity',filter=condition),0),sales_total=Coalesce(Sum(ExpressionWrapper(F('order_lines__quantity')*F('order_lines__unit_price'),output_field=BigIntegerField()),filter=condition),0,output_field=BigIntegerField())).order_by('-units_sold','name')[:20]
    if request.user.has_perm('store.view_checkoutdraft'):
        context['unpaid_drafts']=CheckoutDraft.objects.filter(status='awaiting_gateway').count()
    return _original_index(request,extra_context=context)
admin.site.index=dashboard

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=('name','parent','position','route')
    list_editable=('position',)
    fields=('name','slug','parent','position','route')
    readonly_fields=('route',)
    prepopulated_fields={'slug':('name',)}
    @admin.display(description='نشانی دسته (خودکار)')
    def route(self,obj):return obj.get_absolute_url() if obj.pk else 'پس از ذخیره ساخته می‌شود'

@admin.register(PricingSettings)
class PricingSettingsAdmin(admin.ModelAdmin):
    fields=('aed_rate',)
    def has_add_permission(self,request):return not PricingSettings.objects.exists() and super().has_add_permission(request)
    def has_delete_permission(self,request,obj=None):return False
