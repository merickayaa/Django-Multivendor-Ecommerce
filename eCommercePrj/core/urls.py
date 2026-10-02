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
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('update-cart-item/', views.update_cart_item, name='update_cart_item'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('create-order/', views.create_order_view, name='create_order'),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('payment-completed/', views.payment_completed_view, name='payment_completed'),
    path('payment/waiting/', views.payment_waiting_view, name='payment_waiting'),
    path('payment-failed/', views.payment_failed_view, name='payment_failed'),
    path('dashboard/', views.customer_dashboard, name='dashboard'),
    path('dashboard/orders', views.customer_orders, name='orders'),
    path('dashboard/order-detail/<str:oid>', views.order_detail, name='order_detail'),
    path('make-review', views.make_review, name='make_review'),
    path('dashboard/wishlist', views.customer_wishlist, name='wishlist'),
    path('dashboard/settings', views.customer_settings, name='settings'),
    path('dashboard/addresses', views.customer_address, name='addresses'),
    path('make-default-address/', views.make_address_default, name='make-default-address'),
    path('delete-address/', views.delete_address, name='delete_address'),
    path('edit-address/', views.edit_address, name='edit_address'),
    # path('dashboard/addresses/address/update/<aid>/', views.update_customer_address, name='update_address'),
    path('wishlist/', views.customer_wishlist, name='wishlist'),
    path('add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-to-wishlist/', views.remove_to_wishlist, name='remove_to_wishlist'),
    path('contact-us/', views.contactUs_view, name='contactUs'),
    path('ajax-contact-form/', views.ajax_contact, name='ajax-contact-form'),
    path("change_password/", views.change_password, name="change_password"),
    path("apply_for_vendor/", views.apply_for_vendor, name="apply_for_vendor"),
    path("vendor_success/", views.vendor_success, name="vendor_success"),











] 
