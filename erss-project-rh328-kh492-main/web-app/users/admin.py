from django.contrib import admin
from .models import *
admin.site.register(Category)
admin.site.register(Warehouse)
admin.site.register(Product)
admin.site.register(Person)
admin.site.register(ShoppingCart)
admin.site.register(WarehouseStock)

admin.site.register(Package)
admin.site.register(Order)
# admin.site.register(Driver)