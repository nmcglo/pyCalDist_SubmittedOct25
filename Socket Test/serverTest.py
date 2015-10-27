import socket


TCP_IP = socket.gethostname() #Server IP
TCP_PORT = 5005
BUFFER_SIZE = 20

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP,TCP_PORT))
s.listen(1)



quit = False
while not quit:
	conn, addr = s.accept()
	print 'Connection Address:', addr
	while 1:
		data = conn.recv(BUFFER_SIZE)
		# if data == 'q':
		# 	quit = True
		if not data: break
		print 'received data:', data
		conn.send(data)

	conn.close()

