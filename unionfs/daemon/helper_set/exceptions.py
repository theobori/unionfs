"""The helper set exceptions module."""

from typing import Optional


class HelperSetError(Exception):
    """HelperSet base error."""

    def __init__(self, message: Optional[str] = None):
        self.__message = message

    def __str__(self) -> str:
        return "An error occured." if self.__message is None else self.__message


class HelperSetEmptyError(HelperSetError):
    """HelperSet empty data error."""


class HelperSetNotExistError(HelperSetError):
    """HelperSet value does not exist error."""
