"""The UnionFS CLI module."""

import sys

from argparse import ArgumentParser
from typing import NoReturn

from unionfs.cli.bind import create_subparser_bind, cli_bind
from unionfs.cli.unbind import create_subparser_unbind, cli_unbind
from unionfs.cli.daemon import create_subparser_daemon, cli_daemon
from unionfs.cli.mount import create_subparser_mount, cli_mount
from unionfs.cli.show import create_subparser_show, cli_show


def create_parser_unionfs() -> ArgumentParser:
    """Create the UnionFS CLI argument parser

    Returns:
        ArgumentParser: The CLI argument parser.
    """

    parser = ArgumentParser(
        description="The UnionFS CLI exposing the filesystem to FUSE."
    )

    subparsers = parser.add_subparsers(help="subcommand help", dest="subparser_name")
    create_subparser_bind(subparsers)
    create_subparser_unbind(subparsers)
    create_subparser_daemon(subparsers)
    create_subparser_mount(subparsers)
    create_subparser_show(subparsers)

    return parser


def cli_unionfs() -> NoReturn:
    """The UnionFS CLI exposing the filesystem to FUSE.

    Returns:
        NoReturn: It returns nothing.
    """

    parser = create_parser_unionfs()
    args = parser.parse_args()

    subparser_name = args.subparser_name
    match subparser_name:
        case "daemon":
            cli_daemon(args.unix_socket_path, args.verbose)
        case "bind":
            cli_bind(
                args.source,
                args.destination,
                args.after,
                args.before,
                args.unix_socket_path,
            )
        case "unbind":
            cli_unbind(args.source, args.destination, args.unix_socket_path)
        case "mount":
            cli_mount(args.root, args.unix_socket_path)
        case "show":
            cli_show(args.root, args.unix_socket_path)
        case _:
            print(f"The subcommand {subparser_name} is invalid.", file=sys.stderr)
            sys.exit(1)
