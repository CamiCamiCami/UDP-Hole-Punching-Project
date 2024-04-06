# Echo client program
import socket


def is_digit(c: chr) -> bool:
    return 47 < ord(c) < 58


def parse_dirr(data: str) -> tuple[int, str]:
    port, ip = data.split(',', 1)
    port = "".join(c for c in port if is_digit(c))
    ip = "".join(c for c in ip if is_digit(c) or c == '.')
    port = int(port)
    return port, ip


HOST = 'camidirr.webhop.me'
PORT = 42069

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(b"", (HOST, PORT))
    data = s.recv(1024)
    print('Received', repr(data))
    s.sendto("Hola".encode("utf-8"), parse_dirr(str(data)))
    data = s.recv(1024)
    print('Received', repr(data))
