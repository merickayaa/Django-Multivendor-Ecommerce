from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import format_html
from userauths.models import User
from datetime import datetime,timezone
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models import Avg
from django.utils.functional import cached_property
from django.conf import settings

# Create your models here.

STATUS_CHOICE = (
    ("process", "Processing"),
    ("shipped", "Shipping"),
    ("delivered", "Delivered"),
)

ORDER_STATUS_CHOICE = (
    ("process", "Processing"),
    ("completed", "Completed"),
#   ("İptal", "Delivered"),
)

STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In_Review"),
    ("published", "Published"),
)

PAYMENT_STATE_CHOICE = (
    ("pending", "Bekliyor"),
    ("paid", "Ödendi"),
    ("failed", "Başarısız"),
)

RATING = (
    (1, "✮☆☆☆☆"),
    (2, "✮✮☆☆☆"),
    (3, "✮✮✮☆☆"),
    (4, "✮✮✮✮☆"),
    (5, "✮✮✮✮✮"),

)

def user_directory_path(instance, filename):
    return "user_{0}/{1}".format(instance.user.id, filename)



    
class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default="Category Name")
    image = models.ImageField(upload_to="Category")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return format_html('<img src="{}" width="50" height="50"/>', self.image.url)
    
    def __str__(self):
        return self.title
    
class Brand(models.Model):
    bid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="bra", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default="Brand Name")
    categories = models.ManyToManyField(Category, blank=True, related_name="brands")
    class Meta:
        verbose_name_plural = "Brands"
    def __str__(self):
        return self.title
    
# class Tags(models.Model):
#     pass

class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="ven", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default="Vendor Name")
    image = models.ImageField(upload_to=user_directory_path)
    description = RichTextUploadingField(default="Vendor Desc")
    address = models.CharField(max_length=100, default="Istanbul")
    country = models.CharField(max_length=200)
    contact = models.CharField(max_length=100, default="+90 555 555 55 55")
    chat_resp_time = models.CharField(max_length=100, default="100")
    shipping_on_time = models.CharField(max_length=100, default="100")
    authentic_rating = models.CharField(max_length=100, default="100")
    days_return = models.CharField(max_length=100, default="100")
    warranty_period = models.CharField(max_length=100, default="100")
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    class Meta:
        verbose_name_plural = "Vendors"

    def vendor_image(self):
        return format_html('<img src="{}" width="50" height="50"/>', self.image.url)
    def time_since_joined(self):
        now = datetime.now(timezone.utc)
        days = (now - self.date).days

        if days < 30:
            return f"{days} gün"
        elif days < 365:
            months = days // 30
            return f"{months} ay"
        else:
            years = days // 365
            return f"{years} yıl"
        
    def __str__(self):
        return self.title
    
class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default="Product Name")
    image = models.ImageField(upload_to=user_directory_path)
    description = RichTextUploadingField(null=True,blank=True, default="This is a Product")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name="brand")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, related_name="vendor")
    price = models.DecimalField(max_digits= 12, decimal_places= 2, default=1.99)
    specifications = RichTextUploadingField(null=True,blank=True, default="This is a Product")
    # stock_count = models.CharField(max_length=100, default="10", null=True, blank=True)
    # mfd = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    tags = TaggableManager(blank=True)
    product_status = models.CharField(choices=STATUS, max_length=10, default="in_review")
    # in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    # digital = models.BooleanField(default=False)
    sku = ShortUUIDField(unique=True, length=4, max_length=10, prefix="sku", alphabet="1234567890")
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    
    class Meta:
        verbose_name_plural = "Products"

    @cached_property
    def average_rating(self):
        if hasattr(self, "avg_rating"):            # annotate ile geldiyse sorgu atma
            return self.avg_rating or 0
        avg = self.productreview_set.aggregate(avg=Avg("rating"))["avg"]
        return avg or 0
    @property
    def full_stars(self):
        return range(int(self.average_rating))
    @property
    def half_star(self):
        return self.average_rating - int(self.average_rating) >= 0.5
    @property
    def empty_stars(self):
        return range(5 - int(self.average_rating) - int(self.half_star))
    

    def product_image(self):
        print(self.image.url)
        return format_html('<img src="{}" width="50" height="50" />', self.image.url)
        

    def __str__(self):
        return self.title
    
class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images")
    product = models.ForeignKey(Product, related_name="product_images", on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        verbose_name_plural = "Product Images"

                                            
                                            ########### Cart Order OrderItems Adress #######################
                                            ########### Cart Order OrderItems Adress #######################
                                            ########### Cart Order OrderItems Adress #######################
                                            ########### Cart Order OrderItems Adress #######################
                                            ########### Cart Order OrderItems Adress #######################



class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name="product_cart", null=True)
    # title = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    # price = models.DecimalField(max_digits=10, decimal_places=2)
    # image = models.CharField(max_length=200)
    # vendor = models.CharField(max_length=100)
    # added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}"

class Address(models.Model):
    # aid = ShortUUIDField(unique=True, length=10, max_length=20,prefix="loc", alphabet="abcdefgh12345")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    title = models.CharField(max_length=100, default="Home")
    phone = models.CharField(max_length=300,null=True)
    address = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Address"

class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    oid = ShortUUIDField(unique=True, length=4, max_length=10, alphabet="1234567890")
    invoice_no = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=1.99)
    paid_status = models.BooleanField(default=False)
    payment_status = models.CharField(choices=PAYMENT_STATE_CHOICE, max_length=20, default="pending")
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=ORDER_STATUS_CHOICE, max_length=10, default="process")
    shipping_title = models.CharField(max_length=100)
    shipping_phone = models.CharField(max_length=300)
    shipping_country = models.CharField(max_length=100)
    shipping_address = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = "Cart Order"

    def is_completed(self):
        if not self.cartorderitems_set.exclude(product_status = "delivered").exists() == True:
            return "Completed"
        else:
            return "Process"

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=200, default="process")
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=1.99)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=1.99)
    class Meta:
        verbose_name_plural = "Cart Order Items"
    def order_image(self):
        return format_html('<img src="{}{}" width="50" height="50"/>', settings.MEDIA_URL, self.image)



                                            ########### Product Review, Wishlist, Adress #######################
class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return self.product.title
    
    def get_rating(self):
        return self.rating
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    rating = models.IntegerField(choices=RATING, default=None, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return self.product.title
    
