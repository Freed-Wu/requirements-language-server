import sys
from typing import Literal

from lsprotocol.types import Diagnostic, DiagnosticSeverity
from tree_sitter import Tree

from . import Finder


def get_diagnostics(finders: list[Finder], tree: Tree) -> list[Diagnostic]:
    return [
        diagnostic
        for finder in finders
        for diagnostic in finder.nodes2diagnostics(finder.find_all(tree))
    ]


def count_level(
    diagnostics: list[Diagnostic],
    level: DiagnosticSeverity = DiagnosticSeverity.Warning,
) -> int:
    return len(
        [
            diagnostic
            for diagnostic in diagnostics
            if diagnostic.severity and diagnostic.severity <= level
        ]
    )


class _Colorama:
    """Colorama."""

    def __getattribute__(self, _: str) -> str:
        """Getattribute.

        :param _:
        :type _: str
        :rtype: str
        """
        return ""


def diagnostics2linter_messages(
    path: str,
    diagnostics: list[Diagnostic],
    color: Literal["auto", "always", "never"] = "auto",
    colors: list[str] | None = None,
) -> list[str]:
    from colorama import Fore, init

    init()
    if not sys.stdout.isatty() and color == "auto" or color == "never":
        Fore = _Colorama()
    if colors is None:
        colors = [Fore.RESET, Fore.RED, Fore.YELLOW, Fore.BLUE, Fore.GREEN]
    return [
        f"{Fore.MAGENTA}{path}{Fore.RESET}:{Fore.CYAN}{diagnostic.range.start.line + 1}:{diagnostic.range.start.character + 1}{Fore.RESET}-{Fore.CYAN}{diagnostic.range.end.line + 1}:{diagnostic.range.end.character + 1}{Fore.RESET}:{colors[diagnostic.severity if diagnostic.severity else 0]}{str(diagnostic.severity).split('.')[-1].lower()}{Fore.RESET}: {diagnostic.message}"
        for diagnostic in diagnostics
    ]