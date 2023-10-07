import os
import world_amazon_pb2 
import amazon_ups_pb2 
from django.db.models import Q
import threading
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amazon.settings")
if django.VERSION >= (1, 7):
    django.setup()
import funcs
from users.models import *


# def updateInventory(package_id):
#     try:
#         print(f'start change inventory of warehouse')
#         curPackage = Package.objects.get(id = package_id)
#         curWh = curPackage.warehouse
#         curOrder = Order.objects.get(package = curPackage)
#         product_num = curOrder.product_num
#         curWh.total += product_num
#         curWh.save()
#         curtotal = curWh.total
#         print(f'total is {curtotal}')
#     except Exception as e:
#         print(e)

def changeAddress(shipid, x, y):
    try:
        print(f'start change address of package')
        curpackage = Package.objects.filter(id = shipid)
        curpackage.update(address_x = x)
        curpackage.update(address_y = y)
    except Exception as e:
        print(e)
    return

def changeStatus(shipid, st):
    try:
        print(f'start change status of package to ', str(st))
        curpackage = Package.objects.get(id = shipid)
        print('changing')
        curpackage.status = st
        print('change to ', curpackage.status)
        curpackage.save()
        print('changed')
    except Exception as e:
        print(e)
    return

def returnDescribe(shipid):
    curpackage = Package.objects.get(id=shipid)
    curorder = Order.objects.filter(package=curpackage).first()  # Get the first order associated with the package
    if curorder:  # Check if there is an order associated with the package
        curproduct = curorder.product
        if curproduct:  # Check if there is a product associated with the order
            des = curproduct.description
            print(des)

def updateInventoryPacked(package_id):
    curPackage = Package.objects.get(id = package_id)
    curWarehouse = curPackage.warehouse
    curOrder = Order.objects.get(package = curPackage)
    curProduct = curOrder.product
    curNum = curOrder.product_num
    curStock, created = WarehouseStock.objects.get_or_create(warehouse = curWarehouse, product = curProduct)
    curStock.num_product -= curNum
    print('success to reduce the stock')
    curStock.save()
    
def updatePackageTruckId(package_id):
    curPackage = Package.objects.get(id = package_id)
    curWarehouse = curPackage.warehouse
    curTruckid = curWarehouse.truck_id
    curPackage.truck_id = curTruckid
    curPackage.save()

  
# if __name__ == "__main__":
    # changeAddress(1, 6, 7)
    # changeStatus(1, 'packing')
    # printDescribe(1)
    # print(queue_processing[0])
    