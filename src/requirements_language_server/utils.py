r"""Utils
=========
"""
from typing import Literal

import tree_sitter_requirements as requirements

from .finders import (
    InvalidPackageFinder,
    InvalidPathFinder,
    RepeatedPackageFinder,
    UnsortedRequirementFinder,
)
from .tree_sitter_lsp.diagnose import (
    count_level,
    diagnostics2linter_messages,
    get_diagnostics,
)
from .tree_sitter_lsp.finders import ErrorFinder, MissingFinder


def check(
    paths: list[str], color: Literal["auto", "always", "never"] = "auto"
) -> int:
    r"""Check.

    :param paths:
    :type paths: list[str]
    :param color:
    :type color: Literal["auto", "always", "never"]
    :rtype: int
    """
    count = 0
    lines = []
    for path in paths:
        finders = [
            ErrorFinder(),
            MissingFinder(),
            InvalidPackageFinder(),
            InvalidPathFinder(path),
            RepeatedPackageFinder(path),
            UnsortedRequirementFinder(path),
        ]
        with open(path) as f:
            src = f.read()
        tree = requirements.parse(src)
        diagnostics = get_diagnostics(finders, tree)
        count += count_level(diagnostics)
        lines += diagnostics2linter_messages(path, diagnostics, color)
    print("\n".join(lines))
    return count
