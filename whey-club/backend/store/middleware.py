from django.conf import settings
from django.http import JsonResponse
class SecureAccountMiddleware:
    def __init__(self,get_response):self.get_response=get_response
    def __call__(self,request):
        if settings.ACCOUNT_REQUIRE_HTTPS and (request.path.startswith('/api/account/') or request.path=='/api/checkout/' or request.path=='/admin' or request.path.startswith('/admin/')) and not request.is_secure():
            return JsonResponse({'error':'برای حفظ امنیت حساب و نشانی، استفاده از اتصال HTTPS لازم است.'},status=426)
        return self.get_response(request)
