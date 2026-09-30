import time
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from userauths.models import User, ContactUs,Profile
from core.models import Product,Category,Vendor,CartOrderItems,CartOrder, Wishlist, Address, ProductImages, ProductReview,Brand, Cart
from taggit.models import Tag
from django.db.models import Avg, Q
import math
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib.auth.decorators import login_required
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.db import transaction
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.serializers import serialize
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.models import PayPalIPN
from paypal.standard.ipn.signals import valid_ipn_received

def baseView(view_func):
    def wrapper(request, *args, **kwargs):
        # code to be executed before the view
        for product in args:
            average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
            average_rating = average_rating['rating'] or 0.0
            full_stars = math.floor(average_rating)
            half_star = 1 if (average_rating - full_stars) >= 0.5 else 0
            empty_stars = 5 - full_stars - half_star
            product.full_stars = ['★'] * full_stars
            product.half_star = ['☆'] * half_star
            product.empty_stars = ['☆'] * empty_stars
            product.average_rating = average_rating
        response = view_func(request, *args, **kwargs)
        # code to be executed after the view
        return response
    return wrapper
# Create your views here.
@baseView
def index(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
        products = Product.objects.filter(product_status="published").exclude(vendor=vendor)
        featured_products = Product.objects.filter(product_status="published", featured = True).exclude(vendor=vendor)
        last_products = Product.objects.filter(product_status="published").exclude(vendor=vendor).order_by("-date")[:3]
    except:
        products = Product.objects.filter(product_status="published")
        featured_products = Product.objects.filter(product_status="published", featured = True)
        last_products = Product.objects.filter(product_status="published").order_by("-date")[:3]
    for product in products:
        average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
        average_rating = average_rating['rating'] or 0.0
        full_stars = math.floor(average_rating)
        half_star = 1 if (average_rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        product.full_stars = ['★'] * full_stars
        product.half_star = ['☆'] * half_star
        product.empty_stars = ['☆'] * empty_stars
        product.average_rating = average_rating
    for product in featured_products:
        average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
        average_rating = average_rating['rating'] or 0.0
        full_stars = math.floor(average_rating)
        half_star = 1 if (average_rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        product.full_stars = ['★'] * full_stars
        product.half_star = ['☆'] * half_star
        product.empty_stars = ['☆'] * empty_stars
        product.average_rating = average_rating
    for product in last_products:
        average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
        average_rating = average_rating['rating'] or 0.0
        full_stars = math.floor(average_rating)
        half_star = 1 if (average_rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        product.full_stars = ['★'] * full_stars
        product.half_star = ['☆'] * half_star
        product.empty_stars = ['☆'] * empty_stars
        product.average_rating = average_rating
    context = {
        'products':products,
        'last_products':last_products,
        'featured_products':featured_products,

    }
    return render(request, 'index.html', context)

@baseView
def products_list_view(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
        products = Product.objects.filter(product_status="published").exclude(vendor=vendor)
    except:
        products = Product.objects.filter(product_status="published")
    context = {
        'products':products,
    }
    return render(request, 'products-list.html', context)


def category_list_view(request):
    categories = Category.objects.all()
    context = {
        'categories':categories,
    }
    return render(request, 'category-list.html', context)

@baseView
def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    try:
        vendor = Vendor.objects.get(user=request.user)
        products = Product.objects.filter(product_status="published", category=category).exclude(vendor=vendor)
    except:
        products = Product.objects.filter(product_status="published", category=category)
    brands = Brand.objects.filter(categories=category)
    categories = Category.objects.all()
    context = {
        'products': products,
        'category': category,
        'categories': categories,
        'brands': brands,
    }
    return render(request, 'products-list.html', context)

def vendor_detail_view(request,vid):
    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(vendor=vendor,product_status="published")
    last_products = Product.objects.filter(vendor=vendor,product_status="published").order_by("-date")[:3]
    context = {
        'vendor':vendor,
        'products':products,
        'last_products':last_products,
    }
    return render(request,'vendor_details.html', context)

def vendor_about_view(request,vid):
    vendor = Vendor.objects.get(vid=vid)
    context = {
        'vendor':vendor,
    }
    return render(request,'vendor_about.html', context)

def vendor_products_list_view(request,vid):
    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(vendor=vendor,product_status="published")
    context = {
        'vendor':vendor,
        'products':products,
    }
    return render(request,'vendor_product_list.html', context)

def product_detail_view(request,pid):
    product = Product.objects.get(pid=pid)
    p_images = product.product_images.all()
    related_products = Product.objects.filter(category=product.category, product_status="published").exclude(title=product.title)
    reviews = ProductReview.objects.filter(product=product).order_by('-date')
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
    average_rating = average_rating['rating'] or 0.0
    full_stars = math.floor(average_rating)
    half_star = 1 if (average_rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    context = {
        'product':product,
        'p_images':p_images,
        'related_products':related_products,
        'reviews': reviews,
        'average_rating': average_rating,
        'full_stars': ['★'] * full_stars,
        'half_star': ['✮'] * half_star,
        'empty_stars': ['☆'] * empty_stars,
    }
    return render(request,'product_details.html', context)

def tag_list_view(request,tag_slug=None):
    try:
        vendor = Vendor.objects.get(user=request.user)
        products = Product.objects.filter(product_status="published").exclude(vendor=vendor).order_by("-id")
    except:
        products = Product.objects.filter(product_status="published").order_by("-id")
    tag= None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {
        'products':products,
    }
    return render(request, 'tag.html', context)

@baseView
def search_view(request):
    query = request.GET.get('q', "")
    filters = Q()
    if query:
        filters |= Q(title__icontains=query) | Q(description__icontains=query) | Q(tags__name__icontains=query)
    try:
        vendor = Vendor.objects.get(user=request.user)
        products = Product.objects.filter(filters).exclude(vendor=vendor).distinct().order_by('-date')
    except:
        products = Product.objects.filter(filters).distinct().order_by('-date')
    brands = Brand.objects.all().order_by('title')
    context = {
        # 'min_price':min_price,
        # 'max_price':max_price,
        # 'category':category,
        'query':query,
        # 'brand':brand,
        'products': products,
        'brands':brands,

    }
    return render(request, 'search.html', context)
@baseView
def filter_view(request):
    if request.method == "GET":
        category = request.GET.get('category', "")
        min_price = request.GET.get('min_price', "")
        max_price = request.GET.get('max_price', "")
        brand = request.GET.get('brand', "") #bid
        rating = request.GET.get('rating', "")
        query = request.GET.get('q', "")
        
        # Sorgu oluşturma
        filters = Q()
        if query:
            filters |= Q(title__icontains=query) | Q(description__icontains=query) | Q(tags__name__icontains=query)
        if brand:
            filters &= Q(brand__bid__icontains=brand) #brand tablosundaki bid ile brand eslesiyor mu
        if category:
            filters &= Q(category__cid__icontains=category)
        if min_price:
            filters &= Q(price__gte=min_price)
        if max_price:
            filters &= Q(price__lte=max_price)
        if rating:
            filters &= Q(rating__gte=rating)

        try:
            vendor = Vendor.objects.get(user=request.user)
            products = Product.objects.filter(filters).exclude(vendor=vendor).distinct()
        except:
            products = Product.objects.filter(filters).distinct()
    brands = Brand.objects.filter(category__cid=category).order_by('title') if category else Brand.objects.all().order_by('title')
        



    context = {
        'min_price':min_price,
        'max_price':max_price,
        'category':category,
        'query':query,
        'brand':brand,
        'products': products,
        'brands':brands,

    }
    return render(request, 'products-list.html', context)

@login_required
def add_to_cart(request):
    if request.method == "POST":
        product_pid = request.POST.get('pid')
        print("pid", product_pid)
        # image = request.POST.get('image')
        quantity = int(request.POST.get('qty', 1))  # Default miktar 1
        # title = request.POST.get('title')
        # price = float(request.POST.get('price'))
        # vendor = request.POST.get('vendor')

        # Kullanıcının sepetinde aynı ürün var mı kontrol et
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=Product.objects.get(pid=product_pid),
            defaults={
                'quantity': quantity,
            }
        )

        if not created:
            # Eğer ürün zaten varsa miktarını artır
            cart_item.quantity += quantity
            cart_item.save()

        # Sepetteki toplam ürün sayısını hesapla
        total_cart_items = Cart.objects.filter(user=request.user).count()

        return JsonResponse({
            'message': 'Ürün sepete eklendi',
            'totalcartitems': total_cart_items
        })

    return JsonResponse({'error': 'Geçersiz istek'}, status=400)

def calculate_cart_totals(user):
    """Helper function to calculate total cart amount and item count."""
    cart_items = Cart.objects.filter(user=user)
    cart_total_amount = float(sum(item.quantity * item.product.price for item in cart_items))  # Float dönüşümü eklendi
    cart_data = {
        item.product.pid: {
            'title': item.product.title,
            'price': float(item.product.price),
            'qty': item.quantity,
            'total_price': float(item.quantity * item.product.price)
        } for item in cart_items
    }
    return cart_items.count(), cart_total_amount, cart_data

@login_required
def update_cart_item(request):
    if request.method == 'POST':
        product_id = request.POST.get('pid')
        new_qty = int(request.POST.get('qty', 0))

        # Retrieve the cart item
        cart_item = get_object_or_404(Cart, user=request.user, product__pid=product_id)

        if new_qty > 0:
            # Update the quantity
            cart_item.quantity = new_qty
            cart_item.save()
        else:
            # Remove the item if quantity is 0
            cart_item.delete()

        # Calculate updated cart totals
        totalcartitems, cart_total_amount, cart_data = calculate_cart_totals(request.user)
        if not cart_data:
            return JsonResponse({"success": True, "is_empty": True})
        return JsonResponse({
            'success': True,
            'totalcartitems': totalcartitems,
            'cart_total_amount': cart_total_amount,
            'cart_data': cart_data
        })

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)



@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)

    cart_data = [
        {
            "pid": item.product.pid,
            "title": item.product.title,
            "quantity": item.quantity,
            "price": item.product.price,
            "image": item.product.image if hasattr(item.product.image, 'url') else item.product.image,
            "vendor": item.product.vendor,
            "total_price": item.product.price * item.quantity
        }
        for item in cart_items
    ]

    cart_total_amount = sum(item['total_price'] for item in cart_data)
    if not cart_data:
        return redirect("index")
    addresses = Address.objects.filter(user=request.user)
    
    context = {
        'cart_data': cart_data,
        'totalcartitems': len(cart_data),
        'cart_total_amount': cart_total_amount,
        "addresses":addresses,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    return render(request, 'cart.html', context)

@login_required
def checkout_view(request):
    cart_data = {}
    try:
        active_address = Address.objects.get(user=request.user, status=True)
    except Address.DoesNotExist:
        messages.warning(request, "Aktif bir adresiniz bulunmuyor. Lütfen bir adres ekleyin.")
        return redirect("cart")
    except Address.MultipleObjectsReturned:
        messages.warning(request, "Birden fazla aktif adresiniz var. Lütfen birini seçin.")
        return redirect("addresses")

    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.warning(request, "Sepetiniz boş. Devam etmeden önce ürün ekleyin.")
        return redirect('cart')
    order = CartOrder.objects.create(user=request.user, price=0)

    # Sipariş oluşturma
    cart_total_amount = 0
    vendors = []
    for item in cart_items:
        try:
            vendor = Vendor.objects.get(title=item.product.vendor)
        except Vendor.DoesNotExist:
            messages.error(request, f"{item.product.vendor} adlı satıcı bulunamadı.")
            return redirect('cart')
        if vendor not in vendors:
            vendors.append(vendor)
        item_total_price = item.quantity * item.product.price
        cart_total_amount += item_total_price
        # Sepet verilerini doldur
        cart_data[item.product.pid] = {
            'title': item.product.title,
            'price': item.product.price,
            'qty': item.quantity,
            'total_price': item_total_price,
            'image': item.product.image if hasattr(item.product.image, 'url') else item.product.image,
            'vendor': vendor.title,
        }
        CartOrderItems.objects.create(
            order=order,
            item=item.product.title,
            image=item.product.image,
            quantity=item.quantity,
            price=item.product.price,
            total=item_total_price,
            vendor=vendor
        )

    order.price = cart_total_amount
    order.invoice_no=order.oid
    order.save()


    host = request.get_host()
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": cart_total_amount,
        "item_name": f"Order-{order.oid}",
        "invoice": order.invoice_no,
        "notify_url": f"http://{host}{reverse('paypal-ipn')}",
        "return": f"http://{host}{reverse('payment_waiting')}?invoice={order.oid}",
        "cancel_return": f"http://{host}{reverse('payment_failed')}?invoice={order.oid}",
        "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    # # PayPal ödeme ayarları
    # host = request.get_host()
    # paypal_dict = {
    #     'business': settings.PAYPAL_RECEIVER_EMAIL,
    #     'amount': cart_total_amount,
    #     'item_name': f"Order-{order.oid}",
    #     'invoice': order.oid,
    #     'currency_code': "USD",
    #     'notify_url': f"http://{host}{reverse('paypal-ipn')}",
    #     'return_url': f"http://{host}{reverse('payment_waiting')}?invoice={order.oid}",
    #     'cancel_url': f"http://{host}{reverse('payment_failed')}?invoice={order.oid}",
    # }
    # paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)

    return render(request, 'checkout.html', {
        "cart_data":cart_data,
        "cart_total_amount": cart_total_amount,
        "form":form,
        "order": order,
        "active_address":active_address,
        "MEDIA_URL": settings.MEDIA_URL,
        "vendors":vendors,
    })


def paypal_payment_received(sender, **kwargs):
    ipn = sender
    if ipn.payment_status != ST_PP_COMPLETED:
            return
    
    if ipn.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
        return
    order = CartOrder.objects.filter(oid=ipn.invoice).first()
    cart = Cart.objects.get(user=order.user)
    if ipn.mc_gross == order.price and ipn.mc_currency == "USD":
        order.paid_status = True
        order.save()
        cart.delete()
valid_ipn_received.connect(paypal_payment_received)
        
@login_required
def payment_completed_view(request):
    invoice = request.GET.get('invoice')
    try:
        order = get_object_or_404(CartOrder, oid=invoice, user=request.user)
    except CartOrder.DoesNotExist:
        messages.error(request, "Sipariş bulunamadı.")
        return redirect("cart")
    if not order.paid_status:
        return redirect(f"{reverse('payment_waiting')}?invoice={order.oid}")
    return render(request, "payment-completed.html", {"order": order})


        
@login_required
def payment_waiting_view(request):
    invoice = request.GET.get('invoice')
    if not invoice:
        messages.error(request, "Geçersiz fatura numarası.")
        return redirect("cart")

    return render(request, 'payment-waiting.html', {"invoice": invoice})


@login_required
def payment_failed_view(request):
    invoice = request.GET.get('invoice')
    if invoice:
        try:
            order = CartOrder.objects.get(oid=invoice)
            order.delete()  # Başarısız siparişi sil
        except CartOrder.DoesNotExist:
            pass

    messages.error(request, "Ödeme başarısız oldu. Sipariş iptal edildi.")
    return render(request, 'payment-failed.html')


@login_required
def customer_dashboard(request):
    orders = CartOrder.objects.filter(user=request.user)
    address = Address.objects.filter(user=request.user)
    profile = Profile.objects.get(user=request.user)
    context={
        'orders': orders,
        'addresses': address,
        'profile':profile
    }
    return render(request, 'dashboard.html', context)

@login_required
def order_detail(request,id):
    order = CartOrder.objects.get(user=request.user, oid=id)
    print(order.product_status)
    products = CartOrderItems.objects.filter(order=order)
    for p in products:
        invoice_no = p.invoice_no
    print("invoice", invoice_no)
    context={
        'order': order,
        'products': products,
        'invoice_no':invoice_no
    }
    return render(request, 'order-detail.html', context)

def make_review(request):
    if request.method == "POST":
        user = request.user
        title = request.POST.get("title")
        vendor = request.POST.get("vendor")
        review = request.POST.get("review")
        rating = request.POST.get("rating")
        
        try:
            product = Product.objects.get(title=title, vendor__title=vendor)
            print("product", product)
        except:
            print("olmadi")
            messages.error(request, "Ürün bulunamadı.")
            return redirect("order_detail", id=request.POST.get("order_id"))  # Replace with correct URL
        
        # Create the review
        ProductReview.objects.create(user=user, product=product, review=review, rating=rating)
        
        # Success message
        messages.success(request, "Değerlendirme başarıyla gönderilmiştir.")
        
        # Redirect to the order detail page (adjust the URL name if necessary)
        return redirect("order_detail", id=request.POST.get("order_id"))  # Replace with correct URL
    else:
        # If the request is not POST, redirect or handle differently
        return redirect("home")  # Replace with appropriate fallback


def customer_orders(request):
    orders = CartOrder.objects.filter(user=request.user)
    context={
        'orders': orders,
    }
    return render(request, 'orders.html', context)

@login_required
def customer_wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    for product in wishlist:
        print(product)
    for product in wishlist:
        average_rating = ProductReview.objects.filter(product__title=product).aggregate(rating=Avg('rating'))
        average_rating = average_rating['rating'] or 0.0
        full_stars = math.floor(average_rating)
        half_star = 1 if (average_rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        product.full_stars = ['★'] * full_stars
        product.half_star = ['☆'] * half_star
        product.empty_stars = ['☆'] * empty_stars
        product.average_rating = average_rating
    
    context ={
        'wishlist':wishlist
    }
    return render(request, "wishlist.html", context)

@login_required
def add_to_wishlist(request):
    context = {}
    id = request.POST.get("id")  # get() kullanımı eksik parametreyi kontrol eder
    if not id:
        return JsonResponse({"bool": False, "error": "ID is missing"}, status=400)
    
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return JsonResponse({"bool": False, "error": "Product not found"}, status=404)
    
    wishlist_count = Wishlist.objects.filter(product=product, user=request.user).count()
    if wishlist_count > 0:
        context = {"bool": True}
    else:
        Wishlist.objects.create(user=request.user, product=product)
        context = {"bool": True}
    
    return JsonResponse(context)


@login_required
def remove_to_wishlist(request):
    pid = request.POST['id']
    Wishlist.objects.filter(id=pid, user=request.user).delete()  # Güvenlik için user kontrolü

    # Güncellenmiş wishlist'i al
    wishlist = Wishlist.objects.filter(user=request.user)

    # Wishlist'in sadece ilgili kısmını HTML olarak serialize et
    context = {"wishlist": wishlist}
    wishlist_html = render_to_string("partials/wishlist_list.html", context, request=request)

    return JsonResponse({
        "bool": True,
        "wishlist_html": wishlist_html
    })

@login_required
def customer_settings(request):
    profile = Profile.objects.get(user=request.user)
    user = User.objects.get(username=request.user.username)
    if request.method == "POST":
        try:
            email = request.POST.get("email", user.email)
            username = request.POST.get("username", user.username)
            user.username = username
            user.email = email
            user.save()
            messages.success(request, "Profil başarıyla güncellendi!")
        except Exception as e:
            messages.error(request, f"Bir hata oluştu: {e}")
        return redirect("dashboard")

    context = {
        "profile":profile,
    }
    return render(request, 'settings.html', context)

@login_required
def change_password(request):
    user = request.user
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_new_password = request.POST.get("confirm_new_password")
        errors = []

        # Check if new password and confirm password match
        if new_password != confirm_new_password:
            messages.error(request, "Yeni şifreler eşleşmiyor.")
            return redirect("change_password")

        # Check if old password is correct
        if not check_password(old_password, user.password):
            messages.error(request, "Eski şifre hatalı.")
            return redirect("change_password")

        # Validate the new password against Django's password validation rules
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            errors.extend(e.messages)

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect("change_password")

        # Change the password
        user.set_password(new_password)
        user.save()
        messages.success(request, "Şifre başarıyla değiştirildi. Tekrar giriş yapın.")
        return redirect("userauths:login")

    return render(request, "change_password.html")

@login_required
def customer_address(request):
    if request.method == "POST":
        title = request.POST['title']
        address = request.POST['address']
        country = request.POST['country']
        phone = request.POST['phone']
        addresses = Address.objects.filter(user=request.user)
        if addresses:
            new_address = Address.objects.create(
                user=request.user,
                address=address,
                country=country,
                title=title,
                phone=phone
            )
        else:
            new_address = Address.objects.create(
                user=request.user,
                address=address,
                country=country,
                title=title,
                phone=phone,
                status = True
            )
        print("Basarili")
        return redirect('addresses')

    addresses = Address.objects.filter(user=request.user)
    context={
        'addresses': addresses,
        }
    return render(request, 'myAddresses.html', context)

def delete_address(request):
    id = request.POST.get("id")
    address = Address.objects.get(id=id, user=request.user)
    address.delete()
    return JsonResponse({"boolean": True})

def edit_address(request):
    if request.method == "POST":
        id = request.POST.get("id")
        address = Address.objects.get(id=id, user=request.user)
        title = request.POST.get("title", address.title)
        _address = request.POST.get("address", address.address)
        country = request.POST.get("country", address.country)
        phone = request.POST.get("phone", address.phone)
        address.title = title
        address.address = _address 
        address.country = country
        address.phone = phone
        address.save()
        return redirect("addresses")
    return render(request, "myAddresses.html")

def make_address_default(request):
    id = request.POST['id']
    Address.objects.filter(user=request.user).update(status=False)
    Address.objects.filter(id=id, user=request.user).update(status=True)
    return JsonResponse({"boolean": True})

    
def contactUs_view(request):
    return render(request,"contactus.html")

def ajax_contact(request):
    full_name = request.POST['full_name']
    email = request.POST['email']
    phone = request.POST['phone']
    subject = request.POST['subject']
    message = request.POST['message']

    contact = ContactUs.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
        subject=subject,
        message=message,
    )
    data = {
        "bool":True,
        "message": "Message Sent Successfully"
    }
    return JsonResponse({"data":data})

@login_required
def apply_for_vendor(request):
    # Kullanıcı zaten satıcıysa ve başvuru durumu beklemede değilse, başvuru yapmasın
    if hasattr(request.user, 'vendor'):
        vendor = request.user.vendor
        if not vendor.is_application_pending:
            return redirect('useradmin:dashboard')  # Kullanıcı zaten satıcıysa yönlendirme yapılacak sayfa

    if request.method == 'POST':
        # POST isteği ile gelen verileri alıyoruz
        title = request.POST.get('title')
        image = request.FILES.get('image')
        description = request.POST.get('description')
        address = request.POST.get('address')
        country = request.POST.get('country')
        contact = request.POST.get('contact')
        chat_resp_time = request.POST.get('chat_resp_time', 0)
        shipping_on_time = request.POST.get('shipping_on_time', 0)
        authentic_rating = request.POST.get('authentic_rating', 0)
        days_return = request.POST.get('days_return', 0)
        warranty_period = request.POST.get('warranty_period', 0)

        request.user.is_vendor = True
        request.user.save()

        # Yeni Vendor başvurusu oluşturuluyor
        vendor = Vendor(
            user=request.user,
            title=title,
            image=image,
            description=description,
            address=address,
            country=country,
            contact=contact,
            chat_resp_time=chat_resp_time,
            shipping_on_time=shipping_on_time,
            authentic_rating=authentic_rating,
            days_return=days_return,
            warranty_period=warranty_period,
        )
        
        profile = Profile.objects.get(user=request.user)
        profile.image=image
        profile.full_name = request.user.first_name + " " + request.user.last_name,
        profile.bio=description
        profile.phone=contact
        profile.country=country

        user = User.objects.get(id=request.user.id)
        user.phone=contact
        user.is_vendor=True
        with transaction.atomic():
            vendor.save()
            profile.save()
            user.save()
        return redirect('vendor_success')  # Başarı sayfasına yönlendirme
    profile = Profile.objects.get(user=request.user)
    return render(request, 'apply_for_vendor.html', {"profile":profile})

def vendor_success(request):
    return render(request, "vendor_success.html")