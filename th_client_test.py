__author__ = 'plaggm'

import socket
import pickle
import jsonpickle
import sys
import asyncio
from algHelper import Message
try:
    from socket import socketpair
except ImportError:
    from asyncio.windows_utils import socketpair


import model
import datetime
from model import CalEvent

from EventTypeEnum import EventType
class tester(object):
    x = 3
    y = "More Data Sent!!!!"
    z = {"A":"Element is B"}
if __name__ == '__main__':
    ins = input()
    while(ins is ""):
        print("Sending create event")
        if(len(sys.argv) > 1):
            otherIP = sys.argv[1]
        else:
            otherIP = "192.168.168.175"
        port = 8888
        #data = " ".join(sys.argv[2:])
        BUFFER_SIZE = 2048

        testStart = datetime.datetime(2015,1,12)
        testEnd = datetime.datetime(2016,1,12)
        testEvt = CalEvent("Event Demo",testStart, testEnd,uid="TESTID")
        testStr = testEvt.toJSON()

        testMessage = Message(0,1,[1,2,3,4],["insert"])


        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((otherIP, port))
        #s.send("Hello".encode())
        td = tester()
        dat = pickle.dumps(testMessage,protocol=pickle.HIGHEST_PROTOCOL)
        dat = jsonpickle.encode(testMessage)

        s.send(dat.encode())
        s.close()

        #s.send("More DATA!!!!!!")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((otherIP, port))
        ins = input()
        print("removing that event")
        testMessage = Message(EventType.delete,testStr,1,[[1,2,3],[1,1,1]],[["insert","X"]])
        dat = jsonpickle.encode(testMessage)
        s.send(dat.encode())


        s.close()
        print("sent del message")
        ins = input()
