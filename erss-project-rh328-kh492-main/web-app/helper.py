import world_amazon_pb2 
import amazon_ups_pb2 

from google.protobuf.internal.encoder import _VarintBytes, _EncodeVarint
from google.protobuf.internal.decoder import _DecodeVarint
from google.protobuf.internal.decoder import _DecodeVarint32
# create new world
def createAConnect(aconnect, whs):
    aconnect.isAmazon = True
    # aconnect.worldid = None
        
    for wh_info in whs:
        wh = aconnect.initwh.add()
        wh.id = wh_info.id
        wh.x = wh_info.address_x
        wh.y = wh_info.address_y
    
    return 



# def sendMsg(msg, world_soc):
#     str1 = "---------------------start send msg: \n "
#     print(str1,msg)
#     msg_str = msg.SerializeToString()
#     _EncodeVarint(world_soc.send, len(msg_str), None)
#     world_soc.send(msg_str)
#     return

def parseNum(socket):
    bytes = socket.recv(1024)
    (msg_length, bytes_length) = _DecodeVarint32(bytes, 0)
    
    return bytes[bytes_length:]


