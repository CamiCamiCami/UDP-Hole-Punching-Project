import queue

from GatekeeperThread import INCOMING_MESSAGES, gatekeeper_thread
from Utils import * 
import socket 
from math import ceil
from time import time_ns
from multiprocessing import Process, Lock, Manager
from typing import Tuple, List

from timer import Timer

SEND_LOCK = Lock()

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

        server_ip = get_server_ip(self.server)
        pck, (ip, _) = self.get_pck(timeout=timeout)
        while server_ip == ip:
            pck, (ip, _) = self.get_pck(timeout=timeout)
        return pck

    def get_srv_pck(self, timeout=None):
        to_cache = []
        server_ip = get_server_ip(self.server)
        pck, (ip, _) = self.get_pck(timeout=timeout)
        while server_ip != ip:
            to_cache.append(pck)
            pck, (ip, _) = self.get_pck(timeout=timeout)
        for pck in to_cache:
            self.peer_cache_pcks.put(pck)
        return pck
    def return_peer_pck(self, pck: bytes):
        self.peer_cache_pcks.put(pck)

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
        self._sendto = lambda pck, addr: ___sendto(sock, pck, addr)

        self.receiving_thread = Process(target=gatekeeper_thread, args=(sock,))
        self.receiving_thread.start()

    def send(self, msg: str):
        addr = self.get_addr()
        pck = pack2peer(msg)
        self.wait4ack(addr)
        self.sendto(pck, addr)
        self.cached_pck = pck
        self.wait4ack(addr)

    def receive(self):
        while True:
            timeout = 30.0
            pck = self.mailbox.get_peer_pck(timeout=timeout)
            if is_ack(pck):
                continue #Descarta paquetes de reconocimiento por llegar cuando no deben

            msg = open_peer_pck(pck)
            return msg

    def sendto(self, msg, addr):
        self._sendto(msg, addr)


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

def connect2server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        pass





connect2server()
