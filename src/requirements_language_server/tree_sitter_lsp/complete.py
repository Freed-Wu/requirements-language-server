from glob import glob
import os
from pathlib import Path
from . import Finder

from lsprotocol.types import (
    CompletionList,
    CompletionItem,
    CompletionItemKind,
)


def get_completion_list_by_uri(
    uri: str, text: str = "", expr: str = "*"
) -> CompletionList:
    dirname = os.path.dirname(Finder.uri2path(uri))
    return CompletionList(
        False,
        [
            CompletionItem(
                x.rpartition(dirname + os.path.sep)[-1],
                kind=CompletionItemKind.File
                if os.path.isfile(x)
                else CompletionItemKind.Folder,
                documentation=Path(x).read_text()
                if os.path.isfile(x)
                else "\n".join(os.listdir(x)),
                insert_text=x.rpartition(dirname + os.path.sep)[-1],
            )
            for x in [
                file + ("" if os.path.isfile(file) else os.path.sep)
                for file in glob(
                    os.path.join(dirname, text + f"**{os.path.sep}" + expr),
                    recursive=True,
                )
            ]
        ],
    )
