"""The mount table exceptions module."""

from unionfs.exceptions import UnionFSError


class MountTableError(UnionFSError):
    """MountTable base error."""


class MountTableAlreadyExistError(MountTableError):
    """MountTable any value already exist error."""


class MountTableNotExistError(MountTableError):
    """MountTable any value not exist error."""


class MountTableValueError(MountTableError):
    """MountTable value error."""


class MountTableEmptyError(MountTableError):
    """MountTable empty error."""


class MountTableNoMountPointError(MountTableError):
    """MountTable empty error."""
