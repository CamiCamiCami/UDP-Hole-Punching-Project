# Echo client program
import socket
from typing import Tuple, List


def is_digit(c: chr) -> bool:
    return 47 < ord(c) < 58


def parse_addr(addr: bytes):
    ip_raw = addr[:4]
    port_raw = addr[4:6]
    ip = ""
    for n in ip_raw:
        digits = str(n)
        ip += digits
        ip += '.'
    ip = ip[:-1]
    port = int.from_bytes(port_raw, 'big')
    return ip, port


def receive(s: socket.socket) -> bytes:
    data = bytearray()
    while len(data) == 0 or data[-1] == '\0':
        try:
            data += s.recv(1024)
        except socket.timeout:
            return b""
    return bytes(data)



def connect2server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(30.0)

        s.sendto(b"", (HOST, PORT))
        data = receive(s)

        print('Received', repr(data))
        camiloip, camiloport = parse_addr(data)
        print(camiloip)
        print(camiloport)
        s.sendto(b"Mundo", (camiloip, camiloport))
        data = receive(s)
        print('Received', repr(data))


HOST = 'camidirr.webhop.me'
PORT = 42069

connect2server()
