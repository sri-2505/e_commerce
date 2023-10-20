from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
import os
from utils.constants import *

# model functions
def getFileName(request, file_name) -> str:
    date_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    new_file_name = "%s%s"%(date_time, file_name)
    return os.path.join('uploads/', new_file_name)

# Category model
# TODO::add plurel names to models
class Category(models.Model):
    name = models.CharField(max_length = 255, null = False, blank = False)
    image = models.ImageField(upload_to = getFileName, null = True, blank = True)
    description = models.TextField(max_length = 500, null = False, blank = False)
    status = models.BooleanField(default = False, help_text = "1-show, 0-hidden")
    trending = models.BooleanField(default = False, help_text = "0-default, 1-trending")
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    name = models.CharField(max_length = 255, null = False, blank=False)
    product_image = models.ImageField(upload_to = getFileName, null = True, blank = True)
    quantity = models.IntegerField(null = False, blank = False)
    original_price = models.FloatField(default = 0.00, null = False, blank = False)
    selling_price = models.FloatField(default = 0.00, null = False, blank = False)
    description = models.TextField(max_length = 500, null = False, blank = False)
    status = models.BooleanField(default = False, help_text = "1-show, 0-hidden")
    trending = models.BooleanField(default = False, help_text = "0-default, 1-trending")
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self) -> str:
        return self.name

# shopping cart
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.IntegerField(null = False, blank = False)
    # To add the blow columns to existing table first migrate with only default parameter and them migrate with auto_now 
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        unique_together = ('user', 'product')

    @property
    def total_cost(self):
        return self.quantity * self.product.selling_price

    def __str__(self) -> str:
        return str(self.quantity)
    
# create order
class Order(models.Model):

    payment_status = [
        ('completed', COMPLETED),
        ('pending', PENDING),
        ('in_progres', IN_PROGRES),
        ('error', ERROR)
    ]

    order_status = [
        ('shipped', SHIPPED), # on transport
        ('delivered', DELIVERED), # order completed
        ('in_progres', IN_PROGRES), # packing in progres
        ('cancelled', CANCELLED) # order cancelled
    ]

    user = models.ForeignKey(User, on_delete = models.CASCADE)
    order_number = models.CharField(max_length = 100, null = False, blank = False)
    amount = models.FloatField(default = 0.00, null = False, blank = False)
    street_name = models.CharField(max_length = 100, null = False, blank = False)
    city = models.CharField(max_length = 100, null = False, blank = False)
    district = models.CharField(max_length = 100, null = False, blank = False)
    state = models.CharField(max_length = 100, null = False, blank = False)
    pincode = models.CharField(max_length = 100, null = False, blank = False)
    ordered_date = models.DateTimeField()
    payment_type = models.CharField(max_length = 100, choices = PAYMENT_TYPES)
    payment_status = models.CharField(max_length = 100, choices = payment_status)
    order_status = models.CharField(max_length = 100, choices = order_status)
    provider_order_id = models.CharField(
        max_length=100, null=False, blank=False
    )
    payment_id = models.CharField(
        max_length = 100, null = False, blank = False
    )
    signature_id = models.CharField(
        max_length = 100, null = False, blank = False
    )
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self) -> str:
        return str(self.order_number)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete = models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.IntegerField(default = 0)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self) -> str:
        return str(self.order_number)
