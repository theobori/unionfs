"""The fuse filsystem module."""

import errno
from functools import cache
import os
import socket
import stat
import threading
import time
import errno

import mfusepy as fuse

from pathlib import Path
from typing import Any, Callable, Dict, List, NoReturn, Optional, Tuple

from unionfs.protocol.client import receive_response
from unionfs.protocol.specification.action.action import ActionValue
from unionfs.protocol.specification.action.show import client_show
from unionfs.protocol.specification.status import StatusValue


def remove_slash_prefix(func):
    def wrapper(self, path: str, *args, **kwargs):
        if path is not None:
            path = path.lstrip("/")
        return func(self, path, *args, **kwargs)

    return wrapper


class UnionFilesystem(fuse.Operations):
    def __init__(self, root: Path, unix_socket_path: Path):
        self.__root = root.absolute()
        self.__unix_socket_path = unix_socket_path

    def __get_bound_directories(self) -> List[str]:
        directories: List[str]
        try:
            directories = client_show(self.__unix_socket_path, self.__root)
        except Exception as e:
            raise fuse.FuseOSError(errno.ENODATA)

        return directories

    def __get_first_exist_path(
        self, path: Path, ignore_exist: bool = False
    ) -> Optional[Path]:
        directories = self.__get_bound_directories()

        for directory in directories:
            new_path = Path(directory, path)
            if ignore_exist or new_path.exists():
                return new_path

        return None

    def __process_first_available_path(
        self,
        path: str,
        func: Callable,
        *args: Tuple[Any],
        ignore_exist: bool = False,
        **kwargs: Dict[str, Any],
    ) -> Any:
        first_path = self.__get_first_exist_path(path, ignore_exist=ignore_exist)
        if not ignore_exist and first_path is None:
            raise fuse.FuseOSError(errno.ENOENT)

        ans = func(first_path, *args, **kwargs)
        if ans is None:
            return 0

        return ans

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def chmod(self, path: str, mode: int) -> int:
        return self.__process_first_available_path(path, os.chmod, mode)

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def chown(self, path: str, uid: int, gid: int) -> int:
        return self.__process_first_available_path(path, os.chown, uid, gid)

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def create(self, path: str, mode: int, fi=None) -> int:
        # TODO: handle path is None
        return self.__process_first_available_path(
            path,
            os.open,
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            mode,
            ignore_exist=True,
        )

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def getattr(self, path: str, fh=None) -> dict[str, Any]:
        st: os.stat_result
        if fh is not None:
            st = os.fstat(fh)
        else:
            first_path = self.__get_first_exist_path(path)
            if first_path is not None:
                st = os.lstat(first_path)
            else:
                raise fuse.FuseOSError(errno.ENOENT)

        return {
            key.removesuffix("_ns"): getattr(st, key)
            for key in (
                "st_atime_ns",
                "st_ctime_ns",
                "st_gid",
                "st_mode",
                "st_mtime_ns",
                "st_nlink",
                "st_size",
                "st_uid",
            )
        }

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def mkdir(self, path: str, mode: int) -> int:
        return self.__process_first_available_path(path, os.mkdir, mode)

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def read(self, path: str, size: int, offset: int, fh: int) -> bytes:
        os.lseek(fh, offset, 0)
        return os.read(fh, size)

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def readdir(self, path: str, fh) -> fuse.ReadDirResult:
        ans = [".", ".."]

        directories = self.__get_bound_directories()
        for directory in directories:
            full_path = Path(directory, path)
            if full_path.exists():
                ans.extend(os.listdir(full_path))

        return ans

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def readlink(self, path: str) -> str:
        return self.__process_first_available_path(path, os.readlink)

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def rename(self, old: str, new: str) -> int:
        first_path = self.__get_first_exist_path(old)
        if first_path is None:
            raise fuse.FuseOSError(errno.ENOENT)

        os.rename(old, Path(first_path, new))

        return 0

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def rmdir(self, path: str) -> int:
        directories = self.__get_bound_directories()

        removed = False
        for directory in directories:
            full_path = Path(directory, path)
            if full_path.exists():
                os.rmdir(full_path)
                removed = True

        if removed is False:
            raise fuse.FuseOSError(errno.ENOENT)

        return 0

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def statfs(self, path: str) -> dict[str, int]:
        statvfs_result = self.__process_first_available_path(path, os.statvfs)

        return {
            key: getattr(statvfs_result, key)
            for key in (
                "f_bavail",
                "f_bfree",
                "f_blocks",
                "f_bsize",
                "f_favail",
                "f_ffree",
                "f_files",
                "f_flag",
                "f_frsize",
                "f_namemax",
            )
        }

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def symlink(self, target: str, source: str) -> int:
        return self.__process_first_available_path(source, os.symlink, target)

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def truncate(self, path: str, length: int, fh=None) -> int:
        first_path = self.__get_first_exist_path(path)
        if first_path is None:
            raise fuse.FuseOSError(errno.ENOENT)

        with open(first_path, "rb+") as f:
            f.truncate(length)

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def unlink(self, path: str) -> int:
        directories = self.__get_bound_directories()

        for directory in directories:
            full_path = Path(directory, path)
            if full_path.exists():
                os.unlink(full_path)

        return 0

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def utimens(self, path: str, times: Optional[Tuple[float, float]] = None) -> int:
        def helper(path: str) -> NoReturn:
            ns: Tuple[int, int]

            if times:
                ns = (
                    int(times[0]),
                    int(times[1]),
                )
            else:
                now = int(time.time() * 1e9)
                ns = (
                    now,
                    now,
                )

            os.utime(path, ns=ns)

        return self.__process_first_available_path(path, helper)

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def open(self, path: str, flags: int) -> int:
        return self.__process_first_available_path(path, os.open, flags)

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def release(self, path: str, fh: int) -> int:
        os.close(fh)

        return 0

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def mknod(self, path: str, mode: int, dev: int) -> int:
        first_path = self.__get_first_exist_path(path)
        if first_path is None:
            raise fuse.FuseOSError(errno.ENOENT)

        if stat.S_ISREG(mode):
            fd = os.open(
                first_path, os.O_CREAT | os.O_WRONLY | os.O_EXCL, mode & 0o7777
            )
            os.close(fd)
        else:
            os.mknod(first_path, mode, dev)

    @remove_slash_prefix
    @fuse.overrides(fuse.Operations)
    def write(self, path: str, data, offset: int, fh: int) -> int:
        os.lseek(fh, offset, 0)
        return os.write(fh, data)
