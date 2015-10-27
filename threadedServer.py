import os,sys
import asyncio
import logging
import shlex, subprocess
import threading
from controller import process
import pickle
import jsonpickle
import json
import numpy
import controller
import model
from UserRankEnum import UserRank
import algHelper
from th_client_test import tester
try:
    from socket import socketpair
except ImportError:
    from asyncio.windows_utils import socketpair

from multiprocessing.pool import ThreadPool, Pool
from multiprocessing import Queue
import socketserver
import socket
import EventTypeEnum

returnVals = []
remoteServers = ["127.0.0.1:80000"]
openSockets = []
# global outboundMessageQueue
# outboundMessageQueue = asyncio.Queue()
outboundMessageQueue = algHelper.outQueue
global inboundMessageQueue
inboundMessageQueue = asyncio.Queue()
outMessageQueue = Queue()
inMessageQueue = Queue()
processQueue = asyncio.Queue()


class ThreadWorker():
    '''
    The basic idea is given a function create an object.
    The object can then run the function in a thread.
    It provides a wrapper to start it,check its status,and get data out the function.
    '''
    def __init__(self,func):
        self.thread = None
        self.data = None
        self.func = self.save_data(func)

    def save_data(self,func):
        '''modify function to save its returned data'''
        def new_func(*args, **kwargs):
            self.data=func(*args, **kwargs)

        return new_func

    def start(self,params):
        self.data = None
        if self.thread is not None:
            if self.thread.isAlive():
                return 'running' #could raise exception here

        #unless thread exists and is alive start or restart it
        self.thread = threading.Thread(target=self.func,args=params)
        self.thread.start()
        return 'started'

    def status(self):
        if self.thread is None:
            return 0#'not_started'
        else:
            if self.thread.isAlive():
                return 1#'running'
            else:
                return 2#'finished'

    def get_results(self):
        if self.thread is None:
            return 'not_started' #could return exception
        else:
            if self.thread.isAlive():
                return 'running'
            else:
                return self.data


# class testData(object):
#     x = 3
#     y = "This is some stuff"
#     z = {"A":"B"}


class ProcTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        inMessageQueue.put_nowait(pickle.dump(self.rfile))



def testThread(**args):
    pass


def hanlde_user_input(theProc):
    print("staring process")

    result = theProc.prompt()
    if result and len(result) > 0:
        map(lambda msg: outboundMessageQueue.put_nowait(msg), result)


### "Client" protocol - Code that manages sending of data to the remote servers
class WuuClientProtocol(asyncio.Protocol):
    def __init__(self, messageInJSON, loop):
        self.message = messageInJSON
        self.loop = loop
    def connection_made(self, transport):
        transport.write(self.message.encode())
        ##DEBUG CODER
        print("Data Sent: {!r}".format(self.message))

    def data_received(self, data):
        print("Data was received on WuuClientProtocol. Currently, this is something that shouldn't happen?")

    def connection_lost(self, exc):
        print("Connection was closed.")


### "Client" Streams Manager - alternate way to send data using asyncio


@asyncio.coroutine
def send_message(loop):
    while True:
        while outboundMessageQueue.qsize() > 0:
            print("sending a message")
            #HOSTID, IP ADDRESS, PORT



            message_dests = getDests()
            #message dests should now be a dictionary that has the host IP address as the key, and a list as the data
            if outboundMessageQueue.qsize() > 0 :
                msg = outboundMessageQueue.get_nowait()
                # print("MESSAGE TO " ,msg.destID)
                # print("EEEEVO:", message_dests)
                message_dests[str(msg.destID)][1].append(msg)
                # print(msg)
            for dest in message_dests:
                # print("INDIVID DST:", dest)
                if len(message_dests[str(dest)]) is 0:
                    pass
                else:
                    # print(str(message_dests[str(dest)][0]))

                    #reader,writer = yield  from asyncio.open_connection(deststr,                        loop=loop)

                    #

                    # print("DEESSST TEST", dest)
                    for mess in message_dests[str(dest)][1]:
                        # print("MEEEEESSSS:", mess)
                        #mess = pickle.dumps(mess)

                        x = mess.toJSON()
                        # print(x)
                        y = algHelper.messageFromJSON(x)
                        # print("y is: ", y)
                        yield from threadWriter(message_dests[str(dest)][0],x,loop)
                        #writer.write(jsonpickle.encode(msg).encode())



        # print("send message ran.")
        yield from asyncio.sleep(1)

@asyncio.coroutine
def threadWriter(host, message,Loop):


    try:
        reader,writer = yield from asyncio.open_connection(host=host[0],port=int(host[1]),loop=Loop)
        # print("Sending messsssssage:", host[0], host[1])
        writer.write(message.encode())
        yield from writer.drain()
        writer.close()
        print("Message Send Complete")
    except:
        print("Lost connection to a process")
    #writer.write(message.toJSON().encode())
    #pickle.dump(message,writer,pickle.HIGHEST_PROTOCOL)


    #writer.close()
    return
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        print('Failed to create socket')

    s.connect((host[0],int(host[1])))
    s.send(jsonpickle.encode(message).encode())

    #print("HOST IS DOWN")

    s.close()


def getDests():
    hosts = numpy.loadtxt("hosts.info",dtype='S20', delimiter=",")

    ##OK, how do we know what UUID goes to what server?
    #I'm going to assume that the UUID in a message contains the IP:PORT in a tuple for this.
    message_dests = {}
    for host in hosts:
        # print("Host is ", host.astype(str))
        message_dests[host[0].astype(str)] = ((
                                                  str(host[1].astype(str)).strip(),
                                                  str(host[2].astype(str)).strip()),[])
    return message_dests




#Server streams function
@asyncio.coroutine
def handle_message(reader,writer):
        # print("COG RCV MESSAGE")
        data = yield from reader.read()
        message = data.decode()
        addr = writer.get_extra_info('peername')

        decoded = algHelper.messageFromJSON(message)
        x = decoded
        # print("Received %r from %r" % (decoded, addr))
        #x = pickle.loads(data)
        #x = pickle.decode(message)


        #print("JSON DE-PICKLED IS %s", x)
        #writer.close()
        inboundMessageQueue.put_nowait(decoded)
        theProc = yield from processQueue.get()
        x =  theProc.recvMsg(x)
        y = yield from testCallback()
        processQueue.put_nowait(theProc)
        print("*****Completed message receive.*****")

@asyncio.coroutine
def print_hello():
    print("hello!!")

@asyncio.coroutine
def testCallback():
    print("")
    #q = inboundMessageQueue
    #print("Q SIZE IS ", q.qsize())
    #if(q.qsize() > 0):
    #    print(q.get_nowait())
    #    print("Inside the test callback")






# def testSend():
#     testStart = datetime.datetime(2015,1,12)
#     testEnd = datetime.datetime(2016,1,12)
#     testEvt = CalEvent("Event Demo",testStart, testEnd,uid="TESTID")
#     testStr = testEvt.toJSON()
#     testMessage = Message(EventType.insert,testStr,1,[[1,2,3],[1,1,1]],[["insert","X"]])

@asyncio.coroutine
def userInput():
    while True:
        theproc = processQueue.get_nowait()
        hanlde_user_input(theproc)
        processQueue.put_nowait(theproc)
        print("Press enter")
        yield from asyncio.sleep(1)

def main(procID):
    print("starting system.")
    ext_hosts = numpy.loadtxt("hosts.info",dtype='S20', delimiter=",")
    print("hosts loaded: ", ext_hosts)
    for element  in  ext_hosts:
        for item in element:
            print (item.astype(str))
    #print("testing dests")
    #dests = getDests()
    #print(dests)
    dest = 0
    #deststr = str(dests[str(dest)][0])
    #deststr = deststr.lstrip(' ')
    print("Press enter to begin.")

    theProc = controller.loadProcFromFile()
    if not theProc:
        theProc = process(procID,UserRank.low,len(ext_hosts))
        print("New Process")
    processQueue.put_nowait(theProc)
    loop= asyncio.get_event_loop()
    if os.name == 'nt':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(print_hello())
    future = asyncio.Future()
    loop.create_task(send_message(loop))
    if os.name == 'nt':
        asyncio.async(userInput(), loop=loop)
    else:
        loop.add_reader(sys.stdin, hanlde_user_input, theProc)

    coro = asyncio.start_server(handle_message,host=None, port=8887, loop=loop)
    #oop.call_soon(print_hello)
    #loop.run_until_complete(print_hello)
    server = loop.run_until_complete(coro)


    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.close()
    loop.run_until_complete(server.wait_closed())


    


x = 3
##CLI TESTStheProc = process(1,UserRank.low,2)
if __name__ == '__main__':

    procID = 0
    if len(sys.argv) > 1:
        procID = int(sys.argv[1])
    main(procID)

