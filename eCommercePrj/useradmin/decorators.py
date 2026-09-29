from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
def admin_required(view_func):
    @login_required
    def wrapper(request,*args, **kwargs):
        if request.user.is_vendor != True:
            messages.warning(request, "Bu sayfaya girmek icin gerekli izniniz yok.")
            return redirect("/user/signin/")
        return view_func(request,*args, **kwargs)
    
    return wrapper