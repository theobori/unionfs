"""The UnionFS deamon."""

import socketserver
import logging

from pathlib import Path
from typing import Any, Container, Dict, NoReturn

from unionfs.common.bind import InsertType
from unionfs.common.socket import send_packed_obj, recv_unpacked_obj
from unionfs.daemon.exceptions import (
    MountTableAlreadyExistError,
    MountTableNoMountPointError,
    MountTableNotExistError,
    MountTableValueError,
)
from unionfs.daemon.mount_table import MountTable
from unionfs.protocol.specification.error import ErrorMessageValue
from unionfs.protocol.specification.field import Field
from unionfs.protocol.specification.status import StatusValue
from unionfs.protocol.specification.action import ActionValue
from unionfs.protocol.specification.action.bind import BindMessageField
from unionfs.protocol.specification.action.unbind import UnbindMessageField
from unionfs.protocol.specification.action.mount import MountMessageField
from unionfs.protocol.specification.action.show import ShowMessageField

DAEMON_UNIX_SOCKET_PATH = "/tmp/unionfs.sock"

logger = logging.getLogger(__file__)

aa = 0


class UNIXDaemonHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        # Little hack used for storing values per server instance.
        #
        # Because this class is instanciated for each request it receives.
        if not hasattr(server, "unionfs_mount_table"):
            setattr(server, "unionfs_mount_table", MountTable[Path]())

        self.__mount_table: MountTable[Path] = server.unionfs_mount_table

        super().__init__(request, client_address, server)

    def __send_obj(self, obj: Any) -> NoReturn:
        send_packed_obj(self.request, obj)

    def __recv_obj(self) -> Any:
        return recv_unpacked_obj(self.request)

    def __send_error(self, obj: Any) -> NoReturn:
        self.__send_obj({Field.STATUS: StatusValue.ERROR, Field.MESSAGE: obj})

    def __send_succes(self, obj: Any) -> NoReturn:
        self.__send_obj({Field.STATUS: StatusValue.SUCCESS, Field.MESSAGE: obj})

    def __send_error_if_missing_fields(self, obj: Any, fields: Container[str]) -> bool:
        if not hasattr(obj, "__contains__"):
            raise Exception("This object cannot be checked.")

        for field in fields:
            if not field in obj:
                self.__send_error(ErrorMessageValue.MISSING_FIELD)
                return True

        return False

    def __action_bind(
        self, source: Path, destination: Path, insert_type: InsertType
    ) -> NoReturn:
        try:
            self.__mount_table.create_bind(source, destination, insert_type)
            self.__send_succes(ActionValue.BIND)
        except MountTableAlreadyExistError as e:
            self.__send_error(ErrorMessageValue.BINDING_ALREADY_EXISTS)
            logger.error(e)
        except MountTableValueError as e:
            self.__send_error(ErrorMessageValue.INVALID_INSERT_TYPE)
            logger.error(e)
        except MountTableNoMountPointError as e:
            self.__send_error(ErrorMessageValue.MOUNTPOINT_DOES_NOT_EXIST)
            logger.error(e)
        except Exception as e:
            self.__send_error(ErrorMessageValue.SERVER_ERROR)
            logger.error(e)
            raise e

        logger.info(
            f"Succesfully bound '{source.absolute()}' to '{source.absolute()}'."
        )

    def __action_bind_with_dict(self, _dict: Dict[str, Any]) -> NoReturn:
        err = self.__send_error_if_missing_fields(
            _dict,
            (
                BindMessageField.SOURCE,
                BindMessageField.DESTINATION,
                BindMessageField.INSERT_TYPE,
            ),
        )
        if err:
            return

        insert_type = InsertType.from_value(_dict[BindMessageField.INSERT_TYPE])

        self.__action_bind(
            Path(_dict[BindMessageField.SOURCE]),
            Path(_dict[BindMessageField.DESTINATION]),
            insert_type,
        )

    def __action_show(self, root: Path) -> NoReturn:
        hs = self.__mount_table.get_bind(root)
        self.__send_succes([str(x) for x in hs])

    def __action_show_with_dict(self, _dict: Dict[str, Any]) -> NoReturn:
        err = self.__send_error_if_missing_fields(_dict, (ShowMessageField.ROOT,))
        if err:
            return

        self.__action_show(Path(_dict[ShowMessageField.ROOT]))

    def __action_show_all(self) -> NoReturn:
        self.__send_succes(self.__mount_table.table_str)

    def __action_show_all_with_dict(self) -> NoReturn:
        self.__action_show_all()

    def __action_unbind(self, source: Path, destination: Path) -> NoReturn:
        try:
            self.__mount_table.remove_bind(source, destination)
            self.__send_succes(ActionValue.UNBIND)
        except MountTableNoMountPointError as e:
            self.__send_error(ErrorMessageValue.MOUNTPOINT_DOES_NOT_EXIST)
            logger.error(e)
        except MountTableNotExistError as e:
            self.__send_error(ErrorMessageValue.BINDING_DOES_NOT_EXIST)
            logger.error(e)
        except Exception as e:
            self.__send_error(ErrorMessageValue.SERVER_ERROR)
            logger.error(e)
            raise e

        logger.info(
            f"Succesfully unbound '{source.absolute()}' to '{source.absolute()}'."
        )

    def __action_unbind_with_dict(self, _dict: Dict[str, Any]) -> NoReturn:
        err = self.__send_error_if_missing_fields(
            _dict, (UnbindMessageField.SOURCE, UnbindMessageField.DESTINATION)
        )
        if err:
            return

        self.__action_unbind(
            Path(_dict[UnbindMessageField.SOURCE]),
            Path(_dict[UnbindMessageField.DESTINATION]),
        )

    def __action_mount(self, root: Path) -> NoReturn:
        try:
            self.__mount_table.mount_filesystem(root)
            self.__send_succes(ActionValue.MOUNT)
        except MountTableAlreadyExistError as e:
            self.__send_error(ErrorMessageValue.MOUNTPOINT_ALREADY_EXISTS)
            logger.error(e)
        except Exception as e:
            self.__send_error(ErrorMessageValue.SERVER_ERROR)
            logger.error(e)
            raise e

        logger.info(f"Succesfully mounted '{root.absolute()}'.")

    def __action_mount_with_dict(self, _dict: Dict[str, Any]) -> NoReturn:
        err = self.__send_error_if_missing_fields(_dict, (MountMessageField.ROOT,))
        if err:
            return

        self.__action_mount(Path(_dict[MountMessageField.ROOT]))

    def handle(self):
        obj = self.__recv_obj()

        if not isinstance(obj, dict):
            self.__send_error(ErrorMessageValue.INVALID_OBJECT_TYPE)
            return

        err = self.__send_error_if_missing_fields(obj, (Field.ACTION,))
        if err:
            return

        action: ActionValue = obj[Field.ACTION]

        global aa
        aa += 1
        logger.debug(f"{aa} Received '{action}' action.")

        match action:
            case ActionValue.BIND:
                self.__action_bind_with_dict(obj)
            case ActionValue.SHOW:
                self.__action_show_with_dict(obj)
            case ActionValue.SHOW_ALL:
                self.__action_show_all_with_dict()
            case ActionValue.MOUNT:
                self.__action_mount_with_dict(obj)
            case ActionValue.UMOUNT:
                pass  # TODO: write umount routine
            case ActionValue.UNBIND:
                self.__action_unbind_with_dict(obj)


def daemon_start(server_address: str, verbose: bool) -> NoReturn:
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    with socketserver.UnixStreamServer(server_address, UNIXDaemonHandler) as server:
        logger.info(f"The daemon is now listening at '{server_address}'.")
        server.serve_forever()
