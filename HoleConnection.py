import queue
import socket
from enum import Enum
from math import ceil
from multiprocessing import Process, Queue
from time import sleep
from typing import Tuple, List


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


def is_terminator(byte):
    try:
        byte = chr(byte)
    except TypeError:
        if not type(byte) == chr:
            raise TypeError 
    finally:
        return byte == '\0'

def is_etx(byte):
    try:
        byte = chr(byte)
    except TypeError:
        if not type(byte) == chr:
            raise TypeError 
    finally:
        return byte == ETX


def remove_etx(msg):
    if is_etx(msg[-1]):
        return msg[:-1]
    else:
        raise ValueError

def open_pck(pck: bytearray) -> Tuple[int, int, bytearray]:
    if not is_terminator(pck.pop()):
        raise ValueError # temporal 
    
    part = pck.pop()
    id = pck.pop(0)
    return id, part, pck

class MessageBuilder():
    def __init__(self):
        self.parts: dict = dict()
        self.id: int | None = None
        self.has_end: bool = False
        self.expected_pcks: int | None = None
    
    def __init__(self, pck: bytearray) -> None:
        self.__init__()
        self.add(pck)

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
    

class Source(Enum):
    SERVER = "srv"
    PEER = "peer"


class Receiver():
    def __init__(self, socket: socket.socket):
        self.s = socket
        self.cache_pcks = queue.Queue()

    def get(self) -> Tuple[Source, str | Tuple[str, int]]:
        pck, addr = self._recive_from()
        ip, port = addr

        if ip == self.get_server_ip():
            source = Source.SERVER
            msg = self.process_from_server(pck)
        else:
            source = Source.PEER
            msg = self.process_from_peer(pck)
        
        return source, msg
    

    def process_from_server(pck) -> Tuple[str, int]:
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
        builder = MessageBuilder(pck)

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

    def get_server_ip(self) -> str:
        return socket.gethostbyname(HOST)


def int2byte(n: int) -> bytes:
    try:
        return n.to_bytes(1, 'big')
    except OverflowError:
        raise ValueError


def ip2source(ip: str) -> Source:
    return Source.SERVER


def is_digit(c: chr) -> bool:
    return 47 < ord(c) < 58

def divide_message(data: bytearray) -> List[bytearray]:
    max_size = BUFFER_SIZE - 2
    n_msgs = ceil(len(data) / max_size)
    msgs = []
    for n in range(n_msgs):
        msgs.append(data[:max_size])
        data = data[max_size:]
    return msgs


def send_message(s: socket.socket, data: str, addr: Tuple[str, int]) -> None:
    data += ETX
    data = data.encode('ascii')
    data = bytearray(data)
    messages = divide_message(data)
    for i, msg in enumerate(messages, 1):
        msg += int2byte(i)
        msg += b'\x00'
        msg = b'\x01' + msg
        s.sendto(msg, addr)


def connect2server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        thread = Process(target=receiving_thread, args=(s,))
        thread.start()

        receiver = Receiver(s)

        s.sendto(b"", (HOST, PORT))
        recived = receiver.get()
        _, peer_addr = recived

        send_message(s, "Buen dia", peer_addr)
        _, msg = Receiver.get()
        print(msg)

        thread.kill()


ETX = '\x03'  # End Of Text
BUFFER_SIZE = 1024
INCOMING_MESSAGES: Queue = Queue()
HOST = 'camidirr.webhop.me'
PORT = 42069

connect2server()
