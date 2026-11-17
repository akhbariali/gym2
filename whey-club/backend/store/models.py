from django.conf import settings
from django.db import models

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
