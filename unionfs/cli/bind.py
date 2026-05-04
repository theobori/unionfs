"""The UnionFS CLI bind subcommand"""

from argparse import _SubParsersAction, ArgumentParser
from pathlib import Path
import sys
from typing import NoReturn

from unionfs.common.bind import InsertType
from unionfs.daemon.daemon import DAEMON_UNIX_SOCKET_PATH
from unionfs.exceptions import UnionFSError
from unionfs.protocol.specification.action.bind import client_bind


def create_subparser_bind(
    subparsers: "_SubParsersAction[ArgumentParser]",
) -> ArgumentParser:
    """Creating a subparser for the UnionFS bind subcommand.

    Returns:
        ArgumentParser: The created parser.
    """

    parser = subparsers.add_parser("bind", help="Bind a directory to another.")

    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument(
        "-b",
        "--before",
        action="store_true",
    )
    parser.add_argument(
        "-a",
        "--after",
        action="store_true",
    )
    parser.add_argument(
        "-u",
        "--unix_socket_path",
        required=False,
        default=Path(DAEMON_UNIX_SOCKET_PATH),
        type=Path,
    )

    return parser


def cli_bind(
    source: Path, destination: Path, after: bool, before: bool, unix_socket_path: Path
) -> NoReturn:
    insert_type: InsertType
    if after:
        insert_type = InsertType.AFTER
    elif before:
        insert_type = InsertType.BEFORE
    else:
        print("At least one insert type is required.", file=sys.stderr)
        sys.exit(1)

    try:
        client_bind(unix_socket_path, source, destination, insert_type)
    except UnionFSError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    print(f"Succesfully bound '{source.absolute()}' to '{destination.absolute()}'.")
