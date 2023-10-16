from copy import deepcopy
from urllib.parse import unquote, urlparse

from jinja2 import Template
from lsprotocol.types import Diagnostic, DiagnosticSeverity, Position, Range
from tree_sitter import Node, Tree, TreeCursor


class Finder:
    def __init__(
        self,
        source: str = "",
        message: str = "",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        self.source = source
        self.message = message
        self.severity = severity

    def __call__(self, node: Node) -> bool:
        return True

    def __and__(self, second: "Finder") -> "Finder":
        finder = deepcopy(self)
        finder.__call__ = lambda node: self(node) and second(node)
        return finder

    def __or__(self, second: "Finder") -> "Finder":
        finder = deepcopy(self)
        finder.__call__ = lambda node: self(node) or second(node)
        return finder

    def __minus__(self, second: "Finder") -> "Finder":
        finder = deepcopy(self)
        finder.__call__ = lambda node: self(node) and not second(node)
        return finder

    def move_cursor(self, cursor: TreeCursor) -> bool:
        while self(cursor.node) is False:
            if cursor.node.child_count > 0:
                cursor.goto_first_child()
                continue
            while cursor.node.next_sibling is None:
                cursor.goto_parent()
                # when cannot find new nodes, return
                if cursor.node.parent is None:
                    return False
            cursor.goto_next_sibling()
        return True

    def reset(self):
        pass

    def find(self, tree: Tree) -> Node | None:
        self.reset()
        cursor = tree.walk()
        if self.move_cursor(cursor):
            return cursor.node
        else:
            return None

    def find_all(self, tree: Tree) -> list[Node]:
        self.reset()
        cursor = tree.walk()
        nodes = []
        while True:
            if self.move_cursor(cursor):
                nodes += [cursor.node]
            while cursor.node.next_sibling is None:
                cursor.goto_parent()
                # when cannot find new nodes, return
                if cursor.node.parent is None:
                    return nodes
            cursor.goto_next_sibling()

    def find_node(self, node: Node) -> Node | None:
        return node

    def nodes2diagnostics(self, nodes: list[Node]) -> list[Diagnostic]:
        return [
            Diagnostic(
                range=Range(
                    Position(node.start_point[0], node.start_point[1]),
                    Position(node.end_point[0], node.end_point[1]),
                ),
                source=self.source,
                message=Template(self.message).render(
                    node=node,
                    _node=self.find_node(node),
                ),
                severity=self.severity,
            )
            for node in nodes
        ]

    @staticmethod
    def node2range(node: Node) -> Range:
        return Range(Position(*node.start_point), Position(*node.end_point))

    @staticmethod
    def uri2path(uri: str) -> str:
        return unquote(urlparse(uri).path)

    @staticmethod
    def get_text(node: Node) -> str:
        return node.text.decode()
