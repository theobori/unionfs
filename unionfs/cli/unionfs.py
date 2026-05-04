"""The UnionFS CLI module."""

import sys

from argparse import ArgumentParser
from typing import NoReturn

from unionfs.cli.bind import create_subparser_bind, cli_bind
from unionfs.cli.daemon import create_subparser_daemon, cli_daemon


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
    create_subparser_daemon(subparsers)

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
            cli_daemon(args.unix_socket)
        case "bind":
            cli_bind(
                args.source,
                args.destination,
                args.after,
                args.before,
                args.unix_socket,
            )
        case "list":
            pass
        case _:
            print(f"The subcommand {subparser_name} is invalid.", file=sys.stderr)
            sys.exit(1)
