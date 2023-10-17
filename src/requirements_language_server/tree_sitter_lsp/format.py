r"""Format
==========
"""
from lsprotocol.types import Position, Range, TextEdit


def position_2d_to_1d(source: str, position: Position) -> int:
    r"""Position 2d to 1d.

    :param source:
    :type source: str
    :param position:
    :type position: Position
    :rtype: int
    """
    return (
        sum(len(line) + 1 for line in source.splitlines()[: position.line])
        + position.character
    )


def range_2d_to_1d(source: str, region: Range) -> range:
    r"""Range 2d to 1d.

    :param source:
    :type source: str
    :param region:
    :type region: Range
    :rtype: range
    """
    return range(
        position_2d_to_1d(source, region.start),
        position_2d_to_1d(source, region.end),
    )


def apply_text_edits(text_edits: list[TextEdit], source: str) -> str:
    r"""Apply text edits.

    :param text_edits:
    :type text_edits: list[TextEdit]
    :param source:
    :type source: str
    :rtype: str
    """
    for text_edit in text_edits:
        region = range_2d_to_1d(source, text_edit.range)
        source = (
            source[: region.start] + text_edit.new_text + source[region.stop :]
        )
    return source
