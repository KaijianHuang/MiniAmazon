import threading
import world_amazon_pb2 as world
import amazon_ups_pb2 as ups
import front_end_pb2 as front
from helper import *
from database import *
from funcs import *
from concurrent.futures import ThreadPoolExecutor
import time

from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint
from google.protobuf.internal.decoder import _DecodeVarint32

SEQNUM = 1
ACKS = set()
SEQNUM_LOCK = threading.Lock()
ACK_LOCK = threading.Lock()

CALL_TRUCK_NUM = 2
TRUCK_CALLED = False
TRUCK_LOCK = threading.Lock()

SOCKET_LOCK = threading.Lock()
DB_LOCK = threading.Lock()

def sendAckToWorld(sim_socket, ack):
    print("send ack to world")
    command = world.ACommands()
    command.acks.append(ack)
    sendMsg(command, sim_socket)
    return
    
def sendAckToUps(ups_socket, ack):
    print("send ack to ups")
    message = ups.AUMessages()
    message.acks.append(ack)
    sendMsg(message, ups_socket)
    return

def sendMsgTillAck(socket, msg, seq_num):
    print('start sending msg')
    i = 0
    while True:
        print(i)
        i += 1
        sendMsg(msg, socket)
        time.sleep(1)
        if seq_num in ACKS:
            print('seq_num in ACKS: ', seq_num)
            break
    return

def addSeqnum():
    SEQNUM_LOCK.acquire()
    global SEQNUM
    SEQNUM += 1
    ans = SEQNUM
    SEQNUM_LOCK.release()
    return ans

def addAcks(ack):
    ACK_LOCK.acquire()
    global ACKS
    ACKS.add(ack)
    print(ACKS)
    ACK_LOCK.release()
    return

def handleWorldResponses(sim_socket, ups_socket):
    # pool = ThreadPoolExecutor(100)
    while True:
        response = recvMsg(world.AResponses, sim_socket)
        print("---Msg from world---")
        print(response)
        for err in response.error:
            sendAckToWorld(sim_socket, err.seqnum)
            print("---World Error---")
            print("Origin seqnum:", err.originseqnum)
            print("Error message:", err.err)
            
        for ack in response.acks:
            print("receive ack from world")
            addAcks(ack)
            
        for arrived_purchase in response.arrived:
            print("---Purchase Arrived---")
            handleArrived(sim_socket, arrived_purchase)
            
        for packed in response.ready:
            print("---Packed Received---")
            handlePacked(sim_socket, ups_socket, packed)
        
        loaded_shipid = []
        for loaded_package in response.loaded:
            print("---Packages Loaded---")
            sendAckToWorld(sim_socket, loaded_package.seqnum)
            loaded_shipid.append(loaded_package.shipid)

        if len(loaded_shipid) > 0:
            handleLoaded(ups_socket, loaded_shipid)
        
        if response.finished == True:
            print("---Close All Connections---")
            sim_socket.close()
            ups_socket.close()
            break
            
    return
    
def handleUpsMessages(sim_socket, ups_socket):
    # pool = ThreadPoolExecutor(100)
    while True:
        message = recvMsg(ups.UAMessages, ups_socket)
        print("-----msg from ups-")
        print(message)
        for err in message.error:
            sendAckToUps(ups_socket, err.seqnum)
            print("---Ups Error---")
            print("Origin seqnum:", err.originseqnum)
            print("Error message:", err.err)

        for ack in message.acks:
            print("recv ack from ups")
            addAcks(ack)

        for truck_arrived in message.truckArrived:
            print("---Truck Arrived---")
            handleTruckArrived(sim_socket, ups_socket, truck_arrived)           
        for update_status in message.updatePackageStatus:
            print("---Update Package Status---")
            handleUpdateStatus(ups_socket, update_status)
            print('returned from handleUpdateStatus')
        for update_address in message.updatePackageAddress:
            print("---Update Package Address---")
            handleUpdateAddress(ups_socket, update_address)
            
    return

def handleFrontCommands(sim_socket, ups_socket, front_socket):
    # pool = ThreadPoolExecutor(100)
    while True:
        command = recvMsg(front.FCommands, front_socket)
        print("---msg from front end---")
        print(command)
        if command.HasField('buy'):
            print("---Order Received---")
            upsPlaceOrder(ups_socket, command.buy.packageid)
            handleBuy(sim_socket, command.buy.packageid)

            # handlePlaceOrder(sim_socket, ups_socket, front_socket, command.buy.packageid)
        if command.HasField('associate'):
        
            print("---Associate Request Received---")
            associateUpsId(ups_socket, command.associate.packageid, command.associate.userid)
            # handleAssociate(ups_socket, front_socket, command.associate)

def handlePlaceOrder(sim_socket, ups_socket, front_socket, package_id):
    flag = upsPlaceOrder(ups_socket, package_id)
    response = front.BResponses()

    if flag:
        handleBuy(sim_socket, package_id)
        response.isValid = True
    else:
        response.isValid = False
    
    sendMsg(response, front_socket)

def handleAssociate(ups_socket, front_socket, associate):
    flag = associateUpsId(ups_socket, associate.packageid, associate.userid)
    response = front.BResponses()

    if flag:
        response.isValid = True
    else:
        response.isValid = False

    sendMsg(response, front_socket)

def handleArrived(sim_socket, arrived_purchase):
    sendAckToWorld(sim_socket, arrived_purchase.seqnum)
    print("ack number ", arrived_purchase.seqnum)
    for i in arrived_purchase.things:
        thing = i

    updateInventoryArrived(arrived_purchase.whnum, thing.id, thing.count)
    
    DB_LOCK.acquire()
    curWh = Warehouse.objects.get(id = arrived_purchase.whnum)
    packages = Package.objects.filter(status = "PROCESSED", warehouse = curWh)  
    DB_LOCK.release()
    for package in packages:
        package_id = package.id
        if checkInventory(package_id):
            worldToPack(sim_socket, package_id)
    return

# packed
def handlePacked(sim_socket, ups_socket, packed):
    sendAckToWorld(sim_socket, packed.seqnum)
    changeStatus(packed.shipid, "PACKED")
    
    if getPackedNum(packed.shipid) >= CALL_TRUCK_NUM and TRUCK_CALLED == False:
        changeTruckCalled()
        upsCallTruck(ups_socket, packed)
    
    return   
    
def changeTruckCalled():
    TRUCK_LOCK.acquire()
    global TRUCK_CALLED
    TRUCK_CALLED = not TRUCK_CALLED
    TRUCK_LOCK.release()

def handleLoaded(ups_socket, loaded_shipid):
    for shipid in loaded_shipid:

        changeStatus(shipid, "LOADED")
    
        # update package truck id
        updatePackageTruckId(shipid)

    # update truck status to loaded
    upsChangeTruckStatusLoaded(ups_socket, loaded_shipid[0])    
    upsTruckGoDeliver(ups_socket, loaded_shipid[0])
    
def upsChangeTruckStatusLoaded(ups_socket, package_id):
    # send new command
    new_seq = addSeqnum()
    aumessage = ups.AUMessages()
    update_info = aumessage.updateTruckStatus.add()
    update_info.seqnum = new_seq
    update_info.status = "LOADED"
    
    DB_LOCK.acquire()
    curPackage = Package.objects.get(id = package_id)
    DB_LOCK.release()
    curWarehouse = curPackage.warehouse
    
    update_info.truckid = curWarehouse.truck_id
    
    sendMsgTillAck(ups_socket, aumessage, new_seq)
    return

def upsChangeTruckStatusLoading(ups_socket, truck_id):
    # send new command
    new_seq = addSeqnum()
    aumessage = ups.AUMessages()
    update_info = aumessage.updateTruckStatus.add()
    update_info.seqnum = new_seq
    update_info.status = "LOADING"
    
    update_info.truckid = truck_id
    
    # sendMsgTillAck(ups_socket, aumessage, new_seq)
    sendMsg(aumessage, ups_socket)
    return

def upsTruckGoDeliver(ups_socket, package_id):
    # send new command
    new_seq = addSeqnum()
    aumessage = ups.AUMessages()
    truck_go = aumessage.truckGoDeliver.add()
    
    truck_go.seqnum = new_seq
    
    DB_LOCK.acquire()
    curPackage = Package.objects.get(id = package_id)
    curWarehouse = curPackage.warehouse
    truck_go.truckid = curWarehouse.truck_id
    
    all_loaded = Package.objects.filter(warehouse = curWarehouse, status="LOADED")
    DB_LOCK.release()
    for loaded in all_loaded:
        truck_go.shipid.append(loaded.id)
        print(loaded.id)
    
    sendMsgTillAck(ups_socket, aumessage, new_seq)

    # after receive ack, change package status
    for loaded in all_loaded:
        changeStatus(loaded.id, "DELIVERING")
    changeTruckCalled()
    
def sendPurchaseMore(sim_socket, package_id):
    # send new command
    new_seq = addSeqnum()
    command = world.ACommands()
    buy_object = command.buy.add()
    buy_object.seqnum = new_seq

    DB_LOCK.acquire()
    curPackage = Package.objects.get(id = package_id)
    curOrder = Order.objects.get(package = curPackage)
    DB_LOCK.release()

    curWarehouse = curPackage.warehouse
    whnum = curWarehouse.id
    curProduct = curOrder.product
    product_id = curProduct.id
    product_description = curProduct.description
    product_count = curOrder.product_num

    buy_object.whnum = whnum
    new_thing = buy_object.things.add()
    new_thing.id = product_id
    new_thing.description = product_description
    new_thing.count = product_count
    
    sendMsgTillAck(sim_socket, command, new_seq)
    return
    
def handleBuy(sim_socket, package_id):
    # if checkInventory(package_id):
    #     # enough inventory
    #     worldToPack(sim_socket, package_id)
    # else:
        # not enough inventory
        # send purchasemore command to world
    changeStatus(package_id, "PROCESSED")        
    sendPurchaseMore(sim_socket, package_id)

def associateUpsId(ups_socket, package_id, ups_id):
    # new message
    new_seq = addSeqnum()
    message = ups.AUMessages
    associate = message.associateUserId.add()
    associate.userid = str(ups_id)
    associate.shipid = package_id
    associate.seqnum = new_seq
    
    # flag = sendMsgCheckError(ups_socket, message, new_seq)
    sendMsgTillAck(ups_socket, message, new_seq)
    return True

def worldToPack(sim_socket, package_id):
    # change status to packing
    changeStatus(package_id, "PACKING")
    # decrease invenory
    updateInventoryPacked(package_id)
    
    # send new command
    new_seq = addSeqnum()
    command = world.ACommands()

    DB_LOCK.acquire()
    curPackage = Package.objects.get(id = package_id)
    curOrder = Order.objects.get(package = curPackage)
    DB_LOCK.release()

    curWarehouse = curPackage.warehouse
    whnum = curWarehouse.id
    curProduct = curOrder.product
    product_id = curProduct.id
    product_description = curProduct.description
    product_count = curOrder.product_num

    pack_object = command.topack.add()
    pack_object.seqnum = new_seq
    pack_object.shipid = package_id
    pack_object.whnum = whnum
    
    thing = pack_object.things.add()
    thing.id = product_id
    thing.description = product_description
    thing.count = product_count
    print('start send topack: ', command)
    sendMsg(command, sim_socket)
    # sendMsgTillAck(sim_socket, command, new_seq)
    return

def upsCallTruck(ups_socket, packed):
    # send new command
    new_seq = addSeqnum()
    aumessage = ups.AUMessages()
    call_truck = aumessage.callTruck.add()
    
    DB_LOCK.acquire()
    curPackage = Package.objects.get(id = packed.shipid)
    curWarehouse = curPackage.warehouse
    whnum = curWarehouse.id
    call_truck.whnum = whnum
    call_truck.seqnum = new_seq
    
    packages = Package.objects.filter(warehouse = curWarehouse, status="packed")
    DB_LOCK.release()

    for package in packages:
        call_truck.shipid.add(package.id)
    
    sendMsgTillAck(ups_socket, aumessage, new_seq)            
    
    return

'''
    If the order is successfully placed, return true
    else return false
'''
def upsPlaceOrder(ups_socket, package_id):
    # send new message
    new_seq = addSeqnum()
    message = ups.AUMessages()
    place_order = message.order.add()
    place_order.shipid = package_id
    place_order.seqnum = new_seq
    
    DB_LOCK.acquire()
    curPackage = Package.objects.get(id = package_id)
    curWarehouse = curPackage.warehouse
    whnum = curWarehouse.id
    curOrder = Order.objects.get(package = curPackage)
    DB_LOCK.release()
    curProduct = curOrder.product
    product_id = curProduct.id
    product_description = curProduct.description
    product_count = curOrder.product_num
    address_x = curPackage.address_x
    address_y = curPackage.address_y

    if curPackage.ups_id != -1:
        place_order.userid = str(curPackage.ups_id)
    
    # order = place_order.order.add()
    place_order.order.id = product_id
    place_order.order.description = product_description
    place_order.order.count = product_count
    place_order.order.x = address_x
    place_order.order.y = address_y
    place_order.order.whid = whnum
    
    print(message)
    # flag = sendMsgCheckError(ups_socket, message, new_seq)
    # sendMsgTillAck(ups_socket, message, new_seq)
    sendMsg(message, ups_socket)
    return True

def sendMsgCheckError(ups_socket, msg, seqnum):
    while True:
        sendMsg(msg, ups_socket)
        print("start receive")
        uamessage = recvMsg(ups.UAMessages, ups_socket)
        print("Parsed message length:", uamessage.ByteSize())
        print('Print uamessage type:', type(uamessage))
        print("end receive, and print uamessage")
        print(uamessage)
        for err in uamessage.error:
        # if uamessage.HasField("error"):
            print("no err")
            sendAckToUps(ups_socket, err.seqnum)
            return False
            
        # if uamessage.HasField("acks"):
        for ack in uamessage.acks:
            addAcks(ack)
            print(ack)
            if ack == seqnum:
                return True
            
def getPackedNum(package_id):
    DB_LOCK.acquire()
    curPackage = Package.objects.get(id = package_id)
    curWarehouse=Warehouse.objects.get(id = curPackage.warehouse.id)
    DB_LOCK.release()
    try:
        stockpackages = Package.objects.filter(warehouse = curWarehouse, status = "PACKED")
        return len(stockpackages)
    except Package.DoesNotExist:
        return 0

def handleTruckArrived(sim_socket, ups_socket, truck_arrived):
    sendAckToUps(ups_socket, truck_arrived.seqnum)
    
    # update truckid for wh
    truckid = truck_arrived.truckid
    whid = truck_arrived.whid
    time.sleep(1)
    updateTruckForWh(truckid, whid)
    # update truck status to loading
    upsChangeTruckStatusLoading(ups_socket, truckid)
    # start loading
    startLoading(sim_socket, whid, truckid)

    
def handleUpdateStatus(ups_socket, update_status): 
    sendAckToUps(ups_socket, update_status.seqnum)
    changeStatus(update_status.shipid, update_status.status)
    print('in handleUpdateStatus, change status to' + update_status.status)
    return
    
def handleUpdateAddress(ups_socket, update_address):
    sendAckToUps(ups_socket, update_address.seqnum)
    changeAddress(update_address.shipid, update_address.x, update_address.y)
    return

def startLoading(sim_socket, whid, truckid):
    
    DB_LOCK.acquire()
    curWh = Warehouse.objects.get(id = whid)
    packages = Package.objects.filter(warehouse = curWh, status = "PACKED")
    DB_LOCK.release()
    for package in packages:
        changeStatus(package.id, "LOADED")
        command = world.ACommands()       
        # send new command
        new_seq = addSeqnum()
        new_load = command.load.add()
        new_load.whnum = whid
        new_load.truckid = truckid
        new_load.shipid = package.id
        new_load.seqnum = new_seq
        sendMsg(command,sim_socket)    



def updateTruckForWh(truck_id, wh_id):
    DB_LOCK.acquire()
    curWarehouse = Warehouse.objects.get(id = wh_id)
    DB_LOCK.release()
    curWarehouse.truck_id = truck_id
    curWarehouse.save()
    time.sleep(1)

def updateInventoryArrived(whnum, product_id, count):
    DB_LOCK.acquire()
    curWarehouse = Warehouse.objects.get(id = whnum)
    curProduct = Product.objects.get(id = product_id)
    curWarehouseStock = None
    curWarehouseStock, created = WarehouseStock.objects.get_or_create(warehouse = curWarehouse, product = curProduct)
    curWarehouseStock.num_product += count
    curWarehouseStock.save()
    DB_LOCK.release()

def checkInventory(package_id):
    """
        if current package product_num > the warehouse stock of the product:
            return False
        else:
            return True
    """
    DB_LOCK.acquire()
    curPackage = Package.objects.get(id = package_id)
    curOrder = Order.objects.get(package = curPackage)
    curProduct = curOrder.product
    curDes = curProduct.description
    curNum = curOrder.product_num
    curWarehouse = curPackage.warehouse
    curWarehouseStock, created = WarehouseStock.objects.get_or_create(warehouse = curWarehouse, product = curProduct)
    curProductStock = curWarehouseStock.num_product
    DB_LOCK.release()

    """
    TODO: check inventory num_product and product_num
    """
    print("product_num is "+str(curNum))
    print("num_product is "+ str(curProductStock))
    if curNum > curProductStock:
        print("stock not enough")
        return False
    print("enough stock, pack")
    return True



def recvMsg(response_type, socket):
    # SOCKET_LOCK.acquire()
    var_int_buff = []
    while True:
        try:
            buf = socket.recv(1)
            var_int_buff += buf
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            if new_pos != 0:
                break
        except IndexError as ex:
            continue

    message = socket.recv(msg_len)

    # var_int_buff = parseNum(socket)
    response = response_type()
    response.ParseFromString(message)
    # SOCKET_LOCK.release()
    return response

def sendMsg(msg, socket):
    # SOCKET_LOCK.acquire()
    serialized_msg = msg.SerializeToString()
    size = msg.ByteSize()
    socket.sendall(_VarintBytes(size) + serialized_msg)
    print("---------send msg---------------------\n", msg)
    # SOCKET_LOCK.release()

def recvUAMsg(socket):
    # var_int_buff = []
    # while True:
    #     buf = socket.recv(1)
    #     var_int_buff += buf
    #     msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
    #     if new_pos != 0:
    #         break
    # var_int_buff = socket.recv(msg_len)

    var_int_buff = parseNum(socket)
    print("print varbuff")
    print(var_int_buff)
    print('\n')
    response = ups.UAMessages()
    response.ParseFromString(var_int_buff)
    print("start printing response")
    print("Parsed message length:", response.ByteSize())
    print('Print uamessage type:', type(response))
    print(response)
    return response


    # data = b''
    # while True:
    #     data += socket.recv(1)        
    #     try:
    #         size = _DecodeVarint(data, 0)[0]
    #         break
    #     except IndexError:
    #         pass
    # data = socket.recv(size)
    # print(data)

    # response = amazon_ups_pb2.UAMessages()
    # response.ParseFromString(data)
    # return response