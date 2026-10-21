from django.shortcuts import render,redirect,get_object_or_404
from core.models import STATUS_CHOICE, CartOrder, Product, Category, CartOrderItems,Address,ProductReview, Brand,Vendor
from django.db.models import Sum,Avg
from userauths.models import User,Profile
import datetime
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from .forms import AddProductForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from useradmin.decorators import admin_required

# Create your views here.

from django.db.models import Sum
from django.utils.timezone import now

from django.db.models import Sum
from django.utils.timezone import now

@admin_required
def dashboard(request):
    # Mağaza bilgilerini al
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        messages.error(request, "Mağaza bilgisi bulunamadı.")
        return redirect("index")

    # Satıcıya ait toplam kazanç
    revenue = (
        CartOrderItems.objects.filter(vendor=vendor, order__paid_status=True)
        .aggregate(total=Sum("total"))["total"]
        or 0
    )
    print("revenue", revenue)
    # Satıcıya ait toplam sipariş sayısı
    total_orders_count = CartOrder.objects.filter(cartorderitems__vendor=vendor, paid_status=True).distinct().count()
    print("total_orders_count", total_orders_count)

    # Satıcıya ait ürünler
    products = Product.objects.filter(vendor=vendor)
    print("products", products)

    # Aylık kazanç
    today = now()
    monthly_revenue = (
        CartOrderItems.objects.filter(vendor=vendor, order__paid_status=True, order__order_date__month=today.month, order__order_date__year=today.year)
        .aggregate(monthly_total=Sum("total"))["monthly_total"]
        or 0
    )
    print("monthly_revenue", monthly_revenue)

    # Satıcıya ait son siparişler
    latest_orders = (
        CartOrder.objects.filter(cartorderitems__vendor=vendor, paid_status=True)
        .distinct()
        .order_by("-order_date")[:10]
    )

    context = {
        "vendor": vendor,
        "revenue": revenue,
        "total_orders_count": total_orders_count,
        "products": products,
        "monthly_revenue": monthly_revenue,
        "latest_orders": latest_orders,
    }

    return render(request, "useradmin/dashboard.html", context)



@admin_required
def products(request):
    # Satıcıya ait ürünleri filtreliyoruz
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        vendor = None  # Eğer kullanıcıya ait vendor yoksa

    # Eğer satıcı varsa, ona ait ürünleri filtreliyoruz
    if vendor:
        products = Product.objects.filter(vendor=vendor)
    else:
        products = Product.objects.none()  # Satıcı yoksa hiç ürün göstermiyoruz

    categories = Category.objects.all()
    
    # Sayfalama
    page_number = request.GET.get('page', 1)
    paginator = Paginator(products, 10)  # 10 ürün başına sayfalama
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)
    
    # Ürünlerin ortalama puanlarını hesaplıyoruz
    for product in products:
        average_rating = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        product.average_rating = average_rating if average_rating else 0

    # Eğer AJAX isteği ise, JSON formatında veri döndürüyoruz
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        products_data = [{
            'id': product.id,
            'pid': product.pid,
            'title': product.title,
            "description": product.description,
            "image_url": product.image.url if product.image else "",
            "date": product.date.strftime("%d/%m/%Y"),
            "price": product.price,
            'average_rating': product.average_rating
        } for product in products]

        return JsonResponse({"products": products_data, "has_next": page_obj.has_next()})

    # Sayfa verisini ve kategorileri context'e ekliyoruz
    context = {
        'products': page_obj,
        'categories': categories,
    }
    
    return render(request, "useradmin/product-list.html", context)

@admin_required
def add_product(request):
    if request.method == 'POST':
        form = AddProductForm(request.POST,request.FILES)
        if form.is_valid():
            new_form = form.save(commit=False)
            vendor = Vendor.objects.get(user=request.user)
            new_form.user = request.user
            new_form.vendor = vendor
            new_form.save()
            form.save_m2m()
            messages.success(request, "Urun Basvuruya Alindi")
            return redirect("useradmin:products")
    else:
        form = AddProductForm()
    context = {
        'form':form
    }
    return render(request, "useradmin/add-product.html", context)

# API endpoint to get brands based on category
def get_brands_by_category(request, category_id):
    # category_id ile marka filtrelemesi yapıyoruz
    brands = Brand.objects.filter(categories__id=category_id)
    
    # Markaları JSON formatında döndürüyoruz
    brand_data = [{'id': brand.id, 'title': brand.title} for brand in brands]
    
    return JsonResponse({'brands': brand_data})

@admin_required
def edit_product(request,pid):
    product = get_object_or_404(Product, pid=pid, vendor__user=request.user)
    if request.method == 'POST':
        form = AddProductForm(request.POST,request.FILES,instance=product)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            form.save_m2m()
            return redirect("useradmin:edit_product", product.pid)
    else:
        form = AddProductForm(instance=product)
    context = {
        'product':product,
        'form':form
    }
    return render(request, "useradmin/edit-product.html", context)

@admin_required
def delete_product(request,pid):
    if request.method == "POST":
        product = get_object_or_404(Product, pid=pid, vendor__user=request.user)
        product.delete()
    return redirect("useradmin:products")
 
@admin_required
def orders(request):
    # Satıcıya ait siparişleri filtreliyoruz
    vendor = get_object_or_404(Vendor, user=request.user)

    # Eğer satıcı varsa, ona ait siparişleri filtreliyoruz
    if vendor:
        orders = CartOrderItems.objects.filter(vendor=vendor).select_related("order").distinct()
        # orders = CartOrder.objects.filter(cartorderitems__vendor=vendor).distinct()
    else:
        orders = CartOrder.objects.none()  # Satıcı yoksa hiç sipariş göstermiyoruz

    context = {
        'orders': orders,
    }
    
    return render(request, "useradmin/orders.html", context)
@admin_required
def order_detail(request,id):
    vendor = get_object_or_404(Vendor, user=request.user)
    order = get_object_or_404(CartOrder, id=id)
    order_items = CartOrderItems.objects.filter(order=order, vendor=vendor)
    if not order_items.exists():
        raise Http404
    context={
        "order_items":order_items,
        "order":order,
        "order_first_item": order_items.first(),
    }
    return render(request, "useradmin/order_detail.html", context)

@admin_required
def change_order_status(request,oid):
    order = get_object_or_404(CartOrder, oid=oid)
    vendor = get_object_or_404(Vendor, user=request.user)
    order_items = CartOrderItems.objects.filter(order=order, vendor=vendor)
    if request.method == "POST":
        status = request.POST.get("status")
        if status in STATUS_CHOICE:
            order_items.update(product_status=status)
            messages.success(request, f"Order Status Changed To {status}")
    return redirect("useradmin:order_detail", order.id)

@admin_required
def shop_page(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        vendor = None  # Eğer kullanıcıya ait vendor yoksa

    # Satıcı varsa, ürünleri filtreliyoruz
    if vendor:
        products = Product.objects.filter(vendor=vendor)  # Satıcıya ait ürünleri alıyoruz
        revenue = CartOrderItems.objects.filter(vendor=vendor, order__paid_status=True).aggregate(price=Sum("total"))  # Satıcıya ait satış miktarı
        total_sales = CartOrderItems.objects.filter(vendor=vendor, order__paid_status=True).aggregate(quantity=Sum("quantity"))  # Satıcıya ait satış miktarı
    else:
        products = Product.objects.none()  # Satıcı yoksa hiç ürün gösterme
        revenue = {'price': 0}  # Gelir yoksa sıfır göster
        total_sales = {'quantity': 0}  # Satış yoksa sıfır göster

    context = {
        "products": products,
        "revenue": revenue,
        "total_sales": total_sales,
    }
    return render(request, "useradmin/shop-page.html", context)


@admin_required
def reviews(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        vendor = None  # Eğer kullanıcıya ait vendor yoksa

    if vendor:
        # Satıcıya ait ürünlerin yorumlarını alıyoruz
        reviews = ProductReview.objects.filter(product__vendor=vendor)
    else:
        reviews = ProductReview.objects.none()  # Eğer vendor yoksa hiçbir yorum göstermiyoruz

    # Paginasyon işlemi
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)

    context = {
        "reviews": page_obj,  # Paginasyonu uyguladık
    }

    return render(request, "useradmin/reviews.html", context)

    
@admin_required
def settings(request):
    vendor = Vendor.objects.get(user=request.user)
    if request.method == "POST":
        image = request.FILES.get("image")
        full_name = request.POST.get("full_name")
        bio = request.POST.get("bio")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        country = request.POST.get("country")

        if image != None:
            vendor.image = image

        vendor.title = full_name
        vendor.description = bio
        vendor.contact = phone
        vendor.address = address
        vendor.country = country
        vendor.save()
        messages.success(request, "Success")

        return redirect("useradmin:settings")
    
    context = {
        "profile":vendor
    }
    return render(request, "useradmin/settings.html", context)


@admin_required
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
            return redirect("useradmin:change_password")

        # Check if old password is correct
        if not check_password(old_password, user.password):
            messages.error(request, "Eski şifre hatalı.")
            return redirect("useradmin:change_password")

        # Validate the new password against Django's password validation rules
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            errors.extend(e.messages)

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect("useradmin:change_password")

        # Change the password
        user.set_password(new_password)
        user.save()
        messages.success(request, "Şifre başarıyla değiştirildi. Tekrar giriş yapın.")
        return redirect("userauths:signin")

    return render(request, "useradmin/change_password.html")