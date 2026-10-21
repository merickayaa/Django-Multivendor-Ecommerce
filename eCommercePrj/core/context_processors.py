from core.models import Cart,Product,Category,Vendor,CartOrderItems,CartOrder, Wishlist, Address, ProductImages, ProductReview,Brand
from django.conf import settings
def default(request):
    categories = Category.objects.all()
    try:
        cart = Cart.objects.filter(user=request.user)
    except:
        cart = None
        
    return {
        'categories':categories,
        'cart':cart,
        "MEDIA_URL":settings.MEDIA_URL,
    }
