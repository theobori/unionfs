import socket

from enum import IntEnum, StrEnum
from pathlib import Path
from typing import Any, NoReturn

from unionfs.exceptions import UnionFSError
from unionfs.protocol.client import _client_send_and_receive_response
from unionfs.protocol.specification.action.action import ActionValue
from unionfs.protocol.specification.error import ErrorMessageValue
from unionfs.protocol.specification.field import Field
from unionfs.protocol.specification.status import StatusValue


class UmountMessageField(StrEnum):
    ROOT = Field.ROOT


class UMountErrorMessageValue(IntEnum):
    MOUNTPOINT_DOES_NOT_EXIST = ErrorMessageValue.MOUNTPOINT_DOES_NOT_EXIST
    SERVER_ERROR = ErrorMessageValue.SERVER_ERROR


def _client_umount(sock: socket.socket, root: Path) -> NoReturn:
    status: StatusValue
    message: Any
    try:
        status, message = _client_send_and_receive_response(
            sock,
            {
                Field.ACTION: ActionValue.UMOUNT,
                UmountMessageField.ROOT: str(root.absolute()),
            },
        )
    except Exception as e:
        raise e

    if status == StatusValue.SUCCESS:
        return

    match message:
        case UMountErrorMessageValue.MOUNTPOINT_DOES_NOT_EXIST:
            raise UnionFSError(
                f"The UnionFS mountpoint '{root.absolute()}' doest not exists."
            )
        case UMountErrorMessageValue.SERVER_ERROR:
            raise UnionFSError("Server internal error.")


def client_umount(unix_socket_path: Path, root: Path) -> NoReturn:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        try:
            sock.connect(str(unix_socket_path.absolute()))
            _client_umount(sock, root)
        except Exception as e:
            raise e
