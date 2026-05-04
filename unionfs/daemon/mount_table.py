"""The FUSE union table module."""

from pathlib import Path
from typing import Dict, Optional
from collections import defaultdict

from typing import NoReturn

from unionfs.common.bind import InsertType
from unionfs.daemon.exceptions import (
    MountTableAlreadyExistError,
    MountTableNotExistError,
    MountTableValueError,
)
from unionfs.daemon.helper_set import HelperSet

type TableType[T] = Dict[T, HelperSet[T]]


class MountTable[T]:
    def __init__(self):
        self.__table: Dict[T, HelperSet[T]] = defaultdict(HelperSet[T])

    def create_bind(
        self, source_path: Path, destination_path: Path, insert_type: InsertType
    ) -> NoReturn:
        source_set = self.__table[source_path]

        if destination_path in source_set:
            raise MountTableAlreadyExistError(
                f"The bind '{source_path}' to '{destination_path}' already exists."
            )

        match insert_type:
            case InsertType.AFTER:
                source_set.push(destination_path)
            case InsertType.BEFORE:
                source_set.pushleft(destination_path)
            case _:
                raise MountTableValueError("Invalid insert type.")

        n = len(source_path.name)

        for source, destination in self.__table.items():
            if len(source.name) > n and source.name.startswith(source_path.name):
                new_path = destination_path / Path(source)

                match insert_type:
                    case InsertType.AFTER:
                        destination.push(new_path)
                    case InsertType.BEFORE:
                        destination.pushleft(new_path)

    def remove_bind(self, source_path: Path, destination_path: Path) -> NoReturn:
        source_set = self.__table[source_path]

        if not destination_path in source_set:
            raise MountTableNotExistError(
                f"The bind '{source_path}' to '{destination_path}' does not exists."
            )

        source_set.remove(destination_path)

        n = len(destination_path.name)

        for source, destination in self.__table.items():
            value = destination_path / source
            if len(value.name) > n and value in destination:
                destination.remove(value)

    def get_bind(self, source_path: Path) -> HelperSet[T]:
        return self.__table[source_path]

    @property
    def table(self) -> TableType[T]:
        return self.__table
