r"""Finders
===========
"""

import os
from dataclasses import dataclass
from typing import Any, Literal

from lsp_tree_sitter import UNI
from lsp_tree_sitter.finders import (
    ErrorFinder,
    QueryFinder,
    RepeatedFinder,
    UnsortedFinder,
)
from lsprotocol.types import Diagnostic, DiagnosticSeverity
from tree_sitter import Node, Tree

from . import FILETYPE
from .packages import get_pkginfos
from .utils import get_query, parser


@dataclass(init=False)
class InvalidPackageFinder(QueryFinder):
    r"""Invalidpackagefinder."""

    def __init__(
        self,
        message: str = "{{uni.text}}: no such package",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        r"""Init.

        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        query = get_query("package")
        super().__init__(query, message, severity)

    def capture2uni(
        self, label: str, nodes: list[Node], uri: str
    ) -> UNI | None:
        r"""Capture2uni.

        :param self:
        :param label:
        :type label: str
        :param nodes:
        :type nodes: list[Node]
        :param uri:
        :type uri: str
        :rtype: UNI | None
        """
        uni = UNI(nodes[0], uri)
        text = uni.text
        return uni if text not in get_pkginfos() else None


@dataclass(init=False)
class OptionFinder(QueryFinder):
    r"""Optionfinder."""

    def __init__(
        self,
        filetype: FILETYPE,
        message: str = "setuptools only supports PEP508",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        r"""Init.

        :param filetype:
        :type filetype: FILETYPE
        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        query = get_query("option")
        super().__init__(query, message, severity)
        if filetype == "pip":
            self.find_all = self.fake_find_all

    def fake_find_all(self, *args: Any, **kwargs: Any) -> list:
        r"""Fake find all.

        :param args:
        :type args: Any
        :param kwargs:
        :type kwargs: Any
        :rtype: list
        """
        return []


@dataclass(init=False)
class InvalidPathFinder(QueryFinder):
    r"""Invalidpathfinder."""

    def __init__(
        self,
        message: str = "{{uni.text}}: no such {{_type}}",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        r"""Init.

        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        query = get_query("path")
        super().__init__(query, message, severity)
        self.paths = {"file": [], "dir": []}

    def captures2unis(
        self, captures: dict[str, list[Node]], uri: str
    ) -> list[UNI]:
        r"""Captures2unis.

        :param captures:
        :type captures: list[tuple[Node, str]]
        :param uri:
        :type uri: str
        :rtype: list[UNI]
        """
        unis = []
        for label, nodes in captures.items():
            uni = UNI(nodes[0], uri)
            path = uni.path
            if (
                label == "file"
                and not os.path.isfile(path)
                or label == "dir"
                and not os.path.isdir(path)
            ):
                unis += [uni]
                self.paths[label] += [uni]
        return unis

    def get_type(self, uni: UNI) -> Literal["file", "dir"]:
        r"""Get type.

        :param self:
        :param uni:
        :type uni: UNI
        :rtype: Literal["file", "dir"]
        """
        try:
            self.paths["file"].index(uni)
            return "file"
        except ValueError:
            return "dir"

    def uni2diagnostic(self, uni: UNI) -> Diagnostic:
        r"""Uni2diagnostic.

        :param uni:
        :type uni: UNI
        :rtype: Diagnostic
        """
        return uni.get_diagnostic(
            self.message,
            self.severity,
            _type=self.get_type(uni),
        )


class RepeatedPackageFinder(RepeatedFinder):
    r"""Repeatedpackagefinder."""

    def __init__(
        self,
        filetype: FILETYPE = "pip",
        message: str = "{{uni.text}}: is repeated on {{_uni}}",
        severity: DiagnosticSeverity = DiagnosticSeverity.Warning,
    ) -> None:
        r"""Init.

        :param self:
        :param pep508:
        :type pep508: bool
        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        super().__init__(message, severity)
        self.filetype = filetype

    def is_include_node(self, node: Node) -> bool:
        r"""Is include node.

        :param node:
        :type node: Node
        :rtype: bool
        """
        return node.type == "path" and self.filetype == "pip"

    def parse(self, code: bytes) -> Tree:
        r"""Parse.

        :param code:
        :type code: bytes
        :rtype: Tree
        """
        return parser.parse(code)

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
        message: str = "{{uni.text}}: is unsorted due to {{_uni}}",
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


FORMATTING_FINDER_CLASSES = [UnsortedRequirementFinder]


DIAGNOSTICS_FINDER_CLASSES = [
    ErrorFinder,
    InvalidPackageFinder,
    InvalidPathFinder,
    RepeatedPackageFinder,
    OptionFinder,
    UnsortedRequirementFinder,
]
