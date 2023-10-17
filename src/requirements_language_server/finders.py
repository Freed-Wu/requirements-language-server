from lsprotocol.types import DiagnosticSeverity
from pip_cache import get_package_names

from .tree_sitter_lsp import UNI, Finder
from .tree_sitter_lsp.finders import (
    NonExistentFinder,
    RepeatedFinder,
    UnsortedFinder,
)


class InvalidPackageFinder(Finder):
    def __init__(
        self,
        message: str = "{{uni.get_text()}}: no such package",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        super().__init__(message, severity)

    def __call__(self, uni: UNI) -> bool:
        text = uni.get_text()
        return uni.node.type == "package" and text not in get_package_names(
            text
        )


class InvalidPathFinder(NonExistentFinder):
    def __init__(
        self,
        message: str = "{{uni.get_text()}}: no such package",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        super().__init__(message, severity)

    def __call__(self, uni: UNI) -> bool:
        return uni.node.type == "path" and self.is_non_existent(uni)


class RepeatedPackageFinder(RepeatedFinder):
    def __init__(
        self,
        message: str = "{{uni.get_text()}}: is repeated on {{_uni}}",
        severity: DiagnosticSeverity = DiagnosticSeverity.Warning,
    ) -> None:
        super().__init__(message, severity)

    def filter(self, uni: UNI) -> bool:
        return uni.node.type == "package"


class UnsortedRequirementFinder(UnsortedFinder):
    def __init__(
        self,
        message: str = "{{uni.get_text()}}: is unsorted due to {{_uni}}",
        severity: DiagnosticSeverity = DiagnosticSeverity.Warning,
    ) -> None:
        super().__init__(message, severity)

    def filter(self, uni: UNI) -> bool:
        return uni.node.type == "requirement"
