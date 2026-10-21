import time
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from core.filters import ProductFilter
from useradmin.forms import VendorForm
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
from core.decorators import ajax_login_required

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
from paypal.standard.models import (
    ST_PP_COMPLETED, ST_PP_DENIED, ST_PP_FAILED, ST_PP_EXPIRED,
    ST_PP_VOIDED, ST_PP_REVERSED, ST_PP_REFUNDED,
)

# Create your views here.

def index(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
        products = Product.objects.filter(product_status="published").exclude(vendor=vendor).annotate(avg_rating=Avg("productreview__rating"))
        featured_products = Product.objects.filter(product_status="published", featured = True).exclude(vendor=vendor).annotate(avg_rating=Avg("productreview__rating"))
        last_products = Product.objects.filter(product_status="published").exclude(vendor=vendor).annotate(avg_rating=Avg("productreview__rating")).order_by("-date")[:3]
    except:
        products = Product.objects.filter(product_status="published").annotate(avg_rating=Avg("productreview__rating"))
        featured_products = Product.objects.filter(product_status="published", featured = True).annotate(avg_rating=Avg("productreview__rating"))
        last_products = Product.objects.filter(product_status="published").annotate(avg_rating=Avg("productreview__rating")).order_by("-date")[:3]
    context = {
        'products':products,
        'last_products':last_products,
        'featured_products':featured_products,

    }
    return render(request, 'index.html', context)


def products_list_view(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
        products = Product.objects.filter(product_status="published").select_related("category", "vendor").exclude(vendor=vendor).annotate(avg_rating=Avg("productreview__rating"))
        product_filter = ProductFilter(request.GET, queryset=products)
    except:
        products = Product.objects.filter(product_status="published").select_related("category", "vendor").annotate(avg_rating=Avg("productreview__rating"))
        product_filter = ProductFilter(request.GET, queryset=products)
    context = {
        'filter':product_filter,
        'products':product_filter.qs,
    }
    return render(request, 'products-list.html', context)


def category_list_view(request):
    categories = Category.objects.all()
    context = {
        'categories':categories,
    }
    return render(request, 'category-list.html', context)


def category_product_list_view(request, cid):
    category = get_object_or_404(Category, cid=cid)
    return redirect(f"{reverse('products_list')}?category={category.cid}")

def vendor_detail_view(request,vid):
    vendor = get_object_or_404(Vendor, vid=vid)
    products = Product.objects.filter(vendor=vendor,product_status="published").annotate(avg_rating=Avg("productreview__rating"))
    last_products = Product.objects.filter(vendor=vendor,product_status="published").annotate(avg_rating=Avg("productreview__rating")).order_by("-date")[:3]
    context = {
        'vendor':vendor,
        'products':products,
        'last_products':last_products,
    }
    return render(request,'vendor_details.html', context)

def vendor_about_view(request,vid):
    vendor = get_object_or_404(Vendor, vid=vid)
    context = {
        'vendor':vendor,
    }
    return render(request,'vendor_about.html', context)

def vendor_products_list_view(request,vid):
    vendor = get_object_or_404(Vendor, vid=vid)
    products = Product.objects.filter(vendor=vendor,product_status="published").annotate(avg_rating=Avg("productreview__rating"))
    context = {
        'vendor':vendor,
        'products':products,
    }
    return render(request,'vendor_product_list.html', context)

def product_detail_view(request,pid):
    try:
        address = Address.objects.filter(user=request.user, status=True).first()
    except:
        address=None
    product = get_object_or_404(Product, pid=pid)
    p_images = product.product_images.all()
    related_products = Product.objects.filter(category=product.category, product_status="published").exclude(title=product.title)
    reviews = ProductReview.objects.filter(product=product).order_by('-date')
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
    average_rating = average_rating['rating'] or 0.0
    full_stars = math.floor(average_rating)
    half_star = 1 if (average_rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    context = {
        'address':address,
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
    tag = get_object_or_404(Tag, slug=tag_slug)
    return redirect(f"{reverse('products_list')}?tags={tag.slug}")

@ajax_login_required
def add_to_cart(request):
    if request.method == "POST":
        product_pid = request.POST.get('pid')
        print("pid", product_pid)
        # image = request.POST.get('image')
        try:
            quantity = int(request.POST.get("qty", 1))
        except ValueError:
            return JsonResponse({"error": "Geçersiz adet"}, status=400)

        if quantity < 1:
            return JsonResponse({"error": "Adet en az 1 olmalı"}, status=400)
        # title = request.POST.get('title')
        # price = float(request.POST.get('price'))
        # vendor = request.POST.get('vendor')

        product = get_object_or_404(Product, pid=product_pid, product_status="published")

        # Kullanıcının sepetinde aynı ürün var mı kontrol et
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
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

@ajax_login_required
def update_cart_item(request):
    if request.method == 'POST':
        product_id = request.POST.get('pid')
        try:
            new_qty = int(request.POST.get('qty', 0))
        except ValueError:
            return JsonResponse({"error": "Geçersiz adet"}, status=400)
                

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
def create_order_view(request):
    if request.method != "POST":
        return redirect("checkout")
    address = Address.objects.filter(user=request.user,status=True).first()
    if not address:
        messages.warning(request, "Lütfen önce bir teslimat adresi seçin.")
        return redirect("checkout")
    cart_items = Cart.objects.filter(user=request.user).select_related("product__vendor")
    if not cart_items:
        return redirect("cart")
    with transaction.atomic():
        # Sipariş oluşturma
        cart_total_amount = 0
        order = CartOrder.objects.create(user=request.user, price=0)
        for item in cart_items:
            item_total_price = item.quantity * item.product.price
            cart_total_amount += item_total_price
            CartOrderItems.objects.create(
                order=order,
                item=item.product.title,
                image=item.product.image,
                quantity=item.quantity,
                price=item.product.price,
                total=item_total_price,
                vendor=item.product.vendor
            )

        order.price = cart_total_amount
        order.invoice_no=order.oid
        order.shipping_title = address.title
        order.shipping_phone = address.phone
        order.shipping_country = address.country
        order.shipping_address = address.address
        order.save()


        host = request.get_host()
        paypal_dict = {
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "amount": cart_total_amount,
            "item_name": f"Order-{order.oid}",
            "invoice": f"{order.invoice_no}",
            "notify_url": f"http://{host}{reverse('paypal-ipn')}",
            "return": f"http://{host}{reverse('payment_waiting')}?invoice={order.oid}",
            "cancel_return": f"http://{host}{reverse('payment_failed')}?invoice={order.oid}",
            "error_return": f"http://{host}{reverse('payment_failed')}?invoice={order.oid}",
            "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
        }
        form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, "paypal_redirect.html", {"form": form})


@login_required
def checkout_view(request):
    cart_total_amount = 0
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
    cart_data = {}
    totalcartitems = {}
    for item in cart_items:
        try:
            vendor = Vendor.objects.get(title=item.product.vendor)
        except Vendor.DoesNotExist:
            messages.error(request, f"{item.product.vendor} adlı satıcı bulunamadı.")
            return redirect('cart')
        
        item_total_price = item.quantity * item.product.price
        cart_total_amount += item_total_price
        cart_data[item.product.pid] = {
            'title': item.product.title,
            'price': item.product.price,
            'qty': item.quantity,
            'total_price': item_total_price,
            'image': item.product.image if hasattr(item.product.image, 'url') else item.product.image,
            'vendor':vendor
        }
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
        "cart_items":cart_items,
        "cart_total_amount": cart_total_amount,
        # "form":form,
        # "order": order,
        "active_address":active_address,
        "MEDIA_URL": settings.MEDIA_URL,
        # "vendors":vendors,
    })


def paypal_payment_received(sender, **kwargs):
    ipn = sender
    order = CartOrder.objects.filter(oid=ipn.invoice).first()
    FAILED_STATES = (ST_PP_DENIED, ST_PP_FAILED, ST_PP_EXPIRED, ST_PP_VOIDED, ST_PP_REVERSED, ST_PP_REFUNDED)

    if not order:
        return
    if ipn.payment_status in FAILED_STATES:
        order.payment_status = "failed"
        order.paid_status = False
        order.save()
        return

    if ipn.payment_status != ST_PP_COMPLETED:
        return


    if ipn.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
        order.payment_status = "failed"
        order.paid_status = False
        order.save()
        return

    if ipn.mc_gross != order.price:
        order.payment_status = "failed"
        order.paid_status = False
        order.save()
        return

    if ipn.mc_currency != "USD":
        order.payment_status = "failed"
        order.paid_status = False
        order.save()
        return

    if ipn.mc_gross == order.price and ipn.mc_currency == "USD":
        cart = Cart.objects.filter(user=order.user)
        order.payment_status = "paid"
        order.paid_status = True
        order.save()
        cart.delete()
        return


valid_ipn_received.connect(paypal_payment_received)
        
@login_required
def payment_completed_view(request):
    invoice = request.GET.get('invoice')
    order = get_object_or_404(CartOrder, oid=invoice, user=request.user)
    if order.payment_status == "failed":
        return redirect(f"{reverse('payment_failed')}?invoice={order.oid}")
    if order.payment_status != "paid":
        return redirect(f"{reverse('payment_waiting')}?invoice={order.oid}")
    return render(request, "payment-completed.html", {"order": order})


@login_required
def order_payment_state(request, oid):
    order = get_object_or_404(CartOrder, oid=oid, user=request.user)
    return JsonResponse({"state":order.payment_status})
        
@login_required
def payment_waiting_view(request):
    invoice = request.GET.get('invoice')
    if not invoice:
        messages.error(request, "Geçersiz fatura numarası.")
        return redirect("cart")
    get_object_or_404(CartOrder, oid=invoice, user=request.user)
    return render(request, 'payment-waiting.html', {"invoice": invoice})


@login_required
def payment_failed_view(request):
    invoice = request.GET.get('invoice')
    if invoice:
        try:
            order = CartOrder.objects.get(oid=invoice, user=request.user)
            if order.paid_status == False:
                order.delete()  # Başarısız siparişi sil
        except CartOrder.DoesNotExist:
            pass

    messages.error(request, "Ödeme başarısız oldu. Sipariş iptal edildi.")
    return render(request, 'payment-failed.html')


@login_required
def customer_dashboard(request):
    orders = CartOrder.objects.filter(user=request.user, paid_status=True)
    address = Address.objects.filter(user=request.user)
    profile = get_object_or_404(Profile, user=request.user)
    context={
        'orders': orders,
        'addresses': address,
        'profile':profile
    }
    return render(request, 'dashboard.html', context)

@login_required
def order_detail(request, oid):
    order = get_object_or_404(CartOrder, user=request.user, oid=oid)
    products = CartOrderItems.objects.filter(order=order)
    for product in products:
        product.user_review = ProductReview.objects.filter(user=request.user, product__title=product.item, product__vendor=product.vendor).first()
        print(product)
    invoice_no = order.invoice_no
    context={
        'order': order,
        'products': products,
        'invoice_no':invoice_no,
    }
    return render(request, 'order-detail.html', context)

@ajax_login_required
def make_review(request):
    if request.method == "POST":
        user = request.user
        title = request.POST.get("title")
        vendor = request.POST.get("vendor")
        review = request.POST.get("review")
        rating = request.POST.get("rating")
        oid = request.POST.get("order_id")
        
        try:
            product = Product.objects.get(title=title, vendor__title=vendor)
            print("product", product)
        except:
            print("olmadi")
            messages.error(request, "Ürün bulunamadı.")
            return redirect("order_detail", oid=oid)  # Replace with correct URL
        
        # Create the review
        purchased = CartOrderItems.objects.filter(order__user=request.user, product_status="delivered", order__paid_status=True, item=product.title, vendor=product.vendor).exists()
        if not purchased:
            messages.error(request, "Sadece satın alıp teslim aldığınız ürünleri değerlendirebilirsiniz.")
        elif ProductReview.objects.filter(user=user, product=product).exists():
            messages.error(request, "Ürüne zaten yorum yapılmış.")
        else:
            ProductReview.objects.create(user=user, product=product, review=review, rating=rating)
            # Success message
            messages.success(request, "Değerlendirme başarıyla gönderilmiştir.")
        
        # Redirect to the order detail page (adjust the URL name if necessary)
        return redirect("order_detail", oid=oid)  # Replace with correct URL
    else:
        # If the request is not POST, redirect or handle differently
        return redirect("index")  # Replace with appropriate fallback

@login_required
def customer_orders(request):
    orders = CartOrder.objects.filter(user=request.user, paid_status=True)
    context={
        'orders': orders,
    }
    return render(request, 'orders.html', context)

@login_required
def customer_wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    context ={
        'wishlist':wishlist
    }
    return render(request, "wishlist.html", context)

@ajax_login_required
def add_to_wishlist(request):
    context = {}
    id = request.POST.get("id")  # get() kullanımı eksik parametreyi kontrol eder
    if not id:
        return JsonResponse({"bool": False, "error": "ID is missing"}, status=400)
    
    try:
        product = Product.objects.get(id=id)
        average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
        average_rating = average_rating['rating'] or 0.0
    except Product.DoesNotExist:
        return JsonResponse({"bool": False, "error": "Product not found"}, status=404)
    
    wishlist_count = Wishlist.objects.filter(product=product, user=request.user).count()
    if wishlist_count > 0:
        context = {"bool": True}
    else:
        Wishlist.objects.create(user=request.user, product=product, rating=average_rating)
        context = {"bool": True}
    
    return JsonResponse(context)


@ajax_login_required
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
        return redirect("userauths:signin")

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

@login_required
def delete_address(request):
    if request.method == "POST":
        id = request.POST.get("id")
        address = get_object_or_404(Address, id=id, user=request.user)
        address.delete()
        return JsonResponse({"boolean": True})
    return JsonResponse({"error": "Geçersiz istek"}, status=400)

@login_required
def edit_address(request):
    if request.method == "POST":
        id = request.POST.get("id")
        address = get_object_or_404(Address, id=id, user=request.user)
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

@login_required
def make_address_default(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        get_object_or_404(Address, id=id, user=request.user)
        Address.objects.filter(user=request.user).update(status=False)
        Address.objects.filter(id=id, user=request.user).update(status=True)
        return JsonResponse({"boolean": True})
    return JsonResponse({"error": "Geçersiz istek"}, status=400)

    
def contactUs_view(request):
    return render(request,"contactus.html")

def ajax_contact(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if not full_name or not email or not message:
            return JsonResponse({"error": "Lütfen zorunlu alanları doldurun"}, status=400)

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
    return JsonResponse({"error": "Geçersiz istek"}, status=400)

@login_required
def apply_for_vendor(request):
    # Kullanıcı zaten satıcıysa ve başvuru durumu beklemede değilse, başvuru yapmasın
    if hasattr(request.user, 'vendor'):
        return redirect('useradmin:dashboard')  # Kullanıcı zaten satıcıysa yönlendirme yapılacak sayfa

    if request.method == 'POST':
        form = VendorForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():

                new_form = form.save(commit=False)
                new_form.user = request.user
                new_form.save()
                form.save_m2m()
                profile = get_object_or_404(Profile, user=request.user)
                if new_form.image:
                    profile.image=new_form.image
                profile.full_name = request.user.first_name + " " + request.user.last_name
                profile.bio=new_form.description
                profile.phone=new_form.contact
                profile.country=new_form.country
                request.user.is_vendor=True
                profile.save()
                request.user.save()
        # # POST isteği ile gelen verileri alıyoruz
        # try:
        #     title = request.POST.get('title')
        #     image = request.FILES.get('image')
        #     description = request.POST.get('description')
        #     address = request.POST.get('address')
        #     country = request.POST.get('country')
        #     contact = request.POST.get('contact')
        #     chat_resp_time = request.POST.get('chat_resp_time', 0)
        #     shipping_on_time = request.POST.get('shipping_on_time', 0)
        #     authentic_rating = request.POST.get('authentic_rating', 0)
        #     days_return = request.POST.get('days_return', 0)
        #     warranty_period = request.POST.get('warranty_period', 0)
        # except:
        #     messages.error("Lütfen bütün alanları doldurduğunuzdan emin olun.")
        # # Yeni Vendor başvurusu oluşturuluyor
        # vendor = Vendor(
        #     user=request.user,
        #     title=title,
        #     image=image,
        #     description=description,
        #     address=address,
        #     country=country,
        #     contact=contact,
        #     chat_resp_time=chat_resp_time,
        #     shipping_on_time=shipping_on_time,
        #     authentic_rating=authentic_rating,
        #     days_return=days_return,
        #     warranty_period=warranty_period
        # )
        
        # profile = Profile.objects.get(user=request.user)
        # profile.image=image
        # profile.full_name = request.user.first_name + " " + request.user.last_name
        # profile.bio=description
        # profile.phone=contact
        # profile.country=country

        # user = User.objects.get(id=request.user.id)
        # user.phone=contact
        # user.is_vendor=True

            return redirect('vendor_success')  # Başarı sayfasına yönlendirme
    else:
        profile = get_object_or_404(Profile, user=request.user)
        form = VendorForm(initial={
            "title": profile.full_name,
            "description": profile.bio,
            "contact": profile.phone,
            "country": profile.country,
        })

    return render(request, 'apply_for_vendor.html', {"form":form})

@login_required
def vendor_success(request):
    return render(request, "vendor_success.html")