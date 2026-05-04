"""The UnionFS client module."""

from pathlib import Path
import socket
from typing import Any, Dict, Tuple

from unionfs.common.socket import send_packed_obj, recv_unpacked_obj


def client_send_and_recv_obj(unix_socket: Path, obj: Any) -> Tuple[str, Any]:
    """_summary_

    Args:
        unix_socket (Path): _description_
        obj (Any): _description_

    Raises:
        e: _description_
        ValueError: _description_
        ValueError: _description_

    Returns:
        Tuple[str, Any]: _description_
    """

    recv_obj: Dict[str, Any]
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        try:
            sock.connect(unix_socket.absolute().name)
            send_packed_obj(sock, obj)
            recv_obj = recv_unpacked_obj(sock)
        # Lazy to catch all exceptions
        except Exception as e:
            raise e

    if recv_obj is None:
        raise ValueError("Invalid received object.")

    for field in ("status", "value"):
        if not field in recv_obj:
            raise ValueError(f"Missing the '{field}' field.")

    return recv_obj["status"], recv_obj["value"]
