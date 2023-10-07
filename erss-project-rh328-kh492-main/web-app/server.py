import os
import psycopg2
import socket
import urllib.parse as up # For Remote DataBase
import time
import smtplib
import threading
import django

import world_amazon_pb2 as world
import amazon_ups_pb2 as ups


from django.db.models import Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amazon.settings")


if django.VERSION >= (1, 7):
    django.setup()

from users.models import *
from helper import *
from handler import *

# WORLD_ADDRESS = "vcm-32315.vm.duke.edu"

WORLD_ADDRESS = "LAPTOP-MV802FV7"
# change vm number
# UPS_ADDRESS = "vcm-32315.vm.duke.edu"
UPS_ADDRESS = "LAPTOP-MV802FV7"

FRONT_ADDRESS = "KaijianuangsMBP.lan"

def connectToSimulator():
    sim_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            sim_socket.connect((WORLD_ADDRESS, 23456))
        except Exception:
            print("Faild to connect to world simulator")
            continue
        else:
            break
    return sim_socket

def connectToWorld(sim_socket):
    AConnect = world.AConnect()
    
    whs = Warehouse.objects.all()
    createAConnect(AConnect, whs)

    while True:
        sendMsg(AConnect, sim_socket)
        AConnected = recvMsg(world.AConnected, sim_socket)
        if AConnected.result == 'connected!':
            print("Connect to world successfully!!")
            world_id = AConnected.worldid
            return world_id

def connectToFront():
    front_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("1")

    front_socket.bind((FRONT_ADDRESS, 45678))
    print("2")

    front_socket.listen(10)
    print("3")

    # print(front_socket)

    my_socket, _ = front_socket.accept()
    print('1')
    front_socket.close()

    return my_socket

            
def connectToUps(world_id):

    ups_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ups_socket.connect((UPS_ADDRESS, 34567))   
    AUConnect = ups.AUConnect()
    
    AUConnect.worldid = world_id
    while True:
        sendMsg(AUConnect, ups_socket)
        UAConnected = recvMsg(ups.UAConnected, ups_socket)
        print("send auconnect to ups")

        if UAConnected.result == 'connected!':
            print("Connect to UPS successfully!!")
            return ups_socket

        
def disconnect(sim_socket):
    command = world.ACommands()
    command.disconnect = True
    sendMsg(command, sim_socket)
    return
    
# def serverAssociateUpsId(package_id, ups_id):    
#     flag = associateUpsId(UPS_SOCKET, package_id, ups_id)
#     return flag

# def serverPlaceOrderToUps(package_id):
#     flag = placeOrderToUps(UPS_SOCKET, package_id)
#     return flag

# def serverHandleBuy(package_id):
#     handleBuy(SIM_SOCKET, package_id)

def buyTest(sim_socket):
    command = world.ACommands()
    buy_object = command.buy.add()
    buy_object.whnum = 2
    new_thing = buy_object.things.add()
    new_thing.id = 1
    new_thing.description = "Storm Clouds Rolling In"
    new_thing.count = 5
    buy_object.seqnum = 1
    # print(command)
    sendMsg(command, sim_socket)

# def recvAPacked(sim_socket):
#     response = recvMsg(world.AResponses, sim_socket)
#     print(response)
    
def packTest(sim_socket):
    command = world.ACommands()
    pack = command.topack.add()
    pack.whnum = 6
    pack.shipid = 2
    pack.seqnum = 90
    thing = pack.things.add()
    thing.id = 1
    thing.description = "tired"
    thing.count = 5
    
    sendMsg(command, sim_socket)
    
def testToPack(sim_socket):
    command = world.ACommands()
    topack = command.topack.add()
    topack.whnum = 2
    topack.shipid = 100
    topack.seqnum = 4
    thing = topack.things.add()
    thing.id = 1
    thing.description = "Storm Clouds Rolling In"
    thing.count = 2
    sendMsg(command, sim_socket)

def testCallTruck(ups_socket):
    message = ups.AUMessages()
    call_truck = message.callTruck.add()
    call_truck.whnum = 2
    call_truck.shipid.append(100)
    call_truck.seqnum = 3
    sendMsg(message, ups_socket)

def testLoad(sim_socket):
    command = world.ACommands()
    load = command.APutOnTruck.add()
    load.whnum = 2
    load.truckid = 1
    load.shipid = 100
    load.seqnum = 4



if __name__ == "__main__":    
    FRONT_SOCKET = connectToFront()

    # socket connect to world simulator
    SIM_SOCKET = connectToSimulator() 

    # create new world and get world id
    world_id = connectToWorld(SIM_SOCKET)
    print(world_id)
    # socket connect to ups
    UPS_SOCKET = connectToUps(world_id) 


    world_thread = threading.Thread(target=handleWorldResponses, args=(SIM_SOCKET, UPS_SOCKET))
    ups_thread = threading.Thread(target=handleUpsMessages, args=(SIM_SOCKET, UPS_SOCKET))
    front_thread = threading.Thread(target=handleFrontCommands, args=(SIM_SOCKET, UPS_SOCKET, FRONT_SOCKET))

    world_thread.start()
    ups_thread.start()
    front_thread.start()
    
    #TODO: build thread to listen to placeorder and ups_id
    # package_thread = threading.Thread(target= , args=(SIM_SOCKET, UPS_SOCKET))
    # upsid_thread = threading.Thread(target = , args = (SIM_SOCKET, UPS_SOCKET))
    # buyTest(sim_socket)
    # response = recvMsg(world.AResponses, sim_socket)
    # print(response)
    # response = recvMsg(world.AResponses, sim_socket)
    # print(response)
    
    # packTest(sim_socket)
    # response = recvMsg(world.AResponses, sim_socket)
    # print(response)
    # response = recvMsg(world.AResponses, sim_socket)
    # print(response)
    
    # whs = Warehouse.objects.all()
    # print(len(whs))

    # buyTest(SIM_SOCKET)
    # response = recvMsg(world.AResponses, SIM_SOCKET)
    # print(response)

    # testToPack(SIM_SOCKET)
    # response = recvMsg(world.AResponses, SIM_SOCKET)
    # print(response)
    # response = recvMsg(world.AResponses, SIM_SOCKET)
    # print(response)

    # testCallTruck(UPS_SOCKET)
    # response = recvMsg(ups.UAMessages, UPS_SOCKET)
    # print(response)
    # response = recvMsg(ups.UAMessages, UPS_SOCKET)
    # print(response)


# socket connect to world simulator
# SIM_SOCKET = connectToSimulator() 
# # create new world and get world id
# world_id = connectToWorld(SIM_SOCKET)
# # socket connect to ups
# UPS_SOCKET = connectToUps(world_id) 

# run()

