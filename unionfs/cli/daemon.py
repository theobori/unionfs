"""The UnionFS CLI daemon subcommand"""

import socketserver
import logging

from argparse import _SubParsersAction, ArgumentParser
from pathlib import Path
from typing import NoReturn

from unionfs.daemon import DAEMON_UNIX_SOCKET_PATH, UNIXDaemonHandler
from unionfs.daemon.daemon import daemon_start

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


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
        "--unix_socket_path",
        required=False,
        default=Path(DAEMON_UNIX_SOCKET_PATH),
        type=Path,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
    )

    return parser


def cli_daemon(unix_socket_path: Path, verbose: bool) -> NoReturn:
    """Start the UnionFS daemon

    Args:
        unix_socket_path (Path): The unix_socket_path where the daemon will listen to.

    Returns:
        NoReturn: It returns nothing.
    """

    # TODO Remove the unix socket file when programs is killed

    server_address = str(unix_socket_path.absolute())

    daemon_start(server_address, verbose)
