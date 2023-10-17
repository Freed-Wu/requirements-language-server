import os

from lsprotocol.types import (
    Diagnostic,
    DiagnosticSeverity,
    Location,
    Position,
    Range,
    TextEdit,
)
from tree_sitter import Node

from . import UNI, Finder


class MissingFinder(Finder):
    def __init__(
        self,
        message: str = "{{uni.get_text()}}: missing",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        super().__init__(message, severity)

    def __call__(self, uni: UNI) -> bool:
        node = uni.node
        return node.child_count == 0 and node.is_missing


class ErrorFinder(Finder):
    def __init__(
        self,
        message: str = "{{uni.get_text()}}: error",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        super().__init__(message, severity)

    def __call__(self, uni: UNI) -> bool:
        node = uni.node
        return node.child_count == 0 and node.has_error


class NonExistentFinder(Finder):
    def __init__(
        self,
        message: str = "{{uni.get_text()}}: no such file or directory",
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    ) -> None:
        super().__init__(message, severity)

    def is_non_existent(self, uni: UNI) -> bool:
        path = uni.get_path()
        text = uni.get_text()
        return not os.path.exists(UNI.join(path, text))

    def __call__(self, uni: UNI) -> bool:
        return self.is_non_existent(uni)


class RepeatedFinder(Finder):
    def __init__(
        self,
        message: str = "{{uni.get_text()}}: is repeated on {{_uni}}",
        severity: DiagnosticSeverity = DiagnosticSeverity.Warning,
    ) -> None:
        super().__init__(message, severity)

    def reset(self) -> None:
        self.unis = []
        self.uni_pairs = []

    def filter(self, uni: UNI) -> bool:
        return True

    def compare(self, uni: UNI, _uni: UNI) -> bool:
        return uni.node.text == _uni.node.text

    def __call__(self, uni: UNI) -> bool:
        if self.filter(uni) is False:
            return False
        for _uni in self.unis:
            if self.compare(uni, _uni):
                self.uni_pairs += [[uni, _uni]]
                return True
        self.unis += [uni]
        return False

    def get_definitions(self, uni: UNI) -> list[Location]:
        for uni_, _uni in self.uni_pairs:
            # cache hit
            if uni == uni_:
                return [_uni.get_location()]
        return []

    def get_references(self, uni: UNI) -> list[Location]:
        locations = []
        for uni_, _uni in self.uni_pairs:
            # cache hit
            if uni == _uni:
                locations += [uni_.get_location()]
        return locations

    def get_text_edits(self) -> list[TextEdit]:
        edits = []
        for uni, _uni in self.uni_pairs:
            # swap 2 unis
            edits += [
                uni.get_text_edit(_uni.get_text()),
                _uni.get_text_edit(uni.get_text()),
            ]
        return edits

    def uni2diagnostic(self, uni: UNI) -> Diagnostic:
        for uni_, _uni in self.uni_pairs:
            if uni == uni_:
                return uni.get_diagnostic(
                    self.message, self.severity, _uni=_uni
                )
        return uni.get_diagnostic(self.message, self.severity)


class UnsortedFinder(RepeatedFinder):
    def __init__(
        self,
        message: str = "{{uni.get_text()}}: is unsorted due to {{_uni}}",
        severity: DiagnosticSeverity = DiagnosticSeverity.Warning,
    ) -> None:
        super().__init__(message, severity)

    def compare(self, uni: UNI, _uni: UNI) -> bool:
        return uni.node.text < _uni.node.text


class TypeFinder(Finder):
    def __init__(self, _type: str) -> None:
        super().__init__()
        self.type = _type

    def __call__(self, uni: UNI) -> bool:
        node = uni.node
        return node.type == self.type


class PositionFinder(Finder):
    def __init__(self, position: Position) -> None:
        super().__init__()
        self.position = position

    @staticmethod
    def belong(position: Position, node: Node) -> bool:
        return (
            Position(*node.start_point)
            <= position
            <= Position(*node.end_point)
        )

    def __call__(self, uni: UNI) -> bool:
        node = uni.node
        return node.child_count == 0 and self.belong(self.position, node)


class RangeFinder(Finder):
    def __init__(self, _range: Range) -> None:
        super().__init__()
        self.range = _range

    @staticmethod
    def equal(_range: Range, node: Node) -> bool:
        return _range.start == Position(
            *node.start_point
        ) and _range.end == Position(*node.end_point)

    def __call__(self, uni: UNI) -> bool:
        node = uni.node
        return self.equal(self.range, node)
