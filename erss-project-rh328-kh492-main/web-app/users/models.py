from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.core.validators import EmailValidator

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

class UserAccount(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    phone = models.BigIntegerField(default=0)
    cardInfo = models.BigIntegerField(default=0)
    ups_userid = models.IntegerField(default=-1)
    def __str__(self):
        return f'{self.user.username} Account Info'

class Address(models.Model):
    owner = models.ForeignKey(UserAccount, related_name='addresses', on_delete=models.CASCADE)
    addressName = models.CharField(max_length=200, default="")
    tag = models.CharField(max_length=30, default="", blank=True)
    address_x = models.IntegerField(default=-1, blank=True)
    address_y = models.IntegerField(default=-1, blank=True)

    def __str__(self):
        return f'{self.tag}: {self.addressName}, <{self.address_x},{self.address_y}>'

class Category(models.Model):
    category = models.CharField(max_length=20, null = False, blank = False)

    def __str__(self):
        return self.category

class Product(models.Model):
    # product id using default serial int as primary key
    description = models.CharField(max_length=200, null = False, blank = False)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null = True)
    price = models.FloatField(default = 9.99, null = False, blank = False)

    def __str__(self):
        return f'<{self.description}, {self.price}>'

class Warehouse(models.Model):
    truck_id = models.IntegerField(default=-1)
    address_x = models.IntegerField(default=-1)
    address_y = models.IntegerField(default=-1)
    total = models.IntegerField(default = 0)
    def __str__(self):
        return f'({self.address_x}, {self.address_y})'

class WarehouseStock(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    num_product = models.IntegerField(default = 0)

class Package(models.Model):
    customer = models.ForeignKey(User, related_name='packages', on_delete=models.CASCADE)
    truck_id = models.IntegerField(default=-1, blank = True)
    warehouse = models.ForeignKey(Warehouse, related_name='packages', on_delete=models.SET_NULL,null = True)
    address_x = models.IntegerField(default=1)
    address_y = models.IntegerField(default=1)
    pack_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50,default = "PROCESSING")
    """STATUS_CHOICES = (
        PROCESSING = 'processing'
        PACKING = 'PACKING'
        PACKED = 'PACKED'
        LOADING = 'LOADING'
        LOADED = 'LOADED'
        DELIVERING = 'DELIVERING' 
        DELIVERED = 'DELIVERED'
    )"""
    ups_id = models.BigIntegerField(default=-1)
    track_num = models.IntegerField(default = -1)

    def __str__(self):
        return f"{self.customer}'s package at {self.warehouse}, {self.status}"

class Order(models.Model):
    customer = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='orders', on_delete=models.SET_NULL, null = True)
    product_num = models.IntegerField(default = 1)
    package = models.ForeignKey(Package, related_name='orders', on_delete=models.SET_NULL, null = True)
    generate_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.product_num} {self.product} in {self.package}'

class ShoppingCart(models.Model):
    customer = models.ForeignKey(User, related_name='shoppingcart', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='shoppingcart', on_delete=models.SET_NULL, null = True)
    product_num = models.IntegerField(default = 1)
    warehouse = models.ForeignKey(Warehouse, related_name='shoppingcart', on_delete=models.SET_NULL,null = True)
    address_x = models.IntegerField(default=1)
    address_y = models.IntegerField(default=1)
    ups_id = models.IntegerField(default = -1)
    def __str__(self):
        return f'{self.product_num} {self.product}'

class Report(models.Model):
    email = models.EmailField(max_length=254, validators=[EmailValidator()])
    content = models.CharField(max_length=500)
    def __str__(self):
        return self.email