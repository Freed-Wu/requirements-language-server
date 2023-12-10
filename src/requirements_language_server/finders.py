r"""Finders
===========
"""
import os
from dataclasses import dataclass
from typing import Any, Literal

import tree_sitter_requirements as requirements
from lsprotocol.types import Diagnostic, DiagnosticSeverity
from tree_sitter import Node, Tree
from tree_sitter_lsp import UNI
from tree_sitter_lsp.finders import (
    ErrorFinder,
    QueryFinder,
    RepeatedFinder,
    TypeFinder,
    UnsortedFinder,
)
from tree_sitter_requirements._core import _language

from . import FILETYPE
from .packages import get_pkginfos
from .utils import get_query


@dataclass(init=False)
class ErrorRequirementsFinder(ErrorFinder):
    r"""Errorrequirementsfinder."""

    def __init__(
        self,
        message: str = "{{uni.get_text()}}: error",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        r"""Init.

        :param filetype:
        :type filetype: str
        :param message:
        :type message: str
        :param severity:
        :type severity: DiagnosticSeverity
        :rtype: None
        """
        super().__init__(_language, message, severity)


@dataclass(init=False)
class InvalidPackageFinder(QueryFinder):
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
        query = get_query("package")
        super().__init__(query, message, severity)

    def capture2uni(self, capture: tuple[Node, str], uri: str) -> UNI | None:
        r"""Capture2uni.

        :param capture:
        :type capture: tuple[Node, str]
        :param uri:
        :type uri: str
        :rtype: UNI | None
        """
        node, _ = capture
        uni = UNI(uri, node)
        text = uni.get_text()
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
        query = get_query("path")
        super().__init__(query, message, severity)

    @staticmethod
    def get_option_type(option: str) -> Literal["file", "dir"]:
        r"""Get option type.

        :param option:
        :type option: str
        :rtype: Literal["file", "dir"]
        """
        if option in ["-e", "--editable"]:
            return "dir"
        return "file"

    def captures2unis(
        self, captures: list[tuple[Node, str]], uri: str
    ) -> list[UNI]:
        r"""Captures2unis.

        :param captures:
        :type captures: list[tuple[Node, str]]
        :param uri:
        :type uri: str
        :rtype: list[UNI]
        """
        kind = "file"
        unis = []
        for capture in captures:
            node, label = capture
            uni = UNI(uri, node)
            if label == "option":
                kind = self.get_option_type(uni.get_text())
                continue
            path = self.uni2path(uni)
            if (
                kind == "file"
                and not os.path.isfile(path)
                or kind == "dir"
                and not os.path.isdir(path)
            ):
                unis += [uni]
        return unis

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
                option = UNI.node2text(children[0])
        return option

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
        filetype: FILETYPE = "pip",
        message: str = "{{uni.get_text()}}: is repeated on {{_uni}}",
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


FORMATTING_FINDER_CLASSES = [UnsortedRequirementFinder]


DIAGNOSTICS_FINDER_CLASSES = [
    ErrorRequirementsFinder,
    InvalidPackageFinder,
    InvalidPathFinder,
    RepeatedPackageFinder,
    OptionFinder,
    UnsortedRequirementFinder,
]
