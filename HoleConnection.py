# Echo client program
import queue
import socket
from enum import Enum
from math import ceil
from multiprocessing import Process, Queue
from time import sleep
from typing import Tuple, List

def is_terminator(byte):
    try:
        byte = chr(byte)
    except TypeError:
        if not type(byte) == chr:
            raise TypeError 
    finally:
        return byte == '\0'


def open_pck(pck: bytearray) -> Tuple[int, int, str]:
    if not is_terminator(pck.pop()):
        raise ValueError # temporal 
    
    part = pck.pop()
    id = pck.pop(0)
    return id, part, repr(pck)

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

    def add(self, pck: bytearray):
        id, key, data = open_pck(pck)
        if self._check_id(id):
            self.parts[key] = data
            if data[-1] == ETX:
                self.has_end = True
                self.expected_pcks = key

    def can_build(self):
        return bool(self.parts) and self.has_end and self._msg_is_complete()

    def build(self) -> str:
        msg = ""
        for s in self.parts.values():
            msg += s
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


def int2byte(n: int) -> bytes:
    try:
        return n.to_bytes(1, 'big')
    except OverflowError:
        raise ValueError


def ip2source(ip: str) -> Source:
    return Source.SERVER


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


def receiving_thread(s: socket.socket) -> None:
    print("THREAD-Thread woke up")
    while True:
        print("THREAD-Searching new message")
        data: bytearray = bytearray()
        while len(data) == 0 or data[-1]:
            try:
                data += s.recv(BUFFER_SIZE)
            except socket.error:
                print("THREAD-Unidentified error, continuing")
                pass
            finally:
                print("THREAD-Received: ", data.hex())
        print("THREAD-Found new message: ", data.hex())
        INCOMING_MESSAGES.put(data)


def catch_message() -> bytes:
    msg = b""
    try:
        msg = INCOMING_MESSAGES.get(block=False)
        print("Message found: ", msg)
    except queue.Empty:
        print("No message found")
        pass
    finally:
        return msg


def remove_etx(msg: str) -> str:
    if msg[-1] == ETX:
        return msg[:-1]
    else:
        raise ValueError


def receive_message():
    builder = MessageBuilder()
    while not builder.can_build():
        pck = catch_message()
        pck = bytearray(pck)
        if not pck:
            sleep(1)
            continue
        builder.add(pck)

    msg = builder.build()
    return remove_etx(msg)


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
    data = data.encode('utf-8')
    data = bytearray(data)
    messages = divide_message(data)
    for i, msg in enumerate(messages, 1):
        msg += int2byte(i)
        msg += b'\x00'
        s.sendto(msg, addr)


def connect2server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        receiver = Process(target=receiving_thread, args=(s,))
        receiver.start()

        s.sendto(b"", (HOST, PORT))
        data = b""
        while not data:
            data = receive_message()
            if data:
                print('Received', data.hex())
            sleep(3)

        addr = parse_addr(data)

        send_message(s, "Buen dia", addr)
        data = b""
        while not data:
            data = receive_message()
            if data:
                print('Received', data.hex())
            sleep(3)

        receiver.kill()


ETX = '\x03'  # End Of Text
BUFFER_SIZE = 1024
INCOMING_MESSAGES: Queue = Queue()
HOST = 'camidirr.webhop.me'
PORT = 42069

connect2server()
