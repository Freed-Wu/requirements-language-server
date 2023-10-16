from lsprotocol.types import DiagnosticSeverity
from pip_cache import get_package_names
from tree_sitter import Node

from . import __name__ as NAME
from .tree_sitter_lsp.finders import (
    NonExistFinder,
    RepeatedFinder,
    TypeFinder,
    UnsortedFinder,
)


class InvalidPackageFinder(TypeFinder):
    def __init__(
        self,
        source: str = NAME,
        message: str = "{{node.text.decode()}}: no such package",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        super().__init__("package", source, message, severity)

    def __call__(self, node: Node) -> bool:
        text = node.text.decode()
        return TypeFinder.__call__(
            self, node
        ) and text not in get_package_names(text)


class InvalidPathFinder(TypeFinder, NonExistFinder):
    def __init__(
        self,
        uri: str,
        source: str = NAME,
        message: str = "{{node.text.decode()}}: no such file",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        TypeFinder.__init__(self, "path", source, message, severity)
        NonExistFinder.__init__(self, uri, source, message, severity)

    def __call__(self, node: Node) -> bool:
        return TypeFinder.__call__(self, node) and NonExistFinder.__call__(
            self, node
        )


class RepeatedPackageFinder(RepeatedFinder):
    def __init__(
        self,
        uri: str,
        source: str = NAME,
        message: str = "{{node.text.decode()}} is repeated in {{_node.start_point[0] + 1}}:{{_node.start_point[1] + 1}}-{{_node.end_point[0] + 1}}:{{_node.end_point[1]}}",
        severity: DiagnosticSeverity = DiagnosticSeverity.Warning,
    ) -> None:
        super().__init__(uri, source, message, severity)

    def filter(self, node: Node) -> bool:
        return node.type == "package"


class UnsortedRequirementFinder(UnsortedFinder):
    def __init__(
        self,
        uri: str,
        source: str = NAME,
        message: str = "{{node.text.decode()}} is unsorted due to {{_node.text.decode()}}@{{_node.start_point[0] + 1}}:{{_node.start_point[1] + 1}}-{{_node.end_point[0] + 1}}:{{_node.end_point[1]}}",
        severity: DiagnosticSeverity = DiagnosticSeverity.Warning,
    ) -> None:
        super().__init__(uri, source, message, severity)

    def filter(self, node: Node) -> bool:
        return node.type == "requirement"
