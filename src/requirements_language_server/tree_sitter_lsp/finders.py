import os

from lsprotocol.types import (
    DiagnosticSeverity,
    Location,
    Position,
    Range,
    TextEdit,
)
from tree_sitter import Node

from . import Finder


class MissingFinder(Finder):
    def __init__(
        self,
        source: str = "",
        message: str = "missing",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        super().__init__(source, message, severity)

    def __call__(self, node: Node) -> bool:
        return node.child_count == 0 and node.is_missing


class ErrorFinder(Finder):
    def __init__(
        self,
        source: str = "",
        message: str = "syntax error",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        super().__init__(source, message, severity)

    def __call__(self, node: Node) -> bool:
        return node.child_count == 0 and node.has_error


class TypeFinder(Finder):
    def __init__(
        self,
        _type: str,
        source: str = "",
        message: str = "{{node.text.decode()}} belongs {{node.type}}",
        severity: DiagnosticSeverity = DiagnosticSeverity.Information,
    ) -> None:
        super().__init__(source, message, severity)
        self.type = _type

    def __call__(self, node: Node) -> bool:
        return node.type == self.type


class NonExistFinder(Finder):
    def __init__(
        self,
        uri: str,
        source: str = "",
        message: str = "{{node.text.decode()}}: no such file",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        super().__init__(source, message, severity)
        self.path = self.uri2path(uri)

    def get_path(self, path) -> str:
        return os.path.join(os.path.dirname(self.path), path)

    def __call__(self, node: Node) -> bool:
        return not os.path.exists(self.get_path(self.get_text(node)))


class RepeatedFinder(Finder):
    def __init__(
        self,
        uri: str,
        source: str = "",
        message: str = "{{node.text.decode()}} is repeated in {{_node.start_point[0] + 1}}:{{_node.start_point[1] + 1}}-{{_node.end_point[0] + 1}}:{{_node.end_point[1]}}",
        severity: DiagnosticSeverity = DiagnosticSeverity.Warning,
    ) -> None:
        super().__init__(source, message, severity)
        self.uri = uri
        self.nodes = []
        self.node_pairs = []

    def reset(self):
        self.nodes = []
        self.node_pairs = []

    def filter(self, node: Node) -> bool:
        return True

    def compare(self, node: Node, _node: Node) -> bool:
        return node.text == _node.text

    def find_node(self, node: Node) -> Node | None:
        for _node in self.nodes:
            if self.compare(node, _node):
                self.node_pairs += [[node, _node]]
                return _node
        if self.filter(node):
            self.nodes += [node]
        return None

    def __call__(self, node: Node) -> bool:
        if self.filter(node) is False:
            return False
        return self.find_node(node) is not None

    def get_definitions(self, node: Node) -> list[Location]:
        for node_, _node in self.node_pairs:
            # cache hit
            if node == node_:
                return [Location(self.uri, self.node2range(_node))]
        return []

    def get_references(self, node: Node) -> list[Location]:
        locations = []
        for node_, _node in self.node_pairs:
            # cache hit
            if node == _node:
                locations += [Location(self.uri, self.node2range(node_))]
        return locations

    def get_text_edits(self) -> list[TextEdit]:
        edits = []
        for node, _node in self.node_pairs:
            # swap 2 nodes
            edits += [
                TextEdit(self.node2range(node), _node.text.decode()),
                TextEdit(self.node2range(_node), node.text.decode()),
            ]
        return edits


class UnsortedFinder(RepeatedFinder):
    def __init__(
        self,
        uri: str,
        source: str = "",
        message: str = "{{node.text.decode()}} is unsorted due to {{_node.text.decode()}}@{{_node.start_point[0] + 1}}:{{_node.start_point[1] + 1}}-{{_node.end_point[0] + 1}}:{{_node.end_point[1]}}",
        severity: DiagnosticSeverity = DiagnosticSeverity.Warning,
    ) -> None:
        super().__init__(uri, source, message, severity)

    def compare(self, node: Node, _node: Node) -> bool:
        return node.text < _node.text


class PositionFinder(Finder):
    def __init__(
        self,
        position: Position,
        source: str = "",
        message: str = "",
        severity: DiagnosticSeverity = DiagnosticSeverity.Information,
    ) -> None:
        super().__init__(source, message, severity)
        self.position = position

    @staticmethod
    def belong(position: Position, node: Node) -> bool:
        return (
            Position(*node.start_point)
            <= position
            <= Position(*node.end_point)
        )

    def __call__(self, node: Node) -> bool:
        return node.child_count == 0 and self.belong(self.position, node)


class RangeFinder(Finder):
    def __init__(
        self,
        range: Range,
        source: str = "",
        message: str = "",
        severity: DiagnosticSeverity = DiagnosticSeverity.Information,
    ) -> None:
        super().__init__(source, message, severity)
        self.range = range

    @staticmethod
    def equal(range: Range, node: Node) -> bool:
        return range.start == Position(
            *node.start_point
        ) and range.end == Position(*node.end_point)

    def __call__(self, node: Node) -> bool:
        return self.equal(self.range, node)
