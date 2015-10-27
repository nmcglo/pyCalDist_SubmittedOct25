__author__ = 'Neil'
import socketserver
import socket
import pickle
class testData(object):
    x = 3
    y = "This is some stuff"
    z = {"A":"B"}
class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip()
        s = self.request[1]
        print("{} wrote:".format(self.client_address[0]))
        if "abc" not in str(data):
            print(data)
            td = testData()
            pd = pickle.dumps(td,protocol=pickle.HIGHEST_PROTOCOL)
            s.sendto(pd,self.client_address)
        else:
            s.sendto(data.upper(), self.client_address)

if __name__ == "__main__":
    selfIP = socket.gethostname()
    PORT = 9999
    server = socketserver.UDPServer((selfIP, PORT), MyUDPHandler)
    server.serve_forever()