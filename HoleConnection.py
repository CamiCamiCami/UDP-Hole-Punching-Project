import queue

from ConnectionHelpers import *
from Utils import * 
import socket 
from math import ceil
from time import time_ns
from multiprocessing import Process, Lock
from typing import Tuple, List

SEND_LOCK = Lock()
INCOMING_MESSAGES: Queue = Queue()
ACK = '\x06'

class Timer:
    def __init__(self, seconds: float):
        self.length = ceil(seconds * 1000000000)
        self.end_time = time_ns() + self.length

    def has_finished(self) -> bool:
        return time_ns() > self.end_time

    def reset(self):
        self.end_time = time_ns() + self.length


def _get_pck(timeout=None):
    try:
        return INCOMING_MESSAGES.get(timeout=timeout)
    except queue.Empty:
        raise TimeoutError


class MailBox:
    def __init__(self, server_url: str):
        self.peer_cache_pcks = queue.Queue()
        self.server = server_url
        self.get_pck = _get_pck

    def get_peer_pck(self, timeout=None) -> bytes:
        if not self.peer_cache_pcks.empty():
            return self.peer_cache_pcks.get_nowait()

        server_ip = socket.gethostbyname(self.server)
        pck, (ip, _) = self.get_pck(timeout=timeout)
        while server_ip == ip:
            pck, (ip, _) = self.get_pck(timeout=timeout)
        return pck

    def get_srv_pck(self, timeout=None):
        to_cache = []
        server_ip = socket.gethostbyname(self.server)
        pck, (ip, _) = self.get_pck(timeout=timeout)
        while server_ip != ip:
            to_cache.append(pck)
            pck, (ip, _) = self.get_pck(timeout=timeout)
        for pck in to_cache:
            self.peer_cache_pcks.put(pck)
        return pck
    def return_peer_pck(self, pck: bytes):
        self.peer_cache_pcks.put(pck)


def pack2peer(msg: str) -> bytes:
    pck = msg.encode('ascii')
    return pck + b'\x00'

def open_peer_pck(pck: bytes):
    pck = remove_terminator(pck)
    return pck.decode('ascii')

def open_server_pck(pck):
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


def is_ack(pck) -> bool:
    return open_peer_pck(pck) == ACK

def ___sendto(sock, pck, addr):
    SEND_LOCK.acquire()
    n = sock.sendto(pck, addr)
    SEND_LOCK.release()
    return n


class HoleConnection:
    def __init__(self, sock:socket.socket, server: str, name: str) -> None:
        self.server = server
        self.mailbox = MailBox(server)
        self.name = name
        self.cached_pck = None
        self.send_lock = Lock()
        self.sendto = lambda pck, addr: ___sendto(sock, pck, addr)

        self.receiving_thread = Process(target=receiving_thread, args=(self.s,))
        self.receiving_thread.start()

    def send(self, msg: str):
        addr = self.get_addr()
        pck = pack2peer(msg)
        self.wait4ack(addr)
        self.sendto(pck, addr)
        self.cached_pck = pck
        self.wait4ack(addr)

    def receive(self):
        pass


    def wait4ack(self, addr):
        if self.cached_pck is None:
            return
        timeout = 10.0
        timeout_timer = Timer(timeout)
        was_acknowledged = False
        while not was_acknowledged:
            if timeout_timer.has_finished():
                self.sendto(self.cached_pck, addr)
                timeout_timer.reset()

            try:
                pck, addr = self.mailbox.get_peer_pck(timeout=timeout)
            except TimeoutError:
                continue

            if is_ack(pck):
                was_acknowledged = True

        self.cached_pck = None





    def get_addr(self):
        self.sendto(self.name, self.server)
        addr = None

        resend_time = 3.0
        resend_timer = Timer(resend_time)
        timeout_timer = Timer(10.0)

        while addr is None:
            if resend_timer.has_finished():
                self.sendto(self.name.encode('ascii'), self.server)
                resend_timer.reset()
            if timeout_timer.has_finished():
                raise TimeoutError

            try:
                pck = self.mailbox.get_srv_pck(timeout=resend_time)
            except TimeoutError:
                continue

            addr = open_server_pck(pck)
        return addr



    def __del__(self):
        print("Me hicieron vrg")
        self.receiving_thread.kill()


def send_message(s: socket.socket, data: str, addr: Tuple[str, int]) -> None:
    data += ETX
    data = data.encode('ascii')
    data = bytearray(data)
    messages = divide_message(data)
    for i, msg in enumerate(messages, 1):
        msg += int2byte(i)
        msg += b'\x00'
        msg = b'\x01' + msg 
        print("por enviar: ", msg)
        print(s.sendto(msg, addr))


def connect2server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:


        receiver = Receiver(s)

        s.sendto(b"", (HOST, PORT))
        recived = receiver.get()
        _, peer_addr = recived

        print(peer_addr)
        send_message(s, "Buen dia", peer_addr)
        _, msg = receiver.get()
        print(msg)

        thread.kill()





connect2server()
