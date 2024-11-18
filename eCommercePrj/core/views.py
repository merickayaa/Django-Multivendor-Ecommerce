from django.shortcuts import render, get_object_or_404
from userauths.models import User
from core.models import Product,Category,Vendor,CartOrderItems,CartOrder, Wishlist, Address, ProductImages, ProductReview,Brand
from taggit.models import Tag
from django.db.models import Avg, Q
import math
# Create your views here.
def index(request):
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

def products_list_view(request):
    products = Product.objects.filter(product_status="published")
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

def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status="published", category=category)
    brands = Brand.objects.filter(category=category)
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
    p_images = product.p_images.all()
    related_products = Product.objects.filter(category=product.category, product_status="published")
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
    products = Product.objects.filter(product_status="published").order_by("-id")
    tag= None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {
        'products':products,
    }
    return render(request, 'tag.html', context)

def search_view(request):
    query = request.GET.get('q')
    products = Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__title__icontains=query) | Q(tags__name__icontains=query)).distinct().order_by('-date')
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

    context = {
        'products': products,
        'query':query
    }
    return render(request, 'search.html', context)

def filter_view(request):
    pass
    # context = {
    #     'products':products
    # }
    # return render(request, 'products-list.html', context)
