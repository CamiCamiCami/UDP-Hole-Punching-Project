from ConnectionHelpers import *
from Utils import * 
import socket 
from math import ceil
from multiprocessing import Process
from typing import Tuple, List

class HoleSocket(socket.socket):
    def __init__() -> None:
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM, -1, None)
        



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
        thread = Process(target=receiving_thread, args=(s,))
        thread.start()

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
