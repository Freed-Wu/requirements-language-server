r"""This module can be called by
`python -m <https://docs.python.org/3/library/__main__.html>`_.
"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime

from . import __name__ as NAME
from . import __version__

try:
    import shtab
except ImportError:
    from . import _shtab as shtab

NAME = NAME.replace("_", "-")
VERSION = rf"""{NAME} {__version__}
Copyright (C) {datetime.now().year}
Written by Wu, Zhenyu
"""
EPILOG = """
Report bugs to <wuzhenyu@ustc.edu>.
"""


def get_parser() -> ArgumentParser:
    r"""Get a parser for unit test."""
    parser = ArgumentParser(
        epilog=EPILOG,
        formatter_class=RawDescriptionHelpFormatter,
    )
    shtab.add_argument_to(parser)
    parser.add_argument("--version", version=VERSION, action="version")
    parser.add_argument(
        "--color",
        choices=["auto", "always", "never"],
        default="auto",
        help="when to display color",
    )
    parser.add_argument(
        "--check",
        nargs="*",
        default={},
        help="check file's errors and warnings",
    ).complete = shtab.FILE  # type: ignore
    parser.add_argument(
        "--format",
        nargs="*",
        default={},
        help="format files",
    ).complete = shtab.FILE  # type: ignore
    return parser


def main() -> None:
    r"""Parse arguments and provide shell completions."""
    args = get_parser().parse_args()

    from lsp_tree_sitter.diagnose import check
    from lsp_tree_sitter.format import format
    from tree_sitter_requirements import parse

    from .finders import DIAGNOSTICS_FINDER_CLASSES, FORMATTING_FINDER_CLASSES
    from .utils import get_filetype

    if args.format or args.check:
        format(args.format, parse, FORMATTING_FINDER_CLASSES, get_filetype)  # type: ignore
        exit(
            check(
                args.check,
                parse,
                DIAGNOSTICS_FINDER_CLASSES,
                get_filetype,
                args.color,
            )
        )

    from .server import RequirementsLanguageServer

    RequirementsLanguageServer(NAME, __version__).start_io()


if __name__ == "__main__":
    main()
