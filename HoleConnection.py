import queue
from GatekeeperThread import INCOMING_MESSAGES, gatekeeper_thread, EXITING_MESSAGES
from Utils import * 
import socket
from multiprocessing import Process, Lock
from timer import Timer

class HoleConnection:
    def __init__(self, sock:socket.socket, server: str, name: str) -> None:
        self.server = server
        self.name = name
        self.cached_pck = None
        self.gatekeeper = Process(target=gatekeeper_thread, args=(sock, server, name))
        self.gatekeeper.start()

    def send(self, msg: str):
        pck = pack2peer(msg)
        self.wait4ack()
        self._send(pck)
        self.cached_pck = pck
        self.wait4ack()

    def receive(self):
        while True:
            pck = self._receive()
            if is_ack(pck):
                continue #Descarta paquetes de reconocimiento por llegar cuando no deben
            msg = open_peer_pck(pck)
            return msg

    def _send(self, msg):
        EXITING_MESSAGES.put(msg)

    def _receive(self, timeout=None):
        try:
            return INCOMING_MESSAGES.get(timeout=timeout)
        except queue.Empty:
            raise TimeoutError

    def wait4ack(self):
        if self.cached_pck is None:
            return
        timeout = 10.0
        timeout_timer = Timer(timeout)
        was_acknowledged = False
        while not was_acknowledged:
            if timeout_timer.has_finished():
                self._send(self.cached_pck)
                timeout_timer.reset()

            try:
                pck, addr = self._receive(timeout=timeout)
            except TimeoutError:
                continue
            if is_ack(pck):
                was_acknowledged = True
        self.cached_pck = None

    def __del__(self):
        print("Me hicieron vrg")
        self.gatekeeper.kill()