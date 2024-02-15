r"""Utils
=========
"""

import os
from typing import Literal

from tree_sitter.binding import Query
from tree_sitter_requirements._core import _language

from . import FILETYPE

QUERIES = {}


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
        QUERIES[name] = _language.query(text)
    return QUERIES[name]


def get_filetype(name: str) -> FILETYPE | Literal[""]:
    r"""Get filetype.

    :param name:
    :type name: str
    :rtype: FILETYPE | Literal[""]
    """
    return "pip"
