from django.shortcuts import render
from userauths.models import User
# Create your views here.
def index(request):
    return render(request, 'index.html')