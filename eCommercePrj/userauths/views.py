from django.shortcuts import render, redirect
from userauths.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
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