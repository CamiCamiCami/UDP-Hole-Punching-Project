import array
import socket
from functools import reduce
from ipaddress import ip_address
import subprocess
from time import sleep
from typing import Tuple, List


# Un servidor que recive las direcciones de dos clientes y les responde la información de conexion del otro
# Los clientes se deben connectar enviando un paquete udp al servidor que preferiblemente contenga su dirección IP anterior

def msg_to_ip(old_ip: bytes) -> str:
    try:
        ip_obj = ip_address(old_ip)
        return str(old_ip)
    except ValueError:
        return ""


def handle_same_client(check_client, new_ip, new_port):
    return False
    check_ip, _, _ = check_client

    if check_ip == ip:
        print("SERVER INFO] Won't serve same client twice")
        CLIENTS.remove(check_client)
        return True
    return False


def handle_ip_change(check_client, old_ip):
    check_ip, _, _ = check_client
    if check_ip == old_ip and old_ip is True:
        print("SERVER INFO] Won't serve same client twice")
        CLIENTS.remove(check_client)
        return True
    return False


def add_client(ip: str, port: int, msg: bytes):
    old_ip = msg_to_ip(msg)

    for client in CLIENTS:
        if handle_same_client(client, ip, port):
            break
        if handle_ip_change(client, old_ip):
            break

    CLIENTS.append((ip, port, old_ip))
    print(f"SERVER INFO] Connected by {(ip, port)}")


def get_addr(i: int) -> Tuple[str, int]:
    if i == 1 or i == 0:
        _ip, _port, _ = CLIENTS[i]
        return _ip, _port
    else:
        raise ValueError


def get_url_ip():
    command = f"dig +short {URL}"
    result = subprocess.run(command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE)
    return str(result.stdout)


def get_actual_ip():
    command = "curl http://icanhazip.com/"
    result = subprocess.run(command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE)
    return str(result.stdout)


def update_server_url():
    while get_url_ip() != get_actual_ip():
        print(f"SERVER INFO] Updating url {URL}")
        command = f"noip-duc -u cammilo -p hipnoiphate -g {URL} --once"
        subprocess.run(command, shell=True, executable="/bin/bash")
        if get_url_ip() != get_actual_ip():
            sleep(90)


def prepare2send_addr(addr: Tuple[str, int]) -> bytes:
    ip, port = addr
    ip_parts = ip.split('.', 3)
    message = bytearray()
    for digits in ip_parts:
        n = int(digits)
        message.append(n)
    port = port.to_bytes(2, 'big')
    message += port
    return bytes(message)


URL = "camidirr.webhop.me"
HOST = ''
PORT = 42069
CLIENTS: List[Tuple[str, int, str]] = []

update_server_url()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))

    while len(CLIENTS) < 2:
        data, addr = s.recvfrom(1024)
        ip, port = addr

        add_client(ip, port, data)

    msg: bytes = prepare2send_addr(get_addr(0))
    s.sendto(msg, get_addr(1))
    msg = prepare2send_addr(get_addr(1))
    s.sendto(msg, get_addr(0))
