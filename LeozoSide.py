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


def prepare2send_addr(addr: Tuple[str, int]) -> bytearray:
    ip, port = addr
    ip_parts = ip.split('.', 3)
    message = bytearray()
    for digits in ip_parts:
        n = int(digits)
        message.append(n)
    port = port.to_bytes(2, 'big')
    message = message + port
    return message


HOST = 'camidirr.webhop.me'
PORT = 42069

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(b"", (HOST, PORT))
    data = s.recv(1024)
    print('Received', repr(data))
    camiloip, camiloport = parse_addr(data)
    print(camiloip)
    print(camiloport)
    s.sendto(b"Mundo", (camiloip, camiloport))
    data = s.recv(1024)
    print('Received', repr(data))
