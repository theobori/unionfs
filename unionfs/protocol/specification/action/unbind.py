import socket

from enum import IntEnum, StrEnum
from pathlib import Path
from typing import Any, NoReturn

from unionfs.protocol.client import _client_send_and_receive_response
from unionfs.protocol.specification.field import Field
from unionfs.protocol.specification.error import ErrorMessageValue
from unionfs.protocol.specification.action import ActionValue
from unionfs.protocol.specification.status import StatusValue
from unionfs.exceptions import UnionFSError


class UnbindMessageField(StrEnum):
    SOURCE = Field.SOURCE
    DESTINATION = Field.DESTINATION


class UnbindErrorMessageValue(IntEnum):
    MOUNTPOINT_DOES_NOT_EXIST = ErrorMessageValue.MOUNTPOINT_DOES_NOT_EXIST
    BINDING_DOES_NOT_EXIST = ErrorMessageValue.BINDING_DOES_NOT_EXIST
    SERVER_ERROR = ErrorMessageValue.SERVER_ERROR


def _client_unbind(sock: socket.socket, source: Path, destination: Path) -> NoReturn:
    status: StatusValue
    message: Any
    try:
        status, message = _client_send_and_receive_response(
            sock,
            {
                Field.ACTION: ActionValue.UNBIND,
                UnbindMessageField.SOURCE: str(source.absolute()),
                UnbindMessageField.DESTINATION: str(destination.absolute()),
            },
        )
    except Exception as e:
        raise e

    if status == StatusValue.SUCCESS:
        return

    match message:
        case UnbindErrorMessageValue.MOUNTPOINT_DOES_NOT_EXIST:
            # Lazy to create more precise exceptions
            raise UnionFSError(
                f"The UnionFS mountpoint '{source.absolute()}' does not exist."
            )
        case UnbindErrorMessageValue.BINDING_DOES_NOT_EXIST:
            raise UnionFSError(
                f"The binding '{source.absolute()}' to '{destination.absolute()}' does not exist."
            )  # It should never happen
        case UnbindErrorMessageValue.SERVER_ERROR:
            raise UnionFSError("Server internal error.")


def client_unbind(unix_socket_path: Path, source: Path, destination: Path) -> NoReturn:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        try:
            sock.connect(str(unix_socket_path.absolute()))
            _client_unbind(sock, source, destination)
        except Exception as e:
            raise e
