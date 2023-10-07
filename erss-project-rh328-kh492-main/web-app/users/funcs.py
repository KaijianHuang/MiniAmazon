from socket import *
from .models import *
import math
serverName = 'backend'
packagePort = 8888
usernamePort = 9999

def notify_backend(packageID):
    try:
        #serverName = gethostname() 
        backend_socket = socket(AF_INET,SOCK_STREAM)
        backend_socket.connect((serverName,packagePort))
        msg = str(packageID)+'\n'
        backend_socket.send(msg.encode('utf-8'))
        response =  backend_socket.recv(256)
        response = response.decode()
        components = response.split(' ')
        if components[0] == 'received' and components[1]==str(packageID):
            return True
        else:
            print('backend says: '+response)
            return False
    except ConnectionRefusedError:
        return False

def check_username(ups_username):
    try:
        #serverName = gethostname()
        backend_socket = socket(AF_INET,SOCK_STREAM)
        backend_socket.connect((serverName,usernamePort))
        msg = str(ups_username)+'\n'
        backend_socket.send(msg.encode('utf-8'))
        response =  backend_socket.recv(256)
        response = response.decode()
        components = response.split(' ')
        if components[0] == 'received' and components[1]==str(ups_username):
            return True
        else:
            print('backend says: '+response)
            return False
    except ConnectionRefusedError:
        return False

def get_closest_wh(address_x, address_y):
    min_dist = float('inf')
    whID = 1
    all_whs = Warehouse.objects.all()
    for wh in all_whs:
        wh_x = wh.address_x
        wh_y = wh.address_y
        dist = math.sqrt(math.pow(address_x-wh_x,2)+math.pow(address_y-wh_y,2))
        if dist<min_dist:
            min_dist = dist
            whID = wh.id
    return whID