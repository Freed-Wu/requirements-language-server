r"""Server
==========
"""
import json
import os
import re
from pathlib import Path
from typing import Any, Tuple

from lsprotocol.types import (
    INITIALIZE,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_HOVER,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    Diagnostic,
    DidChangeTextDocumentParams,
    Hover,
    InitializeParams,
    MarkupContent,
    MarkupKind,
    Position,
    Range,
    TextDocumentPositionParams,
)
from pip._internal.commands import create_command
from pip._internal.req import InstallRequirement
from pip_cache import get_package_names
from piptools._compat import parse_requirements
from piptools.cache import DependencyCache
from piptools.exceptions import NoCandidateFound
from piptools.repositories.pypi import PyPIRepository
from piptools.resolver import LegacyResolver
from platformdirs import user_cache_dir
from pygls.server import LanguageServer

from . import CACHE, NOT_FOUND, TEMPLATE, WHITELIST

OPTIONS = dict(
    filter(
        lambda x: x[0].rstrip("=") in WHITELIST,
        sum(
            [
                list(
                    zip(
                        opt._short_opts
                        + [
                            long_opt + ("=" if opt.nargs else "")
                            for long_opt in opt._long_opts
                        ],
                        len(opt._short_opts + opt._long_opts) * [opt.help],
                    )
                )
                for opt in create_command("install").parser.option_list_all
            ],
            [],
        ),
    )
)


def get_document() -> dict[str, str]:
    r"""Get document.

    :rtype: dict[str, str]
    """
    documents = {}
    if os.path.exists(CACHE):
        with open(CACHE, "r") as f:
            documents: dict[str, str] = json.load(f)
    return documents


def diagnostic(uri: str) -> dict[int, str]:
    r"""Diagnostic.

    :param uri:
    :type uri: str
    :rtype: dict[int, str]
    """
    results = {}
    cache = user_cache_dir("pip-tools")
    repo = PyPIRepository(["--use-deprecated", "legacy-resolver"], cache)
    resolver = LegacyResolver(
        parse_requirements(uri, repo.session), {}, repo, DependencyCache(cache)
    )
    try:
        resolver.resolve()
    except NoCandidateFound as e:
        ireq = e.ireq
        while isinstance(ireq.comes_from, InstallRequirement):
            ireq = getattr(ireq, "comes_from")
        if not isinstance(ireq.comes_from, str):
            return results
        line = int(ireq.comes_from.split(" ")[-1].rsplit(")")[0])
        results = {
            line - 1: f"Could not find a version that matches {ireq.name}",
        }
    return results


class RequirementsLanguageServer(LanguageServer):
    r"""Requirements language server."""

    def __init__(self, *args: Any) -> None:
        r"""Init.

        :param args:
        :type args: Any
        :rtype: None
        """
        super().__init__(*args)
        self.template = ""
        self.documents = {}

        @self.feature(INITIALIZE)
        def initialize(params: InitializeParams) -> None:
            r"""Initialize.

            :param params:
            :type params: InitializeParams
            :rtype: None
            """
            opts = params.initialization_options
            self.template = getattr(opts, "template", TEMPLATE)
            self.documents = get_document()

        @self.feature(TEXT_DOCUMENT_HOVER)
        def hover(params: TextDocumentPositionParams) -> Hover | None:
            r"""Hover.

            :param params:
            :type params: TextDocumentPositionParams
            :rtype: Hover | None
            """
            word = self._cursor_word(
                params.text_document.uri, params.position, True
            )
            if not word:
                return None
            if word[0].startswith("-"):
                help = OPTIONS.get(word[0], OPTIONS.get(word[0] + "="))
                if not help:
                    return None
                return Hover(
                    contents=MarkupContent(
                        kind=MarkupKind.PlainText, value=help
                    ),
                    range=word[1],
                )
            doc = self.documents.get(word[0], NOT_FOUND)
            # if cache is outdated
            if doc == NOT_FOUND:
                from .api import search_document

                doc = search_document(word[0], TEMPLATE)
            if not doc:
                return None
            return Hover(
                contents=MarkupContent(kind=MarkupKind.Markdown, value=doc),
                range=word[1],
            )

        @self.feature(
            TEXT_DOCUMENT_COMPLETION,
        )
        def completions(params: CompletionParams) -> CompletionList:
            r"""Completions.

            :param params:
            :type params: CompletionParams
            :rtype: CompletionList
            """
            line = self._cursor_line(
                params.text_document.uri, params.position
            ).strip()
            for cmd in ["-r", "--requirement=", "-c", "--constraint="]:
                if not line.startswith(cmd):
                    continue
                items = [
                    CompletionItem(
                        label=x,
                        kind=CompletionItemKind.File,
                        documentation=Path(x).read_text()
                        if os.path.isfile(x)
                        else "\n".join(os.listdir(x)),
                        insert_text=x,
                    )
                    for x in os.listdir(".")
                ]
                return CompletionList(is_incomplete=False, items=items)
            word = self._cursor_word(
                params.text_document.uri, params.position, False
            )
            token = "" if word is None else word[0]
            if token.startswith("-"):
                items = [
                    CompletionItem(
                        label=x,
                        kind=CompletionItemKind.Keyword,
                        documentation=OPTIONS[x],
                        insert_text=x,
                    )
                    for x in OPTIONS
                    if x.startswith(token)
                ]
            else:
                items = [
                    CompletionItem(
                        label=x,
                        kind=CompletionItemKind.Module,
                        # even if cache is outdated,
                        # we still don't find because it is too slow
                        documentation=MarkupContent(
                            kind=MarkupKind.Markdown,
                            value=self.documents.get(x, NOT_FOUND),
                        ),
                        insert_text=x,
                    )
                    for x in get_package_names(token)
                ]
            return CompletionList(is_incomplete=False, items=items)

        @self.feature(TEXT_DOCUMENT_DID_OPEN)
        @self.feature(TEXT_DOCUMENT_DID_CHANGE)
        def did_change(params: DidChangeTextDocumentParams) -> None:
            r"""Did change. Only work for requirements.txt.in.

            :param params:
            :type params: DidChangeTextDocumentParams
            :rtype: None
            """
            if params.text_document.uri.split(os.path.extsep)[-1] != "in":
                return None
            text_doc = self.workspace.get_document(params.text_document.uri)
            source = text_doc.source
            diagnostics = [
                Diagnostic(
                    range=Range(
                        Position(line, 0),
                        Position(line, len(source.splitlines()[line])),
                    ),
                    message=msg,
                    source="pip-compile",
                )
                for line, msg in diagnostic(params.text_document.uri).items()
            ]
            self.publish_diagnostics(text_doc.uri, diagnostics)

    def _cursor_line(self, uri: str, position: Position) -> str:
        r"""Cursor line.

        :param uri:
        :type uri: str
        :param position:
        :type position: Position
        :rtype: str
        """
        doc = self.workspace.get_document(uri)
        content = doc.source
        line = content.split("\n")[position.line]
        return str(line)

    def _cursor_word(
        self, uri: str, position: Position, include_all: bool = True
    ) -> Tuple[str, Range] | None:
        r"""Cursor word.

        :param uri:
        :type uri: str
        :param position:
        :type position: Position
        :param include_all:
        :type include_all: bool
        :rtype: Tuple[str, Range] | None
        """
        line = self._cursor_line(uri, position)
        cursor = position.character
        for m in re.finditer(r"[\w-]+", line):
            end = m.end() if include_all else cursor
            if m.start() <= cursor <= m.end():
                word = (
                    line[m.start() : end],
                    Range(
                        start=Position(
                            line=position.line, character=m.start()
                        ),
                        end=Position(line=position.line, character=end),
                    ),
                )
                return word
        return None
