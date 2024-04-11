# Echo client program
import socket
from HoleConnection import HoleConnection

HOST = 'camidirr.webhop.me'
PORT = 42069

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    conn = HoleConnection(s, HOST, "Camilo")
    conn.send("Hola Celu!!!")
    msg = conn.receive()
    print(msg)
