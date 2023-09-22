from django.shortcuts import render, redirect
from .models import Category
from .models import Product
from django.contrib import messages

# home page
def home(request):
    return render(request, 'shop/index.html')

# registeration
def register(request):
    return render(request, 'shop/register.html')

# Categories
def categories(request):
    categories = Category.objects.filter(status=1)
    return render(request, 'shop/categories.html', {'categories': categories})

# Category products
def categoryProducts(request, name):
    if(Category.objects.filter(name = name)):
        products = Product.objects.filter(category__name = name)
        return render(request, 'shop/products.html', {'products': products})
    else:
        messages.warning(request, 'No such category')
        return redirect('categories')