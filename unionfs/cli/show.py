"""The UnionFS CLI list subcommand"""

import sys

from argparse import _SubParsersAction, ArgumentParser
from pathlib import Path
from typing import Dict, List, NoReturn, Optional, Union

from unionfs.daemon import DAEMON_UNIX_SOCKET_PATH
from unionfs.protocol.specification.action.show import client_show, client_show_all


def create_subparser_show(
    subparsers: "_SubParsersAction[ArgumentParser]",
) -> ArgumentParser:
    """Creating a subparser for the UnionFS show subcommand.

    Returns:
        ArgumentParser: The created parser.
    """

    parser = subparsers.add_parser("show", help="Show the UnionFS mount table.")

    parser.add_argument(
        "--root",
        required=False,
        default=None,
        type=Path,
    )
    parser.add_argument(
        "-u",
        "--unix_socket_path",
        required=False,
        default=Path(DAEMON_UNIX_SOCKET_PATH),
        type=Path,
    )

    return parser


def cli_show_with_root(root: Path, destinations: List[str]) -> None:
    root_str = str(root.absolute())

    if len(destinations) == 0:
        print(f"The mountpoint '{root_str}' has no binding.")
        return

    for destination in destinations:
        print(f"'{root_str}' -> {destination}")


def cli_show_without_root(table: Dict[str, str]) -> None:
    if len(table) == 0:
        print("The mount table is empty.")
        return

    for source, destinations in table.items():
        for destination in destinations:
            print(f"'{source}' -> '{destination}'")


def cli_show(root: Optional[Path], unix_socket_path: Path) -> NoReturn:
    """Show binding in the mountable

    Args:
        unix_socket_path (Path): The unix_socket_path exposing the mount table.

    Returns:
        None: It returns nothing.
    """

    obj: Union[List[str], Dict[str, str]]
    try:
        if root:
            obj = client_show(unix_socket_path, root)
        else:
            obj = client_show_all(unix_socket_path)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    if root:
        cli_show_with_root(root, obj)
    else:
        cli_show_without_root(obj)
