"""The UnionFS CLI mount subcommand"""

import sys

import mfusepy as fuse

from argparse import _SubParsersAction, ArgumentParser
from pathlib import Path
from typing import NoReturn

from unionfs.daemon import DAEMON_UNIX_SOCKET_PATH
from unionfs.exceptions import UnionFSError
from unionfs.filesystem import UnionFilesystem
from unionfs.protocol.specification.action.mount import client_mount
from unionfs.protocol.specification.action.umount import client_umount


def create_subparser_mount(
    subparsers: "_SubParsersAction[ArgumentParser]",
) -> ArgumentParser:
    """Creating a subparser for the UnionFS mount subcommand.

    Returns:
        ArgumentParser: The created parser.
    """

    parser = subparsers.add_parser(
        "mount", help="Expose the UnionFS filesystem via FUSE."
    )

    parser.add_argument("root", type=Path)
    parser.add_argument(
        "-u",
        "--unix_socket_path",
        required=False,
        default=Path(DAEMON_UNIX_SOCKET_PATH),
        type=Path,
    )

    return parser


def cli_mount(root: Path, unix_socket_path: Path) -> NoReturn:
    """Expose UnionFS via FUSE

    Args:
        unix_socket_path (Path): The unix_socket_path exposing the mount table.

    Returns:
        NoReturn: It returns nothing.
    """

    absolute_root_path = root.absolute()

    try:
        client_mount(unix_socket_path, absolute_root_path)
    except UnionFSError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    unionfs = UnionFilesystem(absolute_root_path, unix_socket_path)

    fuse.FUSE(
        unionfs,
        str(absolute_root_path),
        foreground=False,
        auto_cache=True,
        attr_timeout=1.0,
        entry_timeout=1.0,
    )

    try:
        client_umount(unix_socket_path, absolute_root_path)
    except UnionFSError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
