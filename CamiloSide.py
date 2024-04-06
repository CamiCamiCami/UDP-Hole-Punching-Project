# Echo client program
import socket
from typing import Tuple


def is_digit(c: chr) -> bool:
    return 47 < ord(c) < 58


def parse_addr(data: str) -> Tuple[str, int]:
    ip, port = data.split(',', 1)
    port = "".join(c for c in port if is_digit(c))
    ip = "".join(c for c in ip if is_digit(c) or c == '.')
    port = int(port)
    return ip, port


HOST = 'camidirr.webhop.me'
PORT = 42069

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(b"", (HOST, PORT))
    data = s.recv(1024)
    print('Received', repr(data))
    leozoip, leozoport = parse_addr(str(data))
    print(leozoip)
    print(leozoport)
    s.sendto(b"Hola", (leozoip, leozoport))
    data = s.recv(1024)
    print('Received', repr(data))
