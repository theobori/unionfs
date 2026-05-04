"""The UnionFS CLI unbind subcommand"""

from argparse import _SubParsersAction, ArgumentParser
from pathlib import Path
import sys
from typing import NoReturn

from unionfs.common.bind import InsertType
from unionfs.daemon.daemon import DAEMON_UNIX_SOCKET_PATH
from unionfs.exceptions import UnionFSError
from unionfs.protocol.specification.action.unbind import client_unbind


def create_subparser_unbind(
    subparsers: "_SubParsersAction[ArgumentParser]",
) -> ArgumentParser:
    """Creating a subparser for the UnionFS unbind subcommand.

    Returns:
        ArgumentParser: The created parser.
    """

    parser = subparsers.add_parser("unbind", help="unbind a directory to another.")

    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument(
        "-u",
        "--unix_socket_path",
        required=False,
        default=Path(DAEMON_UNIX_SOCKET_PATH),
        type=Path,
    )

    return parser


def cli_unbind(source: Path, destination: Path, unix_socket_path: Path) -> NoReturn:
    try:
        client_unbind(unix_socket_path, source, destination)
    except UnionFSError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    print(f"Succesfully unbound '{source.absolute()}' to '{destination.absolute()}'.")
