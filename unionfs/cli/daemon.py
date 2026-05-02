"""The UnionFS CLI daemon subcommand"""

from argparse import _SubParsersAction, ArgumentParser
from pathlib import Path

from unionfs.daemon import DAEMON_UNIX_SOCKET_PATH


def create_subparser_daemon(
    subparsers: "_SubParsersAction[ArgumentParser]",
) -> ArgumentParser:
    """Creating a subparser for the UnionFS daemon subcommand.

    Returns:
        ArgumentParser: The created parser.
    """

    parser = subparsers.add_parser("daemon", help="Start the UnionFS daemon.")

    parser.add_argument(
        "--host",
        required=False,
        default=DAEMON_UNIX_SOCKET_PATH,
        type=Path,
    )

    return parser
