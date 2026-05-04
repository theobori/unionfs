"""The helper set exceptions module."""

from unionfs.exceptions import UnionFSError


class HelperSetError(UnionFSError):
    """HelperSet base error."""


class HelperSetEmptyError(HelperSetError):
    """HelperSet empty data error."""


class HelperSetNotExistError(HelperSetError):
    """HelperSet value does not exist error."""
