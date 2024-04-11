ETX = '\x03'  # End Of Text
TERMINATOR = '\0'
ACK = '\x06'
KEEP_ALIVE = '\x07'
HELLO = '\x05'
HELLO_BACK = HELLO + HELLO


def get_server_ip(server_url) -> str:
    return socket.gethostbyname(server_url)

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

def is_keep_alive(pck) -> bool:
    return open_peer_pck(pck) == KEEP_ALIVE


def int2byte(n: int) -> bytes:
    try:
        return n.to_bytes(1, 'big')
    except OverflowError:
        raise ValueError

def is_terminator(byte):
    try:
        byte = chr(byte)
    except TypeError:
        if not type(byte) == chr:
            raise TypeError 
    finally:
        return byte == TERMINATOR

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

def remove_terminator(msg):
    if is_terminator(msg[-1]):
        return msg[:-1]
    else:
        raise ValueError

