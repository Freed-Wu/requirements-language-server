r"""Diagnostics
===============
"""
import tree_sitter_requirements as requirements
from tree_sitter import Node


def diagnostic(source: str) -> list[tuple[Node, str, str]]:
    r"""Diagnostic.

    :param source:
    :type source: str
    :rtype: list[tuple[Node, str, str]]
    """
    results = []
    tree = requirements.parse(source)
    for node in tree.root_node.children:
        if node.type == "ERROR":
            results += [(node, "error", "Error")]
    return results
