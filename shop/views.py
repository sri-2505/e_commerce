import datetime

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import F, ExpressionWrapper, FloatField, Prefetch, Count, Subquery, OuterRef
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.template.loader import get_template
import logging

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
from shop.celery.tasks import send_order_details_mail
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

logger = logging.getLogger('django')
load_dotenv()


# home page
def home(request):
    try:
        best_deals = Product.objects.active_products().annotate(price_difference=ExpressionWrapper(
            ((F('original_price') - F('selling_price')) * F('original_price')) * 100,
            output_field=FloatField()
        )).order_by('price_difference').values()[:12]

        new_arrivals = Product.objects.active_products().order_by('created_at').values()[:12]

        categories_with_data = Category.objects.annotate(subcategory_count=Count('subcategories')).filter(
            subcategory_count__gt=0
        ).prefetch_related(
            Prefetch('subcategories',
                     queryset=SubCategory.objects.prefetch_related(
                         Prefetch(
                             'products',
                             queryset=Product.objects.filter(category=F('subcategory__category')).filter(
                                 subcategory=F('subcategory'))[:12],
                             to_attr='limited_products'
                         )
                     ).annotate(
                         product_count=Subquery(
                             Product.objects.filter(
                                 category=OuterRef('category'),
                             ).filter(
                                 subcategory=OuterRef('pk')
                             ).annotate(product_count=Count('id')).values('product_count')[:1]
                         )
                     ).filter(
                         product_count__gt=0
                     ),
                     to_attr='all_subcategories'
                     )
        )

        return render(request, 'shop/index.html', {'best_deals': best_deals, 'new_arrivals': new_arrivals,
                                               'categories_with_data': categories_with_data})
    except Exception as e:
        logger.error('something went wrong in home page - {e}')
        return render(request,'shop/status_pages/something_went_wrong.html', {'status_code': 500, 'message': 'Something Went Wrong!'})


# registeration
def register(request):
    try:
        if request.method == 'POST':
            form = CustomUserForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Registration successfully completed. Please login...")
                return redirect('login')
        else:
            form = CustomUserForm()
    
        return render(request, 'shop/authentication/register.html', {'form': form})
    except Exception as e:
        logger.error('something went wrong in register view - {e}')
        messages.success(request, "Something went wrong while registration. Please try after sometimes")
        return redirect(request.META.get('HTTP_REFERER'), '/')

# login
def login_page(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            pass_word = request.POST.get('password')
            user = authenticate(request, username=email, password=pass_word)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                messages.error(request, 'Invalid email or password')
                return redirect('/login')
        else:
            form = LoginForm()

        if 'next' in request.GET:
            messages.info(request, 'Login to continue...')

        return render(request, 'shop/authentication/login.html', {'form': form})
    except Exception as e:
        logger.error('something went wrong in login view  - {e}')
        messages.success(request, "Something went wrong while login. Please try after sometimes")
        return redirect(request.META.get('HTTP_REFERER'), '/')


# logout
@login_required()
def logout_page(request):
    try:
        if request.user.is_authenticated:
            logout(request)
            messages.success(request, 'Logout successfully!')
            return redirect('/')
    except Exception as e:
        logger.error('something went wrong in logout view  - {e}')
        messages.success(request, "Something went wrong while logout. Please try after sometimes")
        return redirect(request.META.get('HTTP_REFERER'), '/')

# Categories
def categories(request, category=None):
    try:
        categories = Category.objects.annotate(subcategory_count=Count('subcategories')).filter(
            subcategory_count__gt=0
        ).prefetch_related(
            Prefetch('subcategories',
                     queryset=SubCategory.objects.prefetch_related(
                         Prefetch(
                             'products',
                             queryset=Product.objects.filter(category=F('subcategory__category')).filter(
                                 subcategory=F('subcategory'))[:12],
                             to_attr='limited_products'
                         )
                     ).annotate(
                         product_count=Subquery(
                             Product.objects.filter(
                                 category=OuterRef('category'),
                             ).filter(
                                 subcategory=OuterRef('pk')
                             ).annotate(product_count=Count('id')).values('product_count')[:1]
                         )
                     ).filter(
                         product_count__gt=0
                     ),
                     to_attr='all_subcategories'
                     )
        )

        if category is not None:
            categories = categories.filter(name=category)

        if not categories.exists():
            messages.info(request, 'No products found on this category. Please visit later...')
            return redirect(request.META.get('HTTP_REFERER'), '/')

        return render(request, 'shop/categories.html', {'categories': categories})
    except Exception as e:
        logger.error('something went wrong in categories view - {e}')
        return render(request,'shop/status_pages/something_went_wrong.html', {'status_code': 500, 'message': 'Something Went Wrong!'})



# Category products
def subcategory_products(request, category_id, subcategory_id=None):
    try:
        products = Product.objects.active_products().filter(category_id=category_id, subcategory_id=subcategory_id)
        paginator = Paginator(products, PRODUCTS_LIMIT_PER_PAGE)
        no_of_pages = paginator.num_pages
        page_numbers = range(1, no_of_pages + 1)
        page_number = request.GET.get('page_number', 1)
        products = paginator.get_page(page_number)
        return render(request, 'shop/products/subcategory_products.html',
                      {'products': products, 'page_numbers': page_numbers})
    except Category.DoesNotExist:
        messages.warning(request, 'No such category')
        return redirect('categories')
    except Exception as e:
        logger.error('something went wrong in subcategory products view - {e}')
        return render(request,'shop/status_pages/something_went_wrong.html', {'status_code': 500, 'message': 'Something Went Wrong!'})


# product details
def product_details(request, id):
    try:
        product = Product.objects.get(pk=id)
        return render(request, 'shop/products/product.html', {'product': product, 'category': product.category})
    except Product.DoesNotExist:
        messages.warning(request, 'No such product')
        return redirect('categories')
    except Exception as e:
        logger.error('something went wrong in product_details view - {e}')
        return render(request,'shop/status_pages/something_went_wrong.html', {'status_code': 500, 'message': 'Something Went Wrong!'})

# add to cart
@login_required()
def add_to_cart(request):
    try:
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
    except Exception as e:
        logger.error('something went wrong in add_to_cart view - {e}')
        return JsonResponse({'status': 'Something went wrong'}, status=500)

# cart list
@login_required()
def cart_list(request):
    try:
        if request.user.is_authenticated:
            user = request.user
            # cart_set is a reverse relationship
            carts = Cart.objects.filter(user=user, is_purchased=False).select_related('product')
            total_final_amount = sum(cart.total_final_cost for cart in carts)
            total_net_amount = sum(cart.total_net_cost for cart in carts)
            delivery_charges = 0
            gst = 0

            context = {
                'carts': carts,
                'total_net_amount': total_net_amount,
                'delivery_charges': delivery_charges,
                'gst': gst,
                # will move to the cart property one gst and delivery logic completed
                'total_final_amount': total_final_amount - delivery_charges - gst,
            }
            return render(request, 'shop/cart/cart_list.html', context=context)
        else:
            messages.warning(request, 'Login to see your cart list.')
            return redirect('/login')
    except Exception as e:
        logger.error('something went wrong in register view - {e}')
        return render(request,'shop/status_pages/something_went_wrong.html', {'status_code': 500, 'message': 'Something Went Wrong!'})


# delete the cart
@login_required
def cart_delete(request, cart_id):
    try:
        Cart.objects.filter(pk=cart_id).delete()
        messages.warning(request, 'Cart removed')
        return redirect('carts')
    except Cart.DoesNotExist:
        messages.warning(request, 'Cart not found')
        return redirect(request.META.get('HTTP_REFERER'), '/')
    except Exception as e:
        logger.error('something went wrong in cart_delete view  - {e}')
        messages.success(request, "Something went wrong while removing cart. Please try after sometimes")
        return redirect(request.META.get('HTTP_REFERER'), '/')


# create order
@login_required()
def create_order(request):
    try:
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

                # razor pay login
                razor_pay_client = razorpay_login()
                razor_pay_order = razor_pay_client.order.create({
                    "amount": getRazorPayAmount(order_amount),
                    "currency": INR,
                    "payment_capture": "0"
                })
                form_values['provider_order_id'] = razor_pay_order['id']
                order = Order.objects.create(**form_values)
                order_item = OrderItem.objects.create(
                    order=order,
                    product_id=product_id,
                    amount=order_amount,
                    quantity=order_quantity
                )

                context = {
                    'callback_url': HTTP + os.getenv('DEV_URL') + '/callback',
                    'razorpay_kay': os.getenv('RAZOR_KEY_ID'),
                    'razorpay_order_id': razor_pay_order['id'],
                    'currency': INR,
                    'amount': order_amount
                }
                if form_values['payment_type'] == ONLINE_PAYMENT.replace(' ', '_'):
                    return render(request, 'shop/order/payment.html', context)
                else:
                    mail_context = {
                        'user_name': request.user.username,
                        'order': order,
                        'order_item': order_item
                    }

                    body = get_template('shop/mail/order_placed.html').render(mail_context)

                    send_order_details_mail.delay(request.user.email, body)

                    context = {
                        'order': order
                    }
                    return render(request, 'shop/order/order_details.html', context)
        else:
            form = OrderForm()
            product_id = request.GET.get('product_id')
            order_quantity = int(request.GET.get('quantity'))
            product = Product.objects.values().get(id=product_id)

            product['order_quantity'] = order_quantity
            product['order_amount'] = order_quantity * product['selling_price']

            context = {
                'form': form,
                'districts': TAMIL_NADU_DISTRICTS,
                'product': product,
            }

            return render(request, 'shop/order/create_order.html', context)
    except Exception as e:
        logger.error('something went wrong in creat_order view - {e}')
        return render(request,'shop/status_pages/something_went_wrong.html', {'status_code': 500, 'message': 'Something Went Wrong!'})

@csrf_exempt
def callback(request):
    try:
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
                Cart.objects.filter(user=order.user).update(created_at__gt=timezone.now(), is_purchased=True)
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
    except Exception as e:
        logger.error('something went wrong in razorpay call back view - {e}')
        return render(request,'shop/status_pages/something_went_wrong.html', {'status_code': 500, 'message': 'Something Went Wrong!'})


# exclusive products
def exclusive(request, subcategory=None):
    try:
        exclusive_products = SubCategory.objects.prefetch_related(
            Prefetch(
                'products',
                queryset=Product.objects.active_products().all()[:12],
                to_attr='limited_products'
            )
        )
        if subcategory is not None:
            if not SubCategory.objects.filter(name=subcategory).exists():
                messages.warning(request, "No such subcategory")
                return redirect('home')
            else:
                exclusive_products = exclusive_products.filter(name=subcategory)

        return render(request, "shop/products/exclusive_products.html", {"exclusive_products": exclusive_products})
    except Exception as e:
        logger.error('something went wrong in exclusive view - {e}')
        return render(request,'shop/status_pages/something_went_wrong.html', {'status_code': 500, 'message': 'Something Went Wrong!'})



@login_required()
def order_details(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        return render(request, 'shop/order/order_details.html', {'order': order})
    except Order.DoesNotExist:
        messages.warning(request, 'No such order')
        return redirect('orders')
    except Exception as e:
        logger.error('something went wrong in order_detials view - {e}')
        return render(request,'shop/status_pages/something_went_wrong.html', {'status_code': 500, 'message': 'Something Went Wrong!'})



@login_required()
def order_list(request):
    try:
        orders = Order.objects.filter(user=request.user).prefetch_related('orderitem_set__product').order_by(
            '-ordered_date')

        paginator = Paginator(orders, ORDERS_LIMIT_PER_PAGE)
        no_of_pages = paginator.num_pages
        page_numbers = range(1, no_of_pages + 1)
        page_number = request.GET.get('page_number', 1)
        orders = paginator.get_page(page_number)

        return render(request, 'shop/order/order_list.html', {'orders': orders, 'page_numbers': page_numbers})
    except Exception as e:
        logger.error('something went wrong in order_list view - {e}')
        return render(request,'shop/status_pages/something_went_wrong.html', {'status_code': 500, 'message': 'Something Went Wrong!'})


@login_required()
def checkout(request):
    try:
        if request.method == 'POST':
            form = OrderForm(request.POST)
            if form.is_valid():
                form_values = form.cleaned_data

                user = request.user
                carts = Cart.objects.filter(user=user).select_related('product')
                total_final_amount = sum(cart.total_final_cost for cart in carts)
                delivery_charges = 0
                gst = 0
                order_amount = total_final_amount + delivery_charges + gst

                # order creation
                form_values['user_id'] = request.user.id
                form_values['ordered_date'] = timezone.now()
                form_values['payment_status'] = PENDING
                form_values['order_status'] = PENDING
                form_values['amount'] = order_amount

                # razor pay login
                razor_pay_client = razorpay_login()
                razor_pay_order = razor_pay_client.order.create({
                    "amount": getRazorPayAmount(order_amount),
                    "currency": INR,
                    "payment_capture": "0"
                })
                form_values['provider_order_id'] = razor_pay_order['id']

                order = Order.objects.create(**form_values)
                order_items = []
                for cart in carts:
                    order_items.append(OrderItem(
                        order=order,
                        product=cart.product,
                        amount=cart.total_final_cost,
                        quantity=cart.quantity
                    ))

                OrderItem.objects.bulk_create(order_items)

                context = {
                    'callback_url': HTTP + os.getenv('DEV_URL') + '/callback',
                    'razorpay_kay': os.getenv('RAZOR_KEY_ID'),
                    'razorpay_order_id': razor_pay_order['id'],
                    'currency': INR,
                    'amount': order_amount
                }
                if form_values['payment_type'] == ONLINE_PAYMENT.replace(' ', '_'):
                    return render(request, 'shop/order/payment.html', context)
                else:
                    mail_context = {
                        'user_name': request.user.username,
                        'order': order,
                        'order_items': order_items
                    }

                    body = get_template('shop/mail/order_placed.html').render(mail_context)

                    send_order_details_mail.delay(request.user.email, body)

                    Cart.objects.filter(user=request.user).update(created_at__gt=timezone.now(), is_purchased=True)

                    context = {
                        'order': order
                    }
                    return render(request, 'shop/order/order_details.html', context)
        else:
        form = OrderForm()
        user = request.user

        # cart_set is a reverse relationship
        carts = Cart.objects.filter(user=user)
        total_final_amount = sum(cart.total_final_cost for cart in carts)
        total_net_amount = sum(cart.total_net_cost for cart in carts)
        delivery_charges = 0
        gst = 0

        context = {
            'form': form,
            'districts': TAMIL_NADU_DISTRICTS,
            'total_final_amount': total_final_amount,
            'total_net_amount': total_net_amount,
            'delivery_charges': delivery_charges,
            'gst': gst
        }
        return render(request, 'shop/cart/checkout.html', context)
    except Exception as e:
        logger.error('something went wrong in checkout view - {e}')
        return render(request,'shop/status_pages/something_went_wrong.html', {'status_code': 500, 'message': 'Something Went Wrong!'})



def subcategories(request, subcategory=None):
    try:
        is_exclusive = request.GET.get('exclusive')
        is_best_deals = request.GET.get('best_deals')

        products_query = Product.objects.filter(
            subcategory=F('subcategory')
        )

        if is_exclusive:
            products_query = products_query.filter(is_exclusive=1).order_by('created_at')

        if is_best_deals:
            products_query = products_query.annotate(price_difference=ExpressionWrapper(
                ((F('original_price') - F('selling_price')) * F('original_price')) * 100,
                output_field=FloatField()
            )).order_by('price_difference')

        subcategories = SubCategory.objects.prefetch_related(
            Prefetch(
                'products',
                queryset=products_query[:12],
                to_attr='limited_products'
            )
        ).annotate(
            product_count=Count('products')
        ).filter(
            product_count__gt=0
        )

        if subcategory is not None:
            if not SubCategory.objects.filter(name=subcategory).exists():
                messages.warning(request, "No such subcategory")
                return redirect('home')
            else:
                subcategories = subcategories.filter(name=subcategory)

        return render(request, 'shop/products/subcategories.html', {'subcategories': subcategories})
    except Exception as e:
        logger.error('something went wrong in razorpayt call back view - {e}')
        return render(request,'shop/status_pages/something_went_wrong.html', {'status_code': 500, 'message': 'Something Went Wrong!'})



# favorites - similar to cart
def favorite(request):
    try:
        return render(request, 'shop/status_pages/coming_soon.html')
    except Exception as e:
        logger.error('something went wrong in favorite view - {e}')
        return render(request,'shop/status_pages/something_went_wrong.html', {'status_code': 500, 'message': 'Something Went Wrong!'})


def user_profile(request):
    try:
        return render(request, 'shop/status_pages/coming_soon.html')
    except Exception as e:
        logger.error('something went wrong in user profile view - {e}')
        return render(request,'shop/status_pages/something_went_wrong.html', {'status_code': 500, 'message': 'Something Went Wrong!'})
