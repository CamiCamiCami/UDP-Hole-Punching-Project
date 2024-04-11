import array
import socket
from functools import reduce
from ipaddress import ip_address
import subprocess
from time import sleep
from typing import Tuple, List, Dict

from timer import Timer


# Un servidor que recive las direcciones de dos clientes y les responde la información de conexion del otro
# Los clientes se deben connectar enviando un paquete udp al servidor que preferiblemente contenga su dirección IP anterior

class Client:
    def __init__(self, name: str, ip: str, port: int):
        self.name = name
        self.ip = ip
        self.port = port
        self.timer = Timer(30)

    def reset_timeout_timer(self):
        self.timer.reset()

    def is_timeout(self):
        return self.timer.has_finished()

    def get_addr(self):
        return self.ip, self.port

    def get_name(self):
        return self.name

    def copy(self, client: Client):
        self.name = client.name
        self.ip = client.ip
        self.port = client.port

class ClientPair(dict):
    def __init__(self):
        super().__init__()

    def connect(self, client: Client):
        try:
            self[client.name].copy(client)
            return
        except AttributeError:
            if len(self) < 2:
                self[client.name] = client

    def disconnect(self, name: str):
        self.pop(name)





def get_url_ip():
    return socket.gethostbyname(URL)


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
    message += b'\x00'
    return bytes(message)

def wait4clients(s: socket.socket):
    while len(CLIENTS) < 2:
        pck, addr = s.recvfrom(1024)
        name = pck.decode('ascii')
        ip, port = addr
        print(f"SERVER INFO] Connected by {(ip, port, name)}")
        client = Client(name, ip, port)
        CLIENTS.connect(client)
    return list(CLIENTS.keys())

URL = "camidirr.webhop.me"
HOST = ''
PORT = 42069
CLIENTS: Dict[str, Client] = ClientPair()

update_server_url()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    names = wait4clients(s)
    while True:
        if CLIENTS[names[0]].is_timeout():
            CLIENTS.
            wait4clients()
        if client1_timer.has_finished():
            CLIENTS.pop(1)
            wait4clients()

        try:
            pck, addr = s.recvfrom(1024)
            ip, port = addr
            name = pck.decode('ascii')
            set_client()
        except socket.timeout:
            pass



    while len(CLIENTS) < 2:
        data, addr = s.recvfrom(1024)
        ip, port = addr

        add_client(ip, port, data)

    msg: bytes = prepare2send_addr(get_addr(0))
    s.sendto(msg, get_addr(1))
    msg = prepare2send_addr(get_addr(1))
    s.sendto(msg, get_addr(0))
