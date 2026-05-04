import socket

from enum import StrEnum
from pathlib import Path
from typing import Dict, List

from unionfs.protocol.client import _client_send_and_receive_response
from unionfs.protocol.specification.action import ActionValue
from unionfs.protocol.specification.field import Field


class ShowMessageField(StrEnum):
    ROOT = Field.ROOT


def _client_show(sock: socket.socket, root: Path) -> List[str]:
    message: List[str]
    try:
        _, message = _client_send_and_receive_response(
            sock,
            {
                Field.ACTION: ActionValue.SHOW,
                ShowMessageField.ROOT: str(root.absolute()),
            },
        )
    except Exception as e:
        raise e

    return message


def client_show(unix_socket_path: Path, root: Path) -> List[str]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        try:
            sock.connect(str(unix_socket_path.absolute()))
            return _client_show(sock, root)
        except Exception as e:
            raise e


def _client_show_all(sock: socket.socket) -> Dict[str, str]:
    message: Dict[str, str]
    try:
        _, message = _client_send_and_receive_response(
            sock,
            {
                Field.ACTION: ActionValue.SHOW_ALL,
            },
        )
    except Exception as e:
        raise e

    return message


def client_show_all(unix_socket_path: Path) -> Dict[str, str]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        try:
            sock.connect(str(unix_socket_path.absolute()))
            return _client_show_all(sock)
        except Exception as e:
            raise e
