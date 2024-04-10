from typing import Tuple, List
from Utils import *
import queue
from multiprocessing import Queue
import socket
from math import ceil
from enum import Enum


ACKNOWLEDMENTS: Queue = Queue()
BUFFER_SIZE = 1024
HOST = 'camidirr.webhop.me'
PORT = 42069


class MessageBuilder():
    def __init__(self):
        self.parts: dict = dict()
        self.id: int | None = None
        self.has_end: bool = False
        self.expected_pcks: int | None = None

    def set_id(self, id:int):
        self.id = id

    def get_id(self):
        return self.id

    def add(self, pck: bytearray) -> bool:
        id, key, data = open_pck(pck)
        print("Paquete abierto: ", (id, key, data))
        print("id propia es:", self.id, self._check_id(id))

        if self._check_id(id):
            self.parts[key] = data
            if is_etx(data[-1]):
                self.has_end = True
                self.expected_pcks = key
            return True
        return False

    def can_build(self):
        return bool(self.parts) and self.has_end and self._msg_is_complete()

    def build(self) -> str:
        msg = bytearray()
        for data in self.parts.values():
            msg += data
        return msg

    def _msg_is_complete(self) -> bool:
        return len(self.parts) == self.expected_pcks
    
    def _check_id(self, data_id: int):
        if not self.id:
            self.set_id(data_id)
            return True
        return data_id == self.id


class Receiver():
    def __init__(self, socket: socket.socket):
        self.s = socket
        self.cache_pcks = queue.Queue()

    def get(self) -> str:
        server_ip = self.get_server_ip()
        while ip == server_ip:
            pck, addr = self._recive_from()
            ip, _ = addr

        msg = self.process_from_peer(pck)
        return msg
    
    def recive_server(self):
        pass

    def recive_peer(self):
        pass


    def get_from_server(self):
        to_cache = []
        server_ip = self.get_server_ip()
        while ip != server_ip:
            pck, addr = self._recive_from()
            to_cache.append((pck, addr))
            ip, _ = addr
        to_cache.pop()

        for data in to_cache:
            self.cache_pcks.put(data)

        msg = self.process_from_server(pck)
        return msg

    def process_from_server(self, pck) -> Tuple[str, int]:
        ip_raw = pck[:4]
        port_raw = pck[4:6]
        ip = ""
        for n in ip_raw:
            digits = str(n)
            ip += digits
            ip += '.'
        ip = ip[:-1]

        port = int.from_bytes(port_raw, 'big')
        return ip, port


    def process_from_peer(self, pck):
        to_cache = []
        builder = MessageBuilder()
        builder.add(pck)

        while not builder.can_build():
            pck, addr = self._recive_from()
            if not builder.add(pck):
                to_cache.append((pck, addr))
        
        for pck_addr in to_cache:
            self.cache_pcks.put(pck_addr, block=True)
        
        msg = builder.build()
        return remove_etx(msg)

    def _receive(self) -> bytearray:
        pck, _ = self._receive_from()
        return pck

    def _recive_from(self) -> Tuple[bytearray, Tuple[str, int]]:
        try:
            pck = self.cache_pcks.get(block=False)
        except queue.Empty:
            pck = self._wait_receive()
        finally:
            return pck

    def _wait_receive(self):
        return INCOMING_MESSAGES.get(block=True, timeout=None)    
    

def divide_message(data: bytearray) -> List[bytearray]:
    max_size = BUFFER_SIZE - 3
    n_msgs = ceil(len(data) / max_size)
    msgs = []
    for _ in range(n_msgs):
        msgs.append(data[:max_size])
        data = data[max_size:]
    return msgs

class Sender():
    def __init__(self, socket: socket.socket):
        self.s = socket
        self.msg_tracker = 1
    
    def send(self, to: Source, msg):
        if to == Source.SERVER:
            to_send = self.pack2server(msg)
        else:
            to_send = self.pack2peer(msg)
        
        addr = self._get_addr(to)
        for pck in to_send:
            length = len(pck)
            sent = 0
            while length > sent:
                sent = self.s.sendto(pck, addr)
        


    
    def pack2server(self, msg: str) -> List[bytes]:
        pck = msg.encode('ascii')
        return [pck]

    def pack2peer(self, msg: str) -> List[bytes]:
        msg += ETX
        data = msg.encode('ascii')
        pcks = divide_message(data)
        to_send = []
        for i, pck in enumerate(pcks, start=1):
            pck += int2byte(i)
            pck += TERMINATOR
            pck = int2byte(self.msg_tracker)
            to_send.append(pck)
        return to_send

    def set_peer_addr(self, ip: str):
        self.peer_addr = ip

    def _get_addr(self, dest: Source):
        if dest == Source.SERVER:
            return get_server_ip()
        else:
            return self.peer_addr


    



def open_pck(pck: bytearray) -> Tuple[int, int, bytearray]:
    if not is_terminator(pck.pop()):
        raise ValueError # temporal 
    
    part = pck.pop()
    id = pck.pop(0)
    return id, part, pck

def get_server_ip() -> str:
    return socket.gethostbyname(HOST)

def receiving_thread(s: socket.socket) -> None:
    print("THREAD-Thread woke up")
    while True:
        print("THREAD-Searching new message")
        data: bytearray = bytearray()
        while len(data) == 0 or data[-1]:
            try:
                new, addr = s.recvfrom(BUFFER_SIZE)
                data += new
                print("THREAD-Received: ", data.hex())
            except socket.error:
                print("THREAD-Unidentified error, continuing")
                pass
                
        INCOMING_MESSAGES.put((data, addr))