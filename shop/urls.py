from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register, name='register'),
    path('login', views.login_page, name='login'),
    path('logout', views.logout_page, name='logout'),
    path('categories', views.categories, name='categories'),
    path('category/<str:name>', views.categoryProducts, name='category'),
    path('product/<str:name>', views.productDetails, name='product'),

    # add to cart - ajax request
    path('add_cart', views.add_to_cart, name='cart_add'),
    path('carts', views.cart_list, name='carts'),
    path('cart_delete/<int:cart_id>', views.cart_delete, name='cart_delete'),

    # order
    path('create_order', views.create_order, name='create_order'),
    path('callback', views.callback, name='callback')
]
