import os
from copy import deepcopy
from typing import Any
from urllib.parse import unquote, urlparse

from jinja2 import Template
from lsprotocol.types import (
    Diagnostic,
    DiagnosticSeverity,
    DocumentLink,
    Location,
    Position,
    Range,
    TextEdit,
)
from tree_sitter import Node, Tree, TreeCursor


class UNI:
    def __init__(self, uri: str, node: Node) -> None:
        self.uri = uri
        self.node = node

    def __repr__(self) -> str:
        return f"{self.get_text()}@{self.uri}:{self.node.start_point[0] + 1}:{self.node.start_point[1] + 1}-{self.node.end_point[0] + 1}:{self.node.end_point[1]}"

    def __eq__(self, that: "UNI") -> bool:
        return self.node == that.node

    def get_text(self) -> str:
        return self.node2text(self.node)

    @staticmethod
    def node2text(node: Node) -> str:
        return node.text.decode()

    def get_location(self) -> Location:
        return Location(self.uri, self.get_range())

    def get_range(self) -> Range:
        return self.node2range(self.node)

    @staticmethod
    def node2range(node: Node) -> Range:
        return Range(Position(*node.start_point), Position(*node.end_point))

    def get_path(self) -> str:
        return self.uri2path(self.uri)

    @staticmethod
    def uri2path(uri: str) -> str:
        return unquote(urlparse(uri).path)

    def get_diagnostic(
        self,
        message: str,
        severity: DiagnosticSeverity,
        **kwargs: Any,
    ) -> Diagnostic:
        _range = self.get_range()
        _range.end.character -= 1
        return Diagnostic(
            _range,
            Template(message).render(uni=self, **kwargs),
            severity,
        )

    def get_text_edit(self, new_text: str) -> TextEdit:
        return TextEdit(self.get_range(), new_text)

    def get_document_link(self, target: str, **kwargs) -> DocumentLink:
        return DocumentLink(
            self.get_range(),
            Template(target).render(uni=self, **kwargs),
        )

    @staticmethod
    def join(path, text) -> str:
        return os.path.join(os.path.dirname(path), text)


class Finder:
    def __init__(
        self,
        message: str = "",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        self.level = 0
        self.message = message
        self.severity = severity
        self.reset()

    def __call__(self, uni: UNI) -> bool:
        return True

    def __and__(self, second: "Finder") -> "Finder":
        finder = deepcopy(self)
        finder.__call__ = lambda uni: self(uni) and second(uni)
        return finder

    def __or__(self, second: "Finder") -> "Finder":
        finder = deepcopy(self)
        finder.__call__ = lambda uni: self(uni) or second(uni)
        return finder

    def __minus__(self, second: "Finder") -> "Finder":
        finder = deepcopy(self)
        finder.__call__ = lambda uni: self(uni) and not second(uni)
        return finder

    def is_include_node(self, node: Node) -> bool:
        return False

    def parse(self, code: bytes) -> Tree:
        raise NotImplementedError

    def uri2tree(self, uri: str) -> Tree:
        with open(UNI.uri2path(uri), "b") as f:
            code = f.read()
        return self.parse(code)

    def node2uri(self, node: Node) -> str:
        return node.text.decode()

    def move_cursor(
        self, uri: str, cursor: TreeCursor, is_all: bool = False
    ) -> str:
        while self(UNI(uri, cursor.node)) is False:
            if self.is_include_node(cursor.node):
                self.level += 1
                old_uri = uri
                uri = self.node2uri(cursor.node)
                tree = self.uri2tree(uri)
                if is_all:
                    self.find_all(uri, tree)
                else:
                    self.find(uri, tree)
                uri = old_uri
                self.level -= 1
            if cursor.node.child_count > 0:
                cursor.goto_first_child()
                continue
            while cursor.node.next_sibling is None:
                cursor.goto_parent()
                # when cannot find new nodes, return
                if cursor.node.parent is None:
                    return ""
            cursor.goto_next_sibling()
        return uri

    def reset(self) -> None:
        pass

    def find(self, uri: str, tree: Tree | None = None) -> UNI | None:
        self.reset()
        if tree is None:
            tree = self.uri2tree(uri)
        cursor = tree.walk()
        if uri := self.move_cursor(uri, cursor, False):
            return UNI(uri, cursor.node)
        else:
            return None

    def find_all(self, uri: str, tree: Tree | None = None) -> list[UNI]:
        self.reset()
        if tree is None:
            tree = self.uri2tree(uri)
        cursor = tree.walk()
        unis = []
        while True:
            if uri := self.move_cursor(uri, cursor, True):
                unis += [UNI(uri, cursor.node)]
            while cursor.node.next_sibling is None:
                cursor.goto_parent()
                # when cannot find new nodes, return
                if cursor.node.parent is None:
                    return unis
            cursor.goto_next_sibling()

    def uni2diagnostic(self, uni: UNI) -> Diagnostic:
        return uni.get_diagnostic(self.message, self.severity)

    def unis2diagnostics(self, unis: list[UNI]) -> list[Diagnostic]:
        return [self.uni2diagnostic(uni) for uni in unis]
