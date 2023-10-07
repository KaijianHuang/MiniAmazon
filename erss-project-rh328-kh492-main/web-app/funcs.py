# import os
# import world_amazon_pb2 
# import amazon_ups_pb2 
# from django.db.models import Q
# import threading
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amazon.settings")
# if django.VERSION >= (1, 7):
#     django.setup()

# from users.models import *

# import psycopg2
# import time
# conn = psycopg2.connect(
#         database="iptqlldc",
#         user="iptqlldc",
#         password="DpY4OG8EVjDBQsLLQidrUdCPo6lNBybm",
#         host="lallah.db.elephantsql.com",
#         port="5432"
#     )
# cursor = conn.cursor()
# idnum = 90
# query = f"""
#     SELECT * FROM public.users_package
#     WHERE public.users_package.id = {idnum};
# """
# cursor.execute(query)
# x = cursor.fetchone()
# print(x)
# cursor.close()


# def connect_webapp(address):
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.bind(address)
#     # Listen for incoming connections and wait for a connection
#     sock.listen(10)
#     webapp_socket, _ = sock.accept()
#     sock.close()
#     return webapp_socket

# def check_status():
#     cur = conn.cursor()
#     while True:
#         cur.execute("SELECT id, status FROM public.users_package WHERE status = 'processing'")
#         rows = cur.fetchall()

#         for row in rows:
#             package_id, status = row
#             # Call the function to perform the operation on the package with the specified ID
#             perform_operation(package_id)
#         # Wait for a certain period of time before checking the package status again
#         # You can adjust the sleep interval based on your needs
#         time.sleep(10)
# def perform_operation(package_id):
#     #TODO: 1. change pack_id status(processing -> processed), 
#     #2. judge if pack_id 
#     #send ApurchaseMOre(warehouse, Aproduct(product_id, desc, count)) command
#     #3. 
#     print(package_id)

# query = ""
# query += f"""
#     UPDATE public.users_warehouse
#     SET total = total + 1
#     WHERE id = 1;
# """
# def updateInventoryArrived(whnum, product_id, count):
#     curWarehouse = Warehouse.objects.get(id = whnum)
#     curProduct = Product.objects.get(id = product_id)
#     curWarehouseStock = None
#     curWarehouseStock, created = WarehouseStock.objects.get_or_create(warehouse = curWarehouse, product = curProduct)
#     curWarehouseStock.num_product += count
#     curWarehouseStock.save()


# def packedInventory(package_id):
#     try:
#         print(f'Packed: start change inventory of warehouse')
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


# def checkWarehouseStock(product_id, warehouse_id):
#     curProduct = Product.objects.get(id = product_id)
#     curWarehouse = Warehouse.objects.get(id = warehouse_id)
#     curWHS = WarehouseStock.objects.filter(warehouse = curWarehouse, product = curProduct)
#     if curWHS.exists():
#         print('exist')
#     else:
#         print("create")

# def checkInventory(package_id):
#     """
#         if current package product_num > the warehouse stock of the product:
#             return False
#         else:
#             return True
#     """
#     curPackage = Package.objects.get(id = package_id)
#     curOrder = Order.objects.get(package = curPackage)
#     curProduct = curOrder.product
#     curDes = curProduct.description
#     curNum = curOrder.product_num
#     curWarehouse = curPackage.warehouse
#     curWarehouseStock, created = WarehouseStock.objects.get_or_create(warehouse = curWarehouse, product = curProduct)
#     curProductStock = curWarehouseStock.num_product

#     """
#     TODO: check inventory num_product and product_num
#     """
#     print("product_num is "+str(curNum))
#     print("num_product is "+ str(curProductStock))
#     if curNum > curProductStock:
#         return False
#     return True

# def getWarehouseid(package_id):
#     """
#         return Warehouseid
#     """

# def checkPackContainUpsId(package_id):
#     curPackage = Package.objects.get(id=package_id)
#     curUser = curPackage.customer
#     try:
#         user_account = UserAccount.objects.get(user=curUser)
#     except UserAccount.DoesNotExist:
#         # UserAccount does not exist, create a new one
#         user_account = UserAccount.objects.create(user=curUser)
#     ups_userid = user_account.ups_userid
#     print(ups_userid)
#     if ups_userid < 0:
#         return -1
#     else:
#         return ups_userid

# def updateInventoryArrived(whnum, product_id, count):
#     curWarehouse = Warehouse.objects.get(id = whnum)
#     curProduct = Product.objects.get(id = product_id)
#     curWarehouseStock = None
#     curWarehouseStock, created = WarehouseStock.objects.get_or_create(warehouse = curWarehouse, product = curProduct)
#     curWarehouseStock.num_product += count
#     curWarehouseStock.save()
    

# # function in handler.py
# def sendPurchaseMore(sim_socket, package_id):
#     command = world.ACommands()
#     buy_object = command.buy.add()
#     new_seq = addSeqnum()
#     buy_object.seqnum = new_seq

#     # Work for TODO
#     curPackage = Package.objects.get(id = package_id)
#     curWarehouse = curPackage.warehouse
#     whnum = curWarehouse.id
#     curOrder = Order.objects.get(package = curPackage)
#     curProduct = curOrder.product
#     product_id = curProduct.id
#     product_description = curProduct.description
#     product_count = curOrder.product_num
#     # Finish work for TODO

#     # TODO: whnum 获取该package的wh id
#     buy_object.whnum = whnum
#     new_thing = buy_object.things.add()
#     # TODO: product_id 这个package里的商品的id
#     new_thing.id = product_id
#     # TODO: product_description 这个package里的商品的description
#     new_thing.description = product_description
#     # TODO: product_count 这个package里的商品的count
#     new_thing.count = product_count
#     sendMsgTillAck(sim_socket, command, new_seq)


# #function in handler.py
# def worldToPack(sim_socket, package_id):
#     new_seq = addSeqnum()
    
#     command = world.ACommands()

#     # Work for TODO
#     curPackage = Package.objects.get(id = package_id)
#     curWarehouse = curPackage.warehouse
#     whnum = curWarehouse.id
#     curOrder = Order.objects.get(package = curPackage)
#     curProduct = curOrder.product
#     product_id = curProduct.id
#     product_description = curProduct.description
#     product_count = curOrder.product_num
#     # Finish work for TODO

#     pack_object = command.topack.add()
#     pack_object.seqnum = new_seq
#     pack_object.shipid = package_id
#     pack_object.whnum = whnum
    
#     thing = pack_object.things.add()
#     thing.id = product_id
#     thing.description = product_description
#     thing.count = product_count
    
    
#     sendMsgTillAck(sim_socket, command, new_seq)
#     return

# def placeOrderToUps(ups_socket, package_id):
#     new_seq = addSeqnum()
#     message = ups.AUMessages()
#     place_order = message.order.add()
#     place_order.shipsid = package_id
#     place_order.seqnum = new_seq
    

#     # Work for TODO
#     curPackage = Package.objects.get(id = package_id)
#     curWarehouse = curPackage.warehouse
#     whnum = curWarehouse.id
#     curOrder = Order.objects.get(package = curPackage)
#     curProduct = curOrder.product
#     product_id = curProduct.id
#     product_description = curProduct.description
#     product_count = curOrder.product_num
#     address_x = curPackage.address_x
#     address_y = curPackage.address_y
#     # Finish work for TODO


#     userId = checkPackContainUpsId(package_id)
#     if userId != -1:
#         place_order.userid = userId
    
#     order = place_order.order.add()
#     order.id = package_id
#     order. description = product_description
#     order.count = product_count
#     order.x = address_x
#     order.y = address_y
#     order.whid = whnum
    
#     sendMsgTillAck(ups_socket, message, new_seq)
#     return

# def getPackedNum(package_id):
#     '''
#         返回package中状态为packed的order的数量
#     '''
#     curPackage = Package.objects.get(id = package_id)
#     curWarehouse=Warehouse.objects.get(id = curPackage.warehouse.id)
#     try:
#         stockpackages = Package.objects.get(warehouse = curWarehouse, status = "packed")
#         print(len(stockpackages))
#         return len(stockpackages)
#     except Package.DoesNotExist:
#         # UserAccount does not exist, create a new one
#         print(0)
#         return 0

# def updateInventoryPacked(package_id):
#     curPackage = Package.objects.get(id = package_id)
#     curWarehouse = curPackage.warehouse
#     curOrder = Order.objects.get(package = curPackage)
#     curProduct = curOrder.product
#     curNum = curOrder.product_num
#     curStock, created = WarehouseStock.objects.get_or_create(warehouse = curWarehouse, product = curProduct)
#     curStock.num_product -= curNum
#     curStock.save()
    
# def updatePackageTruckId(package_id):
#     curPackage = Package.objects.get(id = package_id)
#     curWarehouse = curPackage.warehouse
#     curTruckid = curWarehouse.truck_id
#     curPackage.truck_id = curTruckid
#     curPackage.save()

# def updateTruckForWh(truck_id, wh_id):
#     curWarehouse = Warehouse.objects.get(id = wh_id)
#     curWarehouse.truck_id = truck_id
#     curWarehouse.save()


# if __name__ == "__main__":
    # updateInventory(1)
    # checkPackContainUpsId(1)
    # updateInventoryArrived(11, 1, 30)
    # getPackedNum(1)
    # updateInventoryPacked(1)
    # updatePackageTruckId(1)
    # updateTruckForWh(1,1)
    # packages = Package.objects.all()
    # for pack in packages:
    #     curorder = Order.objects.get()
