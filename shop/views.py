from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import F, ExpressionWrapper, FloatField, Prefetch, Count

# forms
from shop.forms.userRegisterationForm import CustomUserForm
from shop.forms.LoginForm import LoginForm
from shop.forms.orderForm import OrderForm

# models
from .models import (
    Category,
    SubCategory,
    Product,
    Cart,
    Order,
    OrderItem
    )

# core python
import json
import os
from dotenv import load_dotenv

# constant helper
from utils.constants import *
from utils.helper import (
    razorpay_login,
    getRazorPayAmount,
    verify_signature
)

load_dotenv()


# home page
def home(request):
    best_deals = Product.objects.active_products().annotate(price_difference = ExpressionWrapper(
        ((F('original_price') - F('selling_price')) * F('original_price')) * 100,
        output_field = FloatField()
    )).order_by('price_difference').values()[:12]

    new_arrivals = Product.objects.active_products().order_by('created_at').values()[:12]

    categories_with_data =  Category.objects.prefetch_related(
        Prefetch('subcategories',
                queryset = SubCategory.objects.prefetch_related(
                    Prefetch(
                        'products',
                        queryset = Product.objects.all()[:12],
                        to_attr = 'limited_products'
                       )
                    ),
                to_attr = 'all_subcategories'
                )
            )
    return render(request, 'shop/index.html', {'best_deals': best_deals, 'new_arrivals': new_arrivals, 'categories_with_data': categories_with_data})


# registeration
def register(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successfully completed. Please login...")
            return redirect('login')
    else:
        form = CustomUserForm()

    return render(request, 'shop/register.html', {'form': form})


# login
def login_page(request):
    if request.method == 'POST':
        user_name = request.POST.get('username')
        pass_word = request.POST.get('password')
        user = authenticate(request, username=user_name, password=pass_word)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Invalid user name or password')
            return redirect('/login')
    else:
        form = LoginForm()

    if 'next' in request.GET:
        messages.info(request, 'Login to continue...')

    return render(request, 'shop/login.html', {'form': form})


# logout
@login_required(login_url='/login')
def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Logout successfully!')
        return redirect('/')


# Categories
def categories(request):
    categories = Category.objects.all()
    return render(request, 'shop/categories.html', {'categories': categories})


# Category products
def categoryProducts(request, name):
    try:
        Category.objects.filter(name=name).get()
        products = Product.objects.filter(category__name=name, status=1)
        return render(request, 'shop/products/products.html', {'products': products, 'category': name})
    except Category.DoesNotExist:
        messages.warning(request, 'No such category')
        return redirect('categories')


# product details
def productDetails(request, name):
    try:
        product = Product.objects.filter(name=name, status=1).get()
        return render(request, 'shop/products/product.html', {'product': product, 'category': product.category})
    except Product.DoesNotExist:
        messages.warning(request, 'No such product')
        return redirect('categories')


# add to cart
@login_required(login_url='/login')
def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            product_id = data['product_id']
            quantity = data['quantity']
            product = Product.objects.get(pk=product_id)
            if product and product.status and product.quantity >= quantity:
                cart = Cart.objects.filter(user=request.user, product=product_id).first()
                if cart:
                    if cart.quantity != quantity:
                        cart.quantity = quantity
                        cart.save()

                        return JsonResponse({'status': 'Cart updated!'})
                    else:
                        return JsonResponse({'status': 'Product already added to Cart'})
                else:
                    Cart.objects.create(
                        user=request.user,
                        product=product,
                        quantity=quantity
                    )

                    return JsonResponse({'status': 'Product added to cart'})
            else:
                return JsonResponse({'status': 'Product not available'})
        else:
            return JsonResponse({'status': 'Login to add cart items'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid access'}, status=200)


# cart list
@login_required(login_url='/login')
def cart_list(request):
    if request.user.is_authenticated:
        user = request.user
        # cart_set is a reverse relationship
        carts = Cart.objects.filter(user=user).select_related('product')
        return render(request, 'shop/cart/cart_list.html', {'carts': carts})
    else:
        messages.warning(request, 'Login to see your cart list.')
        return redirect('/login')


# delete the cart
@login_required
def cart_delete(request, cart_id):
    try:
        Cart.objects.filter(pk=cart_id).delete()
        messages.warning(request, 'Cart removed')
    except Cart.DoesNotExist:
        messages.warning(request, 'Cart not found')

    return redirect('carts')


# create order
@login_required(login_url='/login')
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form_values = form.cleaned_data
            product_id = request.POST.get('product_id')
            order_quantity = int(request.POST.get('order_quantity'))
            order_amount = float(request.POST.get('order_amount'))

            # order creation
            form_values['user_id'] = request.user.id
            form_values['ordered_date'] = timezone.now()
            form_values['payment_status'] = PENDING
            form_values['order_status'] = PENDING
            form_values['amount'] = order_amount
            # create a unique order number
            form_values['order_number'] = '222'

            # razor pay login
            razor_pay_client = razorpay_login()
            razor_pay_order = razor_pay_client.order.create({
                "amount": getRazorPayAmount(order_amount),
                "currency": INR,
                "payment_capture": "0"
            })
            form_values['provider_order_id'] = razor_pay_order['id']
            order = Order.objects.create(**form_values)

            context = {
                'callback_url': HTTP + os.getenv('DEV_URL') + '/callback',
                'razorpay_kay': os.getenv('RAZOR_KEY_ID'),
                'razorpay_order_id': razor_pay_order['id'],
                'currency': INR,
                'amount': order_amount
            }

            return render(request, 'shop/order/payment.html', context)
    else:
        form = OrderForm()
        product_id = request.GET.get('product_id')
        order_quantity = int(request.GET.get('quantity'))
        product = Product.objects.values().get(id=product_id)

        product['order_quantity'] = order_quantity
        product['order_amount'] = order_quantity * product['selling_price']

        context = {
            'form': form,
            'districts': DISTRICTS,
            'product': product,

        }

        return render(request, 'shop/order/create_order.html', context)


@csrf_exempt
def callback(request):
    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()
        if not verify_signature(request.POST):
            order.status = COMPLETED
            order.save()
            return render(request, "shop/order/callback.html", context={"status": order.status})
        else:
            order.status = ERROR
            order.save()
            return render(request, "shop/order/callback.html", context={"status": order.status})
    else:
        payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        provider_order_id = json.loads(request.POST.get("error[metadata]")).get(
            "order_id"
        )
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.status = ERROR
        order.save()
        return render(request, "shop/order/callback.html", context={"status": 'failed'})
