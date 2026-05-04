"""The UnionFS CLI daemon subcommand"""

from argparse import _SubParsersAction, ArgumentParser
from pathlib import Path
import socketserver
from typing import NoReturn

from unionfs.daemon import DAEMON_UNIX_SOCKET_PATH, UNIXDaemonHandler


def create_subparser_daemon(
    subparsers: "_SubParsersAction[ArgumentParser]",
) -> ArgumentParser:
    """Creating a subparser for the UnionFS daemon subcommand.

    Returns:
        ArgumentParser: The created parser.
    """

    parser = subparsers.add_parser("daemon", help="Start the UnionFS daemon.")

    parser.add_argument(
        "-u",
        "--unix_socket",
        required=False,
        default=Path(DAEMON_UNIX_SOCKET_PATH),
        type=Path,
    )

    return parser


def cli_daemon(unix_socket: Path) -> NoReturn:
    """Start the UnionFS daemon

    Args:
        unix_socket (Path): The unix_socket where the daemon will listen to.

    Returns:
        NoReturn: It returns nothing.
    """

    with socketserver.UnixStreamServer(
        unix_socket.absolute().name, UNIXDaemonHandler
    ) as server:
        server.serve_forever()
