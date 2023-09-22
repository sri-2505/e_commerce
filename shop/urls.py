from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register, name='register'),
    path('categories', views.categories, name='categories'),
    path('category/<str:name>', views.categoryProducts, name='category'),
]
