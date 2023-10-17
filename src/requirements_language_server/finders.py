r"""Finders
===========
"""
import os
from typing import Literal

import tree_sitter_requirements as requirements
from lsprotocol.types import Diagnostic, DiagnosticSeverity
from pip_cache import get_package_names
from tree_sitter import Node, Tree

from .tree_sitter_lsp import UNI, Finder
from .tree_sitter_lsp.finders import RepeatedFinder, UnsortedFinder


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


class InvalidPathFinder(Finder):
    r"""Invalidpathfinder."""

    def __init__(
        self,
        message: str = "{{uni.get_text()}}: no such {{_type}}",
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

    @staticmethod
    def get_option(uni: UNI) -> str:
        r"""Get option.

        :param uni:
        :type uni: UNI
        :rtype: str
        """
        option = ""
        if children := getattr(uni.node.parent, "children", None):
            if len(children) > 0:
                option = children[0].text.decode()
        return option

    @staticmethod
    def get_option_type(option: str) -> Literal["file", "dir", ""]:
        r"""Get option type.

        :param option:
        :type option: str
        :rtype: Literal["file", "dir", ""]
        """
        if option in ["-r", "--requirement", "-c", "--constraint"]:
            return "file"
        if option in ["-e", "--editable"]:
            return "dir"
        return ""

    def __call__(self, uni: UNI) -> bool:
        r"""Call.

        :param uni:
        :type uni: UNI
        :rtype: bool
        """
        path = self.uni2path(uni)
        option = self.get_option(uni)
        return uni.node.type == "path" and not (
            os.path.isfile(path)
            and self.get_option_type(option) == "file"
            or os.path.isdir(path)
            and self.get_option_type(option) == "dir"
        )

    def uni2diagnostic(self, uni: UNI) -> Diagnostic:
        r"""Uni2diagnostic.

        :param uni:
        :type uni: UNI
        :rtype: Diagnostic
        """
        return uni.get_diagnostic(
            self.message,
            self.severity,
            _type=self.get_option_type(self.get_option(uni)),
        )


class RepeatedPackageFinder(RepeatedFinder):
    r"""Repeatedpackagefinder."""

    def __init__(
        self,
        pep508: bool = False,
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
        self.pep508 = pep508

    def is_include_node(self, node: Node) -> bool:
        r"""Is include node.

        :param node:
        :type node: Node
        :rtype: bool
        """
        return node.type == "path" and not self.pep508

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
