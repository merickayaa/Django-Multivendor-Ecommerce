"""
URL configuration for eCommercePrj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.products_list_view, name='products_list'),
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/<cid>/', views.category_product_list_view, name='category_product_list'),
    path('vendor/<vid>/', views.vendor_detail_view, name='vendors_detail'),
    path('vendor/<vid>/profile', views.vendor_about_view, name='vendors_about'),
    path('vendor/<vid>/products', views.vendor_products_list_view, name='vendors_products'),
    path('product/<pid>', views.product_detail_view, name='products_detail'),
    path('products/tag/<slug:tag_slug>/', views.tag_list_view, name='tags'),
    path('search/', views.search_view, name='search'),
    path('products/filter/', views.filter_view, name='filter'),




] 
