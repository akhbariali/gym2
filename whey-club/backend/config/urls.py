from django.urls import path
from django.contrib import admin
from store import views, accounts
urlpatterns = [path('sitemap.xml', views.sitemap), path('products/<slug:slug>/', views.product_page), path('admin/', admin.site.urls), path('api/products/<slug:slug>/', views.product_detail), path('api/products/', views.products), path('api/articles/', views.articles), path('api/articles/<slug:slug>/', views.article), path('api/health/', views.health)]

urlpatterns += [
 path('api/account/session/', accounts.session),
 path('api/account/register/', accounts.register),
 path('api/account/login/', accounts.sign_in),
 path('api/account/logout/', accounts.sign_out),
 path('api/account/addresses/', accounts.addresses),
 path('api/account/addresses/<int:pk>/delete/', accounts.remove_address),
 path('api/checkout/', accounts.checkout),
]
