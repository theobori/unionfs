import socket

from enum import IntEnum, StrEnum
from pathlib import Path
from typing import Any, NoReturn

from unionfs.common.bind import InsertType
from unionfs.protocol.client import _client_send_and_receive_response
from unionfs.protocol.specification.field import Field
from unionfs.protocol.specification.error import ErrorMessageValue
from unionfs.protocol.specification.action import ActionValue
from unionfs.protocol.specification.status import StatusValue
from unionfs.exceptions import UnionFSError


class BindMessageField(StrEnum):
    SOURCE = Field.SOURCE
    DESTINATION = Field.DESTINATION
    INSERT_TYPE = Field.INSERT_TYPE


class BindErrorMessageValue(IntEnum):
    MOUNTPOINT_DOES_NOT_EXIST = ErrorMessageValue.MOUNTPOINT_DOES_NOT_EXIST
    INVALID_INSERT_TYPE = ErrorMessageValue.INVALID_INSERT_TYPE
    BINDING_ALREADY_EXISTS = ErrorMessageValue.BINDING_ALREADY_EXISTS
    SERVER_ERROR = ErrorMessageValue.SERVER_ERROR


def _client_bind(
    sock: socket.socket, source: Path, destination: Path, insert_type: InsertType
) -> NoReturn:
    status: StatusValue
    message: Any
    try:
        status, message = _client_send_and_receive_response(
            sock,
            {
                Field.ACTION: ActionValue.BIND,
                BindMessageField.SOURCE: str(source.absolute()),
                BindMessageField.DESTINATION: str(destination.absolute()),
                BindMessageField.INSERT_TYPE: insert_type.value,
            },
        )
    except Exception as e:
        raise e

    if status == StatusValue.SUCCESS:
        return

    match message:
        case BindErrorMessageValue.MOUNTPOINT_DOES_NOT_EXIST:
            # Lazy to create more precise exceptions
            raise UnionFSError(
                f"The UnionFS mountpoint '{source.absolute()}' does not exist."
            )
        case BindErrorMessageValue.INVALID_INSERT_TYPE:
            raise UnionFSError(
                f"The insert type '{insert_type}' is invalid."
            )  # It should never happen
        case BindErrorMessageValue.BINDING_ALREADY_EXISTS:
            raise UnionFSError(
                f"The binding '{source.absolute()}' to '{source.absolute()}' already exists."
            )
        case BindErrorMessageValue.SERVER_ERROR:
            raise UnionFSError("Server internal error.")


def client_bind(
    unix_socket_path: Path, source: Path, destination: Path, insert_type: InsertType
) -> NoReturn:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        try:
            sock.connect(str(unix_socket_path.absolute()))
            _client_bind(sock, source, destination, insert_type)
        except Exception as e:
            raise e
