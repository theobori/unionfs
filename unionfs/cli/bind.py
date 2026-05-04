"""The UnionFS CLI bind subcommand"""

from argparse import _SubParsersAction, ArgumentParser
from pathlib import Path
import sys
from typing import Any, NoReturn

from unionfs.common.bind import InsertType
from unionfs.daemon.daemon import DAEMON_UNIX_SOCKET_PATH

from unionfs.client import client_send_and_recv_obj


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
        "--unix_socket",
        required=False,
        default=Path(DAEMON_UNIX_SOCKET_PATH),
        type=Path,
    )

    return parser


def cli_bind(
    source: Path, destination: Path, after: bool, before: bool, unix_socket: Path
) -> NoReturn:
    insert_type: InsertType
    if after:
        insert_type = InsertType.AFTER
    elif before:
        insert_type = InsertType.BEFORE
    else:
        print("At least one insert type is required.", file=sys.stderr)
        sys.exit(1)

    status: str
    value: Any
    try:
        status, value = client_send_and_recv_obj(
            unix_socket,
            {
                "action": "bind",
                "source": source.absolute().name,
                "destination": destination.absolute().name,
                "insert_type": insert_type.value,
            },
        )
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    match status:
        case "success":
            print(f"Successfully bound '{source}' to '{destination}'.")
        case "error":
            print(value)
            # handle each error, some should cause exit 1
        case _:
            print("Unknown status", file=sys.stderr)
            sys.exit(1)
