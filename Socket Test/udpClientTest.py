__author__ = 'Neil'
import socket
import sys
import pickle
from udpServerTest import testData


otherIP = sys.argv[1]
PORT = 8888
data = " ".join(sys.argv[2:])

# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().
sock.sendto(bytes("abc\n","utf-8"),(otherIP,PORT))
rec = str(sock.recv(1024),"utf-8")
if "ABC" in rec:
    sock.sendto(bytes(data + "\n", "utf-8"), (otherIP, PORT))
    #received = str(sock.recv(1024), "utf-8")

    #print("Sent:     {}".format(data))
    #print("Received: {}".format(received))

    bindat = sock.recv(PORT)
    unpickle = pickle.loads(bindat,encoding="utf-8")
    print (unpickle.x)
    print (unpickle.y)
    print (unpickle.z)

