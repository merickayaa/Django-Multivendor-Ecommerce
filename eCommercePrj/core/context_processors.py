from core.models import Cart,Product,Category,Vendor,CartOrderItems,CartOrder, Wishlist, Address, ProductImages, ProductReview,Brand
from django.conf import settings
def default(request):
    categories = Category.objects.all()
    try:
        address = Address.objects.get(user=request.user)
    except:
        address=None
    try:
        cart = Cart.objects.filter(user=request.user)
    except:
        cart = None
        
    return {
        'categories':categories,
        'address':address,
        'cart':cart,
        "MEDIA_URL":settings.MEDIA_URL,
    }
