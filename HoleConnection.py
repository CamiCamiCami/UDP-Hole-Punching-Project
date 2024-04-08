# Echo client program
import queue
import socket
from enum import Enum
from math import ceil
from multiprocessing import Process, Queue
from time import sleep
from typing import Tuple, List

def get_pck_number(data: bytearray) -> int:


def open_pck(pck: bytearray) -> bytearray:
    pck.pop()
    pck.pop(0)
    pck.

class MessageBuilder():
    def __init__(self):
        self.parts = dict()
        self.id = None
        self.has_end = False
        self.expected_pck = None
        
    def add(self, data: bytearray):
        if self.check_id(data):
            data.pop()
            self.parts[data.pop()] = data[1:]
            if data[-2] == ETX:
                self.has_end = True
                self.expected_pck = 


    def check_id(self, data: bytearray):
        if not self.id:
            self.set_id(data)
            return True
        return data[0] == self.id
    
    def set_id(self, data:bytearray):
        self.id = data[0]
    
    def.is

    def build(self) -> bytes:
        


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


def msg_exist(msg) -> bool:
    return bool(msg)


def msg_has_end(msg) -> bool:
    last_key = max(msg.keys())
    return msg[last_key][-1] == ord(ETX)


def msg_is_complete(msg) -> bool:
    biggest_key = max(msg.keys())
    return list(msg.keys()) == list(range(1, biggest_key + 1))


def is_message_full(msg: dict):
    print(msg_exist(msg))
    if not msg:
        return False
    print(msg_has_end(msg))
    print(msg_is_complete(msg))
    return msg_exist(msg) and msg_has_end(msg) and msg_is_complete(msg)


def build_message(message_builder: dict):
    message = bytearray()
    max_key = max(message_builder.keys())
    for i in range(1, max_key + 1):
        message += message_builder[i]
    return bytes(message)


def receive_message():
    message_builder = dict()
    while not is_message_full(message_builder):
        data = catch_message()
        data = bytearray(data)
        if not data:
            sleep(1)
            continue
        print(data.hex())
        t = data.pop()
        if t != 0:
            raise ValueError
        message_builder[data.pop()] = data

    return build_message(message_builder)


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
