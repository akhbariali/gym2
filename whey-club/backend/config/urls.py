from django.urls import path
from store import views
urlpatterns = [path('api/products/', views.products), path('api/articles/', views.articles), path('api/articles/<slug:slug>/', views.article), path('api/health/', views.health)]
