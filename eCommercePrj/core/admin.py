from django.contrib import admin
from core.models import Product,Category,Vendor,CartOrderItems,CartOrder, Wishlist, Address, ProductImages, ProductReview, Brand, Cart
# Register your models here.
class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_editable = ['featured', 'product_status']
    list_display = ['vendor','title', 'product_image', 'price', 'category', 'featured', 'product_status']
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title','category_image']
class BrandAdmin(admin.ModelAdmin):
    list_display = ['title']

class VendorAdmin(admin.ModelAdmin):
    list_display = ['title','vendor_image']

class CartOrderAdmin(admin.ModelAdmin):
    list_editable = ['paid_status', 'product_status']
    list_display = ['user', 'oid', 'invoice_no', 'price', 'paid_status','order_date', 'product_status']

class CartOrderItemsAdmin(admin.ModelAdmin):
    list_display = ['order', 'item','image', 'quantity', 'price', 'total']

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user','product', 'review', 'rating']

class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user','product', 'date']

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'address', 'phone', 'status']

class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'quantity']

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderItems, CartOrderItemsAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Cart, CartAdmin)

