r"""Utils
=========
"""
from .finders import (
    InvalidPackageFinder,
    InvalidPathFinder,
    OptionFinder,
    RepeatedPackageFinder,
    UnsortedRequirementFinder,
)
from .tree_sitter_lsp.finders import ErrorFinder, MissingFinder

DIAGNOSTICS_FINDERS = [
    ErrorFinder(),
    MissingFinder(),
    InvalidPackageFinder(),
    InvalidPathFinder(),
    RepeatedPackageFinder(),
    UnsortedRequirementFinder(),
]
DIAGNOSTICS_FINDERS_PEP508 = [
    OptionFinder(),
    ErrorFinder(),
    MissingFinder(),
    InvalidPackageFinder(),
    InvalidPathFinder(),
    RepeatedPackageFinder(True),
    UnsortedRequirementFinder(),
]
FORMATTING_FINDER = UnsortedRequirementFinder()
