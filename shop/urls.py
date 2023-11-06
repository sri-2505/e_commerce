from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register, name='register'),
    path('login', views.login_page, name='login'),
    path('logout', views.logout_page, name='logout'),

    # category
    path('category/<str:category>', views.categories, name='category_with_argument'),
    path('categories', views.categories, name='categories'),

    # subcategory - products
    path('category/<int:category_id>/subcategory/<int:subcategory_id>', views.subcategory_products, name='subcategory_products'),

    # subcategory products - all, exclusive, best deals
    path('subcategories', views.subcategories, name='subcategories'),
    path('subcategories/<str:subcategory>', views.subcategories, name='exclusive_with_argument'),

    # product details
    path('product/<int:id>', views.productDetails, name='product'),


    # add to cart - ajax request
    path('add_cart', views.add_to_cart, name='cart_add'),
    path('carts', views.cart_list, name='carts'),
    path('cart_delete/<int:cart_id>', views.cart_delete, name='cart_delete'),
    path('checkout', views.checkout, name='checkout'),

    # order
    path('create_order', views.create_order, name='create_order'),
    path('callback', views.callback, name='callback'),
    path('order_details/<int:order_id>', views.order_details, name='order_details'),
    path('order_list', views.order_list, name='order_list'),
]

