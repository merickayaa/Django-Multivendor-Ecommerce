from django.shortcuts import render, redirect
from userauths.models import User,Profile
from core.models import Address
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.
def signUp(request):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        passwordagain = request.POST['passwordagain']
        errors = []
        if password != passwordagain:
            errors.append("Şifreler uyuşmuyor.")
        elif password == passwordagain:
            try:
                validate_password(password, user=User)
            except ValidationError as e:
                errors.extend(e.messages)
                
        if User.objects.filter(username=username):
            errors.append("Bu kullanıcı adı zaten alınmış.")
        if User.objects.filter(email=email).exists():
            errors.append("Bu e-posta zaten kayıtlı.")

        if errors:
            context = {
                'errors':errors
            }
            return render(request,"register.html", context)
        user = User.objects.create_user(first_name=firstname,last_name=lastname,username=username,email=email,password=password)
        user.save()
        return redirect('userauths:signin')
    else:
        return render(request, "register.html")

def signIn(request):
    errors = []
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request,user)
            return redirect('index')
        else:
            errors.append("Hatali Giris")
            context = {
                'errors':errors
            }
            return render(request, "login.html", context)
    else: 
        return render(request, "login.html")

@login_required(login_url='userauths:signin')
def logOut(request):
    logout(request)
    return redirect('userauths:signin')


def profile_edit(request):    
    if request.method == "POST":
        profile = Profile.objects.get(user=request.user)
        try:
            profile.full_name = request.POST.get('full_name',profile.full_name)
            profile.bio = request.POST.get('bio',profile.bio)
            profile.phone = request.POST.get('phone',profile.phone)
            profile.country = request.POST.get('country',profile.country)
            address_title = request.POST.get('address_title', None)
            address = Address.objects.filter(user=request.user, title=address_title).first()
            if address:
                profile.address = address.address
            if 'image' in request.FILES:
                profile.image = request.FILES.get('image',profile.image)
            profile.save()
            messages.success(request, "Profil başarıyla güncellendi!")
        except Exception as e:
            messages.error(request, f"Bir hata oluştu: {e}")
        return redirect("dashboard")
        
    return redirect("dashboard")
