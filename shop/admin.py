from django.contrib import admin
from .models import Category
from .models import SubCategory
from .models import Product

# Over writing the category model for admin only
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'description')

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'description')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_image', 'category_id')

admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Product, ProductAdmin)
