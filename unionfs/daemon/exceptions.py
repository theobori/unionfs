"""The mount table exceptions module."""

from typing import Optional


class MountTableError(Exception):
    """MountTable base error."""

    def __init__(self, message: Optional[str] = None):
        self.__message = message

    def __str__(self) -> str:
        return "An error occured." if self.__message is None else self.__message


class MountTableAlreadyExistError(MountTableError):
    """MountTable any value already exist error."""


class MountTableNotExistError(MountTableError):
    """MountTable any value not exist error."""


class MountTableValueError(MountTableError):
    """MountTable value error."""


class MountTableEmptyError(MountTableError):
    """MountTable empty error."""
