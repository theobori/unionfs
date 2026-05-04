"""The UnionFS deamon."""

from pathlib import Path
import socketserver
from typing import Any, Container, Dict, NoReturn

from unionfs.common.bind import InsertType
from unionfs.common.socket import send_packed_obj, recv_unpacked_obj
from unionfs.daemon.exceptions import (
    MountTableAlreadyExistError,
    MountTableNotExistError,
    MountTableValueError,
)
from unionfs.daemon.mount_table import MountTable

DAEMON_UNIX_SOCKET_PATH = "/tmp/unionfs.sock"


class UNIXDaemonHandler(socketserver.BaseRequestHandler):
    """_summary_"""

    # TODO: defined int code with enum for the daemon

    def __init__(self, request, client_address, server):
        # Little hack used for storing variable in
        if not hasattr(server, "unionfs_mount_table"):
            setattr(server, "unionfs_mount_table", MountTable[Path]())

        self.__mount_table = server.unionfs_mount_table

        super().__init__(request, client_address, server)

    def __send_obj(self, obj: Any) -> NoReturn:
        send_packed_obj(self.request, obj)

    def __recv_obj(self) -> Any:
        return recv_unpacked_obj(self.request)

    def __send_error(self, obj: Any) -> NoReturn:
        self.__send_obj({"status": "error", "value": obj})

    def __send_succes(self, obj: Any) -> NoReturn:
        self.__send_obj({"status": "success", "value": obj})

    def __send_error_if_missing_fields(
        self, obj: Any, fields: Container[str]
    ) -> NoReturn:
        if not hasattr(obj, "__contains__"):
            raise Exception("This object cannot be checked.")

        for field in fields:
            if not field in obj:
                self.__send_error(f"The field '{field}' is missing.")
                return True

        return False

    def __action_bind(
        self, source: Path, destination: Path, insert_type: InsertType
    ) -> NoReturn:
        try:
            self.__mount_table.create_bind(source, destination, insert_type)
            self.__send_succes(None)
        except MountTableAlreadyExistError as e:
            self.__send_error("already exist")
        except MountTableValueError as e:
            self.__send_error("bad insert")
        except Exception as e:
            self.__send_error("server side only error")
            # TODO: write logs
            raise e

    def __action_bind_with_dict(self, _dict: Dict[str, Any]) -> NoReturn:
        err = self.__send_error_if_missing_fields(
            _dict, ("source", "destination", "insert_type")
        )
        if err:
            return

        insert_type = InsertType.from_value(_dict["insert_type"])

        self.__action_bind(
            Path(_dict["source"]), Path(_dict["destination"]), insert_type
        )

    def __action_list(self, source: Path) -> NoReturn:
        hs = self.__mount_table.get_bind(source)
        self.__send_succes(list(hs))

    def __action_list_with_dict(self, _dict: Dict[str, Any]) -> NoReturn:
        err = self.__send_error_if_missing_fields(_dict, ("source",))
        if err:
            return

        self.__action_list(Path(_dict["source"]))

    def __action_list_all(self) -> NoReturn:
        table = self.__mount_table.table
        table = {k: list(v) for k, v in table.items()}

        self.__send_succes(table)

    def __action_list_all_with_dict(self) -> NoReturn:
        self.__action_list_all()

    def __action_unbind(self, source: Path, destination: Path) -> NoReturn:
        try:
            self.__mount_table.remove_bind(source, destination)
            self.__send_succes(None)
        except MountTableNotExistError as e:
            self.__send_error("value does not exist")

    def __action_unbind_with_dict(self, _dict: Dict[str, Any]) -> NoReturn:
        err = self.__send_error_if_missing_fields(_dict, ("source", "destination"))
        if err:
            return

        self.__action_unbind(Path(_dict["source"]), Path(_dict["destination"]))

    def handle(self):
        obj = self.__recv_obj()

        if not isinstance(obj, dict):
            self.__send_error("You must send a Python dictionnary.")
            return

        err = self.__send_error_if_missing_fields(obj, ("action",))
        if err:
            return

        match obj["action"]:
            case "bind":
                self.__action_bind_with_dict(obj)
            case "list":
                self.__action_list_with_dict(obj)
            case "list_all":
                self.__action_list_all_with_dict(obj)
            case "unbind":
                self.__action_unbind_with_dict(obj)
            case _:
                self.__send_error("The 'action' value is invalid.")
