ETX = '\x03'  # End Of Text
TERMINATOR = '\0'

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

