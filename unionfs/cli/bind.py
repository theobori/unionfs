"""The UnionFS CLI bind subcommand"""

from argparse import _SubParsersAction, ArgumentParser


def create_subparser_bind(
    subparsers: "_SubParsersAction[ArgumentParser]",
) -> ArgumentParser:
    """Creating a subparser for the UnionFS bind subcommand.

    Returns:
        ArgumentParser: The created parser.
    """

    parser = subparsers.add_parser("bind", help="Bind a directory to another.")

    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument(
        "-r",
        "--replace",
        action="store_true",
    )
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

    return parser
