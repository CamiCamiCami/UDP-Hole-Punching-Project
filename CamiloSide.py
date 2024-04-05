# Echo client program
import socket
#comment
HOST = 'camidirr.webhop.me'
PORT = 42069
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(b"", (HOST, PORT))
    data = s.recv(1024)
    print('Received', repr(data))