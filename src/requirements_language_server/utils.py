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
from .tree_sitter_lsp import Finder
from .tree_sitter_lsp.diagnose import (
    count_level,
    diagnostics2linter_messages,
    get_diagnostics,
)
from .tree_sitter_lsp.finders import ErrorFinder, MissingFinder
from .tree_sitter_lsp.format import apply_text_edits

FINDERS = [
    ErrorFinder(),
    MissingFinder(),
    InvalidPackageFinder(),
    InvalidPathFinder(),
    RepeatedPackageFinder(),
    UnsortedRequirementFinder(),
]


def check(
    paths: list[str],
    color: Literal["auto", "always", "never"] = "auto",
    finders: list[Finder] | None = None,
) -> int:
    count = 0
    lines = []
    if finders is None:
        finders = FINDERS
    for path in paths:
        with open(path) as f:
            src = f.read()
        tree = requirements.parse(src)
        diagnostics = get_diagnostics(finders, path, tree)
        count += count_level(diagnostics)
        lines += diagnostics2linter_messages(path, diagnostics, color)
    print("\n".join(lines))
    return count


def format(paths: list[str]) -> None:
    for path in paths:
        finder = UnsortedRequirementFinder(path)
        with open(path, "r") as f:
            src = f.read()
        tree = requirements.parse(src)
        finder.find_all(path, tree)
        text_edits = finder.get_text_edits()
        src = apply_text_edits(text_edits, src)
        with open(path, "w") as f:
            f.write(src)
