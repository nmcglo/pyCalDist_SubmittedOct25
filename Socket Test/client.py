import socket

BUFFER_SIZE = 1024


def clientSendMessage(otherIP, otherPort, data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((otherIP, otherPort))
    s.send(data)



	if in1 == 1:
		MESSAGE = raw_input('Enter Message:\n')
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		data = s.recv(BUFFER_SIZE)
		s.close()

		print 'received data:', data

