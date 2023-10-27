r"""Utils
=========
"""
from typing import Literal

from . import FILETYPE


def get_filetype(name: str) -> FILETYPE | Literal[""]:
    r"""Get filetype.

    :param name:
    :type name: str
    :rtype: FILETYPE | Literal[""]
    """
    return "pip"
