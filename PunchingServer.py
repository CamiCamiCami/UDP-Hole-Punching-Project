import socket
from ipaddress import ip_address
import subprocess

# Un servidor que recive las direcciones de dos clientes y les responde la información de conexion del otro
# Los clientes se deben connectar enviando un paquete udp al servidor que preferiblemente contenga su dirección IP anterior

def msg_to_ip(old_ip: bytes) -> str:
    try:
        ip_obj = ip_address(old_ip)
        return str(old_ip)
    except ValueError:
        return ""

def handle_same_client(check_client, new_ip, new_port):
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

def get_addr(i: int) -> tuple[str, int]:
    if i == 1 or i == 0:
        ip, port, _ = CLIENTS[i]
        return (ip, port)
    else:
        raise ValueError

def get_url_ip():
    command = f"dig +short {URL}"
    result = subprocess.run(command, shell = True, executable="/bin/bash", stdout=subprocess.PIPE)
    return str(result.stdout)

def get_actual_ip():
    command = "curl http://icanhazip.com/"
    result = subprocess.run(command, shell = True, executable="/bin/bash", stdout=subprocess.PIPE)
    return str(result.stdout)

def update_server_url():

    while get_url_ip() != get_actual_ip():
        print(f"SERVER INFO] Updating url {URL}")
        command = f"noip-duc -u cammilo -p hipnoiphate -g {URL} --once"
        subprocess.run(command, shell = True, executable="/bin/bash")

    

URL = "camidirr.webhop.me"
HOST = ''
PORT = 42069
CLIENTS: list[tuple[str, int, str]] = []

print(get_actual_ip())
print(get_url_ip())
print(get_url_ip() == get_actual_ip())

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:

    s.bind((HOST, PORT))

    while len(CLIENTS) < 2:
        msg, addr = s.recvfrom(1024)
        ip, port = addr

        add_client(ip, port, msg)

    s.sendto(str(get_addr(0)).encode('utf-8'), get_addr(1))
    s.sendto(str(get_addr(1)).encode('utf-8'), get_addr(0))