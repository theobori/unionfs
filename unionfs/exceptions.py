"""The UnioxFS exceptions module."""

"""The mount table exceptions module."""

from typing import Optional


class UnionFSError(Exception):
    """UnionFSError base error."""

    def __init__(self, message: Optional[str] = None):
        self.__message = message

    def __str__(self) -> str:
        return "An error occured." if self.__message is None else self.__message


class UnionFSValueError(UnionFSError):
    """UnionFSError value error."""
