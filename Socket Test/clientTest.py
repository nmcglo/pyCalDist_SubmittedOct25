import socket

TCP_IP = '54.175.196.0' #Server address
TCP_PORT = 5005
BUFFER_SIZE = 1024



quit = False
while not quit:
	welcomeMessage = '1. Send Message\n'
	in1 = input('What would you like to do?' + '\n' + welcomeMessage)
	if in1 == 1:
		MESSAGE = raw_input('Enter Message:\n')
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((TCP_IP, TCP_PORT))
		s.send(MESSAGE)
		data = s.recv(BUFFER_SIZE)
		s.close()

		print 'received data:', data

