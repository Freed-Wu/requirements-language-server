r"""Utils
=========
"""

import os
from typing import Literal

from tree_sitter import Parser, Query
from tree_sitter_requirements._core import _language as language

from . import FILETYPE

SCHEMAS = {}
QUERIES = {}
parser = Parser()
parser.set_language(language)


def get_query(name: str) -> Query:
    r"""Get query.

    :param name:
    :type name: str
    :rtype: Query
    """
    if name not in QUERIES:
        with open(
            os.path.join(
                os.path.join(
                    os.path.join(os.path.dirname(__file__), "assets"),
                    "queries",
                ),
                f"{name}{os.path.extsep}scm",
            )
        ) as f:
            text = f.read()
        QUERIES[name] = language.query(text)
    return QUERIES[name]


def get_filetype(name: str) -> FILETYPE | Literal[""]:
    r"""Get filetype.

    :param name:
    :type name: str
    :rtype: FILETYPE | Literal[""]
    """
    return "pip"
