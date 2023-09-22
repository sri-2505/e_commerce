from django.db import models
import datetime
import os

def getFileName(request, file_name) -> str:
    date_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    new_file_name = "%s%s"%(date_time, file_name)
    return os.path.join('uploads/', new_file_name)

# Category model
# TODO::add plurel names to models
class Category(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    image = models.ImageField(upload_to=getFileName, null=True, blank=True)
    description = models.TextField(max_length=500, null=False, blank=False)
    status = models.BooleanField(default=False, help_text="1-show, 0-hidden")
    trending = models.BooleanField(default=False, help_text="0-default, 1-trending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False, blank=False)
    product_image = models.ImageField(upload_to=getFileName, null=True, blank=True)
    quantity = models.IntegerField(null = False, blank = False)
    original_price = models.FloatField(default=0.00, null = False, blank = False)
    selling_price = models.FloatField(default=0.00, null = False, blank = False)
    description = models.TextField(max_length=500, null=False, blank=False)
    status = models.BooleanField(default=False, help_text="1-show, 0-hidden")
    trending = models.BooleanField(default=False, help_text="0-default, 1-trending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name