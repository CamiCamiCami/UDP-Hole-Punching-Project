# Echo client program
import queue
import socket
from enum import Enum
from multiprocessing import Process, Lock, Queue
from time import sleep
from typing import Tuple, List


class Source(Enum):
    SERVER = "srv"
    PEER = "peer"


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
                pass
            finally:
                print("THREAD-Received: ", data.hex())
        print("THREAD-Found new message: ", data.hex())
        INCOMING_MESSAGES.put(data)


def catch_message() -> bytes:
    msg = b""
    try:
        msg = INCOMING_MESSAGES.get()
        print("Message found: ", msg)
    except queue.Empty:
        print("No message found")
        pass
    finally:
        return msg


def connect2server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        receiver = Process(target=receiving_thread, args=(s,))
        receiver.start()

        s.sendto(b"", (HOST, PORT))
        data = b""
        while not data:
            data = catch_message()
            if data:
                print('Received', data.hex())
            sleep(3)

        camiloip, camiloport = parse_addr(data)
        print(camiloip)
        print(camiloport)

        s.sendto(b"Mundo", (camiloip, camiloport))
        data = b""
        while not data:
            data = catch_message()
            if data:
                print('Received', data.hex())
            sleep(3)

        receiver.kill()


BUFFER_SIZE = 1024
INCOMING_MESSAGES: Queue = Queue()
HOST = 'camidirr.webhop.me'
PORT = 42069

connect2server()
