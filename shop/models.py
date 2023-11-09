from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
import datetime
import os
from utils.constants import *
import uuid
from django.utils import timezone


# custom user manager
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Email is required')

        user = self.model(
            email=self.normalize_email(email),
            username=username
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email,
            password=password,
            username=username,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


# custom user model
class User(AbstractUser):
    username = models.CharField(max_length=50, blank=False)
    email = models.EmailField(max_length=255, unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        if self.is_admin:
            return True
        else:
            return False

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        if self.is_admin:
            return True
        else:
            return False

    @property
    def is_staff(self):
        return self.is_admin


# give file name while uploading
def get_file_name(request, file_name) -> str:
    date_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    new_file_name = "%s%s" % (date_time, file_name)
    return os.path.join('uploads/', new_file_name)


# Extending model managers
class ProductQuerySet(models.QuerySet):
    def active_products(self):
        return self.filter(status=1)

    def exclusive_products(self):
        return self.filter(is_exclusive=1)


# Category model
class Category(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    image = models.ImageField(upload_to=get_file_name, null=True, blank=True)
    status = models.BooleanField(default=False, help_text="1-show, 0-hidden")
    description = models.TextField(max_length=500, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


# sub categories
class SubCategory(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_file_name, null=True, blank=True)
    description = models.TextField(max_length=500, null=False, blank=False)
    status = models.BooleanField(default=False, help_text="1-show, 0-hidden")
    trending = models.BooleanField(default=False, help_text="0-default, 1-trending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False, blank=False)
    product_image = models.ImageField(upload_to=get_file_name, null=True, blank=True)
    quantity = models.IntegerField(null=False, blank=False)
    original_price = models.FloatField(default=0.00, null=False, blank=False)
    selling_price = models.FloatField(default=0.00, null=False, blank=False)
    description = models.TextField(max_length=500, null=False, blank=False)
    status = models.BooleanField(default=False, help_text="1-show, 0-hidden")
    trending = models.BooleanField(default=False, help_text="0-default, 1-trending")
    is_exclusive = models.BooleanField(default=False, help_text="0-default, 1-exclusive")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name


# shopping cart
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False)
    # To add the blow columns to existing table first migrate with only default parameter and them migrate with auto_now
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')

    @property
    def total_final_cost(self):
        return self.quantity * self.product.selling_price

    @property
    def total_net_cost(self):
        return self.quantity * self.product.original_price

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
        ('shipped', SHIPPED),  # on transport
        ('delivered', DELIVERED),  # order completed
        ('in_progres', IN_PROGRES),  # packing in progres
        ('cancelled', CANCELLED)  # order cancelled
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.UUIDField(default=uuid.uuid4, editable=False)
    amount = models.FloatField(default=0.00, null=False, blank=False)
    street_name = models.CharField(max_length=100, null=False, blank=False)
    city = models.CharField(max_length=100, null=False, blank=False)
    district = models.CharField(max_length=100, null=False, blank=False)
    state = models.CharField(max_length=100, null=False, blank=False)
    pincode = models.CharField(max_length=100, null=False, blank=False)
    ordered_date = models.DateTimeField()
    payment_type = models.CharField(max_length=100, choices=PAYMENT_TYPES)
    payment_status = models.CharField(max_length=100, choices=payment_status)
    order_status = models.CharField(max_length=100, choices=order_status)
    provider_order_id = models.CharField(
        max_length=100, null=False, blank=False
    )
    payment_id = models.CharField(
        max_length=100, null=False, blank=False
    )
    signature_id = models.CharField(
        max_length=100, null=False, blank=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.order_number)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    amount = models.FloatField(default=0.00, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('order', 'product')
