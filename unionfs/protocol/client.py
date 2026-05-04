"""The UnionFS protocol client module."""

import socket

from pathlib import Path
from typing import Any, Dict, Tuple

from unionfs.common.socket import send_packed_obj, recv_unpacked_obj
from unionfs.protocol.specification.field import Field
from unionfs.exceptions import UnionFSValueError
from unionfs.protocol.specification.error import ErrorMessageValue
from unionfs.protocol.specification.status import StatusValue
from unionfs.exceptions import UnionFSError


def receive_response(sock: socket.socket) -> Tuple[StatusValue, Any]:
    try:
        recv_obj = recv_unpacked_obj(sock)
    except Exception as e:
        raise e

    if not isinstance(recv_obj, dict):
        raise UnionFSValueError("Invalid received object.")

    for field in (Field.STATUS, Field.MESSAGE):
        if not field in recv_obj:
            raise UnionFSValueError(f"Missing the '{field}' field.")

    status = recv_obj[Field.STATUS]
    message = recv_obj[Field.MESSAGE]

    if status == StatusValue.ERROR:
        match message:
            case ErrorMessageValue.INVALID_OBJECT_TYPE:
                raise UnionFSError("Sent an invalid object type.")
            case ErrorMessageValue.MISSING_FIELD:
                raise UnionFSError("Sent object with at least one missing field.")

    return status, message


def _client_send_and_receive_response(sock: socket.socket, obj: Any) -> Tuple[str, Any]:
    status: StatusValue
    message: Any
    try:
        send_packed_obj(sock, obj)
        status, message = receive_response(sock)
    # Lazy to catch all exceptions
    except Exception as e:
        raise e

    return status, message


def client_send_and_receive_response(
    unix_socket_path: Path, obj: Any
) -> Tuple[str, Any]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        try:
            sock.connect(str(unix_socket_path.absolute()))
            return _client_send_and_receive_response(sock, obj)
        except Exception as e:
            raise e
