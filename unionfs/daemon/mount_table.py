"""The FUSE union table module."""

from pathlib import Path
from typing import Dict
from collections import defaultdict

from typing import NoReturn

from unionfs.common.bind import InsertType
from unionfs.daemon.exceptions import (
    MountTableAlreadyExistError,
    MountTableNoMountPointError,
    MountTableNotExistError,
    MountTableValueError,
)
from unionfs.daemon.helper_set import HelperSet

type TableType[T] = Dict[T, HelperSet[T]]


class MountTable[T]:
    # TODO: check circular mount

    def __init__(self):
        self.__table: Dict[T, HelperSet[T]] = defaultdict(HelperSet[T])

    def create_bind(
        self, source: Path, destination: Path, insert_type: InsertType
    ) -> NoReturn:
        if not source in self.__table:
            raise MountTableNoMountPointError(f"There are no mountpoint for {source}")

        destinations = self.__table[source]

        if destination in destinations:
            raise MountTableAlreadyExistError(
                f"The bind '{source}' to '{destination}' already exists."
            )

        match insert_type:
            case InsertType.AFTER:
                destinations.push(destination)
            case InsertType.BEFORE:
                destinations.pushleft(destination)
            case _:
                raise MountTableValueError("Invalid insert type.")

        source_str = str(source)
        n = len(source_str)

        for k_source, v_destinations in self.__table.items():
            k_source_str = str(k_source)
            if len(k_source_str) > n and k_source_str.startswith(source_str):
                new_path = destination / k_source

                match insert_type:
                    case InsertType.AFTER:
                        v_destinations.push(new_path)
                    case InsertType.BEFORE:
                        v_destinations.pushleft(new_path)

    def remove_bind(self, source: Path, destination: Path) -> NoReturn:
        if not source in self.__table:
            raise MountTableNoMountPointError(f"There are no mountpoint for {source}")

        destinations = self.__table[source]

        if not destination in destinations:
            raise MountTableNotExistError(
                f"The bind '{source}' to '{destination}' does not exists."
            )

        destinations.remove(destination)

        n = len(str(destination))

        for k_source, k_destinations in self.__table.items():
            value = destination / k_source
            if len(str(value)) > n and value in k_destinations:
                k_destinations.remove(value)

    def get_bind(self, source: Path) -> HelperSet[T]:
        return self.__table[source]

    @property
    def table(self) -> TableType[T]:
        return self.__table

    @property
    def table_str(self) -> TableType[str]:
        return {
            str(source): [str(destination) for destination in destinations]
            for source, destinations in self.__table.items()
        }

    def mount_filesystem(self, root: Path) -> NoReturn:
        if root in self.__table:
            raise MountTableAlreadyExistError(
                f"The path {root} is already a mountpoint."
            )

        self.__table[root] = HelperSet[T]()
