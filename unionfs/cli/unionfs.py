"""The UnionFS CLI module."""

from argparse import ArgumentParser
from typing import NoReturn

from unionfs.cli.bind import create_subparser_bind
from unionfs.cli.daemon import create_subparser_daemon


def cli_unionfs() -> NoReturn:
    """The UnionFS CLI exposing the filesystem to FUSE.

    Returns:
        NoReturn: It returns nothing.
    """

    parser = ArgumentParser(
        description="The UnionFS CLI exposing the filesystem to FUSE."
    )

    subparsers = parser.add_subparsers(help="subcommand help")
    create_subparser_bind(subparsers)
    create_subparser_daemon(subparsers)

    parser.parse_args()
