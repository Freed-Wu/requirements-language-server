r"""Finders
===========
"""
import tree_sitter_requirements as requirements
from lsprotocol.types import DiagnosticSeverity
from pip_cache import get_package_names
from tree_sitter import Node, Tree

from .tree_sitter_lsp import UNI, Finder
from .tree_sitter_lsp.finders import (
    NotFileFinder,
    RepeatedFinder,
    UnsortedFinder,
)


class InvalidPackageFinder(Finder):
    r"""Invalidpackagefinder."""

    def __init__(
        self,
        message: str = "{{uni.get_text()}}: no such package",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        r"""Init.

        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        super().__init__(message, severity)

    def __call__(self, uni: UNI) -> bool:
        r"""Call.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        text = uni.get_text()
        return uni.node.type == "package" and text not in get_package_names(
            text
        )


class InvalidPathFinder(NotFileFinder):
    r"""Invalidpathfinder."""

    def __init__(
        self,
        message: str = "{{uni.get_text()}}: no such file",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        r"""Init.

        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        super().__init__(message, severity)

    def __call__(self, uni: UNI) -> bool:
        r"""Call.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        return uni.node.type == "path" and not self.is_file(uni)


class RepeatedPackageFinder(RepeatedFinder):
    r"""Repeatedpackagefinder."""

    def __init__(
        self,
        message: str = "{{uni.get_text()}}: is repeated on {{_uni}}",
        severity: DiagnosticSeverity = DiagnosticSeverity.Warning,
    ) -> None:
        r"""Init.

        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        super().__init__(message, severity)

    def is_include_node(self, node: Node) -> bool:
        r"""Is include node.

        :param node:
        :type node: Node
        :rtype: bool
        """
        return node.type == "path"

    def parse(self, code: bytes) -> Tree:
        r"""Parse.

        :param code:
        :type code: bytes
        :rtype: Tree
        """
        return requirements.parse(code)

    def filter(self, uni: UNI) -> bool:
        r"""Filter.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        return uni.node.type == "package"


class UnsortedRequirementFinder(UnsortedFinder):
    r"""Unsortedrequirementfinder."""

    def __init__(
        self,
        message: str = "{{uni.get_text()}}: is unsorted due to {{_uni}}",
        severity: DiagnosticSeverity = DiagnosticSeverity.Warning,
    ) -> None:
        r"""Init.

        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        super().__init__(message, severity)

    def filter(self, uni: UNI) -> bool:
        r"""Filter.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        return uni.node.type == "requirement"
