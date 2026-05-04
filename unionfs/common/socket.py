"""The common socket module."""

import struct
import socket

import msgpack

from typing import Any, ByteString, NoReturn


# Source - https://stackoverflow.com/a/17668009
# Posted by Adam Rosenfield, modified by community. See post 'Timeline' for change history
# Retrieved 2026-05-03, License - CC BY-SA 4.0
def send_msg(sock: socket.socket, msg: ByteString):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack(">I", len(msg)) + msg
    sock.sendall(msg)


# Source - https://stackoverflow.com/a/17668009
# Posted by Adam Rosenfield, modified by community. See post 'Timeline' for change history
# Retrieved 2026-05-03, License - CC BY-SA 4.0
def recv_msg(sock: socket.socket):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack(">I", raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


# Source - https://stackoverflow.com/a/17668009
# Posted by Adam Rosenfield, modified by community. See post 'Timeline' for change history
# Retrieved 2026-05-03, License - CC BY-SA 4.0
def recvall(sock: socket.socket, n: int):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def send_packed_obj(sock: socket.socket, obj: Any) -> NoReturn:
    send_msg(sock, msgpack.packb(obj))


def recv_unpacked_obj(sock: socket.socket) -> Any:
    msg = recv_msg(sock)
    obj = msgpack.unpackb(msg)

    return obj
