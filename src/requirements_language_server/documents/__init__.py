import json
import os

from .. import CACHE


def get_documents() -> dict[str, str]:
    r"""Get documents.

    :rtype: dict[str, str]
    """
    documents = {}
    if os.path.exists(CACHE):
        with open(CACHE, "r") as f:
            documents: dict[str, str] = json.load(f)
    return documents
