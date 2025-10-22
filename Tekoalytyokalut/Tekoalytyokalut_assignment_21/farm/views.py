from django.shortcuts import render
from .models import Product, Service

def home(request):
    return render(request, "home.html")

def products(request):
    items = Product.objects.all()
    return render(request, "products.html", {"items": items})

def services(request):
    items = Service.objects.all()
    return render(request, "services.html", {"items": items})
