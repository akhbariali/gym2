import json, re
from functools import wraps
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .models import Address, CheckoutDraft, Product
from .views import load

def fail(message,status=400): return JsonResponse({'error':message},status=status)
def protected(fn):
    @wraps(fn)
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:return fail('ابتدا وارد حساب کاربری شوید.',401)
        return fn(request,*args,**kwargs)
    return wrapper

def data(request):
    try:
        result=json.loads(request.body)
        if not isinstance(result,dict):raise ValueError()
        return result
    except (ValueError,UnicodeError):raise ValueError('اطلاعات ارسالی معتبر نیست.')

def limited(request,prefix='auth'):
    # A single Gunicorn worker shares this cache across its threads. Never log credentials.
    import hashlib
    key=prefix+':' +hashlib.sha256(request.META.get('HTTP_X_FORWARDED_FOR',request.META.get('REMOTE_ADDR','')).encode()).hexdigest()
    if cache.add(key,1,300):return False
    try:return cache.incr(key)>20
    except ValueError:return False

def user_json(user):return {'id':user.id,'name':user.first_name,'email':user.email}
def address_json(a):return {k:getattr(a,k) for k in ['id','recipient','phone','province','city','postal_code','street','latitude','longitude']}

@require_GET
def session(request):
    return JsonResponse({'user':user_json(request.user) if request.user.is_authenticated else None,'csrfToken':get_token(request),'payment_available':False})

@require_POST
def register(request):
    if limited(request):return fail('لطفاً چند دقیقه دیگر تلاش کنید.',429)
    try:
        d=data(request);email=str(d.get('email','')).strip().lower();name=str(d.get('name','')).strip();password=d.get('password','')
        validate_email(email)
        if len(email)>150 or not name or len(name)>120 or not isinstance(password,str) or len(password)>128:raise ValueError('اطلاعات ثبت‌نام معتبر نیست.')
        User=get_user_model();u=User(username=email,email=email,first_name=name)
        validate_password(password,u)
        with transaction.atomic():
            u.set_password(password);u.save()
        login(request,u)
        return JsonResponse({'user':user_json(u)},status=201)
    except ValidationError as e:return fail(' '.join(e.messages))
    except IntegrityError:return fail('این ایمیل قبلاً ثبت شده است.',409)
    except ValueError as e:return fail(str(e))

@require_POST
def sign_in(request):
    if limited(request):return fail('لطفاً چند دقیقه دیگر تلاش کنید.',429)
    try:d=data(request)
    except ValueError as e:return fail(str(e))
    password=d.get('password','')
    if not isinstance(password,str) or len(password)>128:return fail('اطلاعات ورود معتبر نیست.')
    u=authenticate(request,username=str(d.get('email','')).strip().lower(),password=password)
    if not u:return fail('ایمیل یا رمز عبور درست نیست.',401)
    login(request,u);return JsonResponse({'user':user_json(u)})

@require_POST
def sign_out(request):
    logout(request);return JsonResponse({'ok':True})

@require_http_methods(['GET','POST'])
@protected
def addresses(request):
    if request.method=='GET':return JsonResponse({'results':[address_json(a) for a in Address.objects.filter(user=request.user).order_by('-id')]})
    try:
        d=data(request);fields={}
        for key,limit in [('recipient',120),('phone',11),('province',80),('city',80),('postal_code',10),('street',500)]:
            value=str(d.get(key,'')).strip().translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩','01234567890123456789'))
            if not value or len(value)>limit:raise ValueError('همه فیلدهای نشانی را کامل و صحیح وارد کنید.')
            fields[key]=value
        if not re.fullmatch(r'09[0-9]{9}',fields['phone']) or not re.fullmatch(r'[0-9]{10}',fields['postal_code']):raise ValueError('شماره موبایل یا کد پستی معتبر نیست.')
        lat,lon=d.get('latitude'),d.get('longitude')
        if (lat is None)!=(lon is None):raise ValueError('موقعیت نقشه کامل نیست.')
        if lat is not None:
            lat,lon=float(lat),float(lon)
            if not (-90<=lat<=90 and -180<=lon<=180):raise ValueError('موقعیت نقشه معتبر نیست.')
        if Address.objects.filter(user=request.user).count()>=20:return fail('حداکثر ۲۰ نشانی قابل ذخیره است.')
        a=Address.objects.create(user=request.user,latitude=lat,longitude=lon,**fields)
        return JsonResponse(address_json(a),status=201)
    except (ValueError,TypeError) as e:return fail(str(e))

@require_POST
@protected
def remove_address(request,pk):
    count,_=Address.objects.filter(pk=pk,user=request.user).delete()
    return JsonResponse({'ok':True}) if count else fail('نشانی پیدا نشد.',404)

@require_POST
@protected
def checkout(request):
    try:
        d=data(request);key=d.get('key','');items=d.get('items')
        if not isinstance(key,str) or not re.fullmatch(r'[a-zA-Z0-9-]{8,80}',key):raise ValueError('شناسه درخواست معتبر نیست.')
        address=Address.objects.filter(pk=d.get('address_id'),user=request.user).first()
        if not address:return fail('یک نشانی متعلق به حساب خود انتخاب کنید.',400)
        if not isinstance(items,list) or not 1<=len(items)<=30:raise ValueError('سبد خرید معتبر نیست.')
        catalog={p.pk:p.as_catalog() for p in Product.objects.filter(is_active=True)};normalized=[];seen=set();total=0
        for item in items:
            pid=item.get('id');qty=item.get('quantity')
            if type(pid)!=int or pid not in catalog or pid in seen or type(qty)!=int or not 1<=qty<=99:raise ValueError('تعداد یا محصول سبد خرید معتبر نیست.')
            p=catalog[pid]
            if p['stock'] is not None and qty>p['stock']:raise ValueError('موجودی محصول کافی نیست.')
            seen.add(pid);total+=p['price']*qty
            normalized.append({'id':pid,'name':p['name'],'quantity':qty,'price':p['price']})
        normalized.sort(key=lambda p:p['id']);snapshot=address_json(address)
        with transaction.atomic():
            draft,created=CheckoutDraft.objects.get_or_create(user=request.user,key=key,defaults={'items':normalized,'address':snapshot,'total':total})
        if draft.items!=normalized or draft.address!=snapshot:return fail('سبد تغییر کرده است؛ دوباره ادامه دهید.',409)
        return JsonResponse({'id':draft.id,'status':draft.status,'total':draft.total,'payment_available':False,'payment_url':None,'message':'درگاه پرداخت هنوز فعال نیست. هیچ مبلغی دریافت نشده و سفارش نهایی ثبت نشده است.'},status=201 if created else 200)
    except (ValueError,TypeError,AttributeError,ValidationError) as e:return fail('سبد یا نشانی معتبر نیست.')
