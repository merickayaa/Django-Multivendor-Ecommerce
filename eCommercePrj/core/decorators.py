from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse

def ajax_login_required(view_func):
    def wrapper(request,*args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error':'Bu işlem için giriş yapmalısınız.', 'login_url':reverse("userauths:signin")}, status=401)
        return view_func(request,*args, **kwargs)
    return wrapper