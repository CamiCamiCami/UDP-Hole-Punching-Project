from enum import Enum
from multiprocessing import Queue
import socket
from typing import Tuple

from timer import Timer
from Utils import *

INCOMING_MESSAGES: Queue = Queue()
EXITING_MESSAGES: Queue = Queue()
BUFFER_SIZE = 1024
HOSTRESS = 'camidirr.webhop.me'
PORT = 42069
SERV_URL = ""
NAME = ""

class MessageType(Enum):
    HELLO = HELLO
    HELLO_BACK_PCK = HELLO_BACK
    KEEP_ALIVE = KEEP_ALIVE
    PEER = "Peer"


def from_pck(pck: bytes) -> MessageType:
    msg = open_peer_pck(pck)
    if msg == MessageType.HELLO.value():
        return MessageType.HELLO
    elif msg == MessageType.KEEP_ALIVE.value():
        return MessageType.KEEP_ALIVE
    else:
        return MessageType.PEER


def is_server(addr):
    pass


def contact_server(s: socket.socket) -> Tuple[str, int]:
    timeout_timer = Timer(20.0)
    while not timeout_timer.has_finished():
        s.sendto(NAME, SERV_URL)
        try:
            pck, addr = s.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            continue

        if not is_server(addr):
            BUFFER_PCK.append(pck)
            continue
        else:
            return open_server_pck(pck)
    reconnect2srv(s)



KEEP_ALIVE_PCK = (KEEP_ALIVE + TERMINATOR).encode('ascii')
def send_keep_alive(s: socket.socket):
    addr = contact_server(s)
    s.sendto(KEEP_ALIVE_PCK, addr)

def send_all(s: socket.socket):
    addr = contact_server(s)
    while not EXITING_MESSAGES.empty():
        pck = EXITING_MESSAGES.get_nowait()
        s.sendto(pck, addr)

def connect2peer(s: socket.socket):
    say_hello(s)

def connect2srv(s: socket.socket):
    pck = None
    old_socket_timeout = s.gettimeout()
    s.settimeout(3.0)
    while not pck:
        s.sendto(NAME, SERV_URL)
        try:
            pck, addr = s.recvfrom(BUFFER_SIZE)
        except TimeoutError:
            continue

        if not is_server(addr):
            BUFFER_PCK.append(pck)
            pck = None
            continue
    s.settimeout(old_socket_timeout)

def reconnect2peer(s: socket.socket):
    connect2peer(s)

def reconnect2srv(s: socket.socket):
    connect2peer(s)

BUFFER_PCK = []
def receive(s: socket.socket) -> bytes:
    if BUFFER_PCK:
        return BUFFER_PCK.pop(0)
    try:
        while True:
            pck, addr = s.recvfrom(BUFFER_SIZE)
            if not is_server(addr):
                return pck
    except socket.timeout:
        raise TimeoutError

HELLO_PCK = (HELLO + TERMINATOR).encode('ascii')
HELLO_BACK_PCK = (HELLO_BACK + TERMINATOR).encode('ascii')
def say_hello(s: socket.socket):
    pck = None
    old_socket_timeout = s.gettimeout()
    s.settimeout(3.0)
    addr = contact_server(s)
    contact_server_timer = Timer(5.0)
    while not pck:
        if contact_server_timer.has_finished():
            addr = contact_server(s)
            contact_server_timer.reset()

        s.sendto(HELLO_PCK, addr)

        try:
            pck, addr = s.recvfrom(BUFFER_SIZE)
            if is_server(addr):
                pck = None
            if from_pck(pck) == MessageType.PEER:
                BUFFER_PCK.append(pck)
        except socket.timeout:
            pass
    s.settimeout(old_socket_timeout)

def answer_hello(s: socket.socket):
    addr = contact_server(s)
    s.sendto(HELLO_BACK_PCK, addr)

def init_thread(s: socket.socket, server: str, name: str):
    s.settimeout(1.0)
    SERV_URL.join(server)
    NAME.join(name)



def gatekeeper_thread(s: socket.socket, server_url: str, name: str) -> None:
    print("THREAD-Thread woke up")
    init_thread(s, server_url, name)
    connect2srv(s)
    connect2peer(s)
    keep_alive_timer = Timer(10.0)
    timeout_timer = Timer(30.0)
    contact_server_timer = Timer(5.0)
    while True:
        if keep_alive_timer.has_finished():
            send_keep_alive(s)
            keep_alive_timer.reset()

        if timeout_timer.has_finished():
            reconnect2peer(s)
            timeout_timer.reset()

        if contact_server_timer.has_finished():
            addr = contact_server(s)
            contact_server_timer.reset()

        send_all(s)

        try:
            pck = receive(s)
            msg_type = from_pck(pck)
            if msg_type == MessageType.PEER or msg_type == MessageType.KEEP_ALIVE:
                timeout_timer.reset()

            if msg_type == MessageType.HELLO:
                answer_hello(s)
            elif msg_type == MessageType.PEER:
                INCOMING_MESSAGES.put(pck)
        except TimeoutError:
            pass


    print("THREAD-Searching new message")
    print("THREAD-Received: ", data.hex())
    print("THREAD-Unidentified error, continuing")



