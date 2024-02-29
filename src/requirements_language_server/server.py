r"""Server
==========
"""

import os
from typing import Any

import tree_sitter_requirements as requirements
from lsp_tree_sitter import UNI
from lsp_tree_sitter.complete import get_completion_list_by_uri
from lsp_tree_sitter.diagnose import get_diagnostics
from lsp_tree_sitter.finders import PositionFinder, TypeFinder
from lsp_tree_sitter.format import get_text_edits
from lsprotocol.types import (
    INITIALIZE,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DOCUMENT_LINK,
    TEXT_DOCUMENT_FORMATTING,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_REFERENCES,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    DidChangeTextDocumentParams,
    DocumentFormattingParams,
    DocumentLink,
    DocumentLinkParams,
    Hover,
    InitializeParams,
    Location,
    MarkupContent,
    MarkupKind,
    TextDocumentPositionParams,
    TextEdit,
)
from pygls.server import LanguageServer

from . import FILETYPE
from .finders import (
    DIAGNOSTICS_FINDER_CLASSES,
    FORMATTING_FINDER_CLASSES,
    InvalidPackageFinder,
    RepeatedPackageFinder,
)
from .misc.option import OPTIONS, OPTIONS_WITH_EQUAL
from .packages import get_pkginfos, render_document, update_pkginfos

try:
    import tomllib as tomli
except ImportError:
    import tomli


class RequirementsLanguageServer(LanguageServer):
    r"""Requirements language server."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        r"""Init.

        :param self:
        :param args:
        :type args: Any
        :param kwargs:
        :type kwargs: Any
        :rtype: None
        """
        super().__init__(*args, **kwargs)
        self.trees = {}

        @self.feature(INITIALIZE)
        async def initialize(params: InitializeParams) -> None:
            opts = params.initialization_options
            timeout = getattr(opts, "timeout", 3)
            await update_pkginfos(timeout)

        @self.feature(TEXT_DOCUMENT_DID_OPEN)
        @self.feature(TEXT_DOCUMENT_DID_CHANGE)
        def did_change(params: DidChangeTextDocumentParams) -> None:
            r"""Did change.

            :param params:
            :type params: DidChangeTextDocumentParams
            :rtype: None
            """
            filetype = self.get_filetype(params.text_document.uri)
            document = self.workspace.get_document(params.text_document.uri)
            self.trees[document.uri] = requirements.parse(document.source)
            diagnostics = get_diagnostics(
                document.uri,
                self.trees[document.uri],
                DIAGNOSTICS_FINDER_CLASSES,
                filetype,
            )
            self.publish_diagnostics(params.text_document.uri, diagnostics)

        @self.feature(TEXT_DOCUMENT_FORMATTING)
        def format(params: DocumentFormattingParams) -> list[TextEdit]:
            r"""Format.

            :param params:
            :type params: DocumentFormattingParams
            :rtype: list[TextEdit]
            """
            document = self.workspace.get_document(params.text_document.uri)
            return get_text_edits(
                document.uri,
                self.trees[document.uri],
                FORMATTING_FINDER_CLASSES,  # type: ignore
            )

        @self.feature(TEXT_DOCUMENT_DEFINITION)
        def definition(params: TextDocumentPositionParams) -> list[Location]:
            r"""Get definition.

            :param params:
            :type params: TextDocumentPositionParams
            :rtype: list[Location]
            """
            document = self.workspace.get_document(params.text_document.uri)
            uni = PositionFinder(params.position).find(
                document.uri, self.trees[document.uri]
            )
            if uni is None:
                return []
            finder = RepeatedPackageFinder()
            finder.find_all(document.uri, self.trees[document.uri])
            return finder.get_definitions(uni)

        @self.feature(TEXT_DOCUMENT_REFERENCES)
        def references(params: TextDocumentPositionParams) -> list[Location]:
            r"""Get references.

            :param params:
            :type params: TextDocumentPositionParams
            :rtype: list[Location]
            """
            document = self.workspace.get_document(params.text_document.uri)
            uni = PositionFinder(params.position).find(
                document.uri, self.trees[document.uri]
            )
            if uni is None:
                return []
            finder = RepeatedPackageFinder()
            finder.find_all(document.uri, self.trees[document.uri])
            return finder.get_references(uni)

        @self.feature(TEXT_DOCUMENT_DOCUMENT_LINK)
        def document_link(params: DocumentLinkParams) -> list[DocumentLink]:
            r"""Get document links.

            :param params:
            :type params: DocumentLinkParams
            :rtype: list[DocumentLink]
            """
            document = self.workspace.get_document(params.text_document.uri)
            finder = InvalidPackageFinder()
            return [
                uni.get_document_link(
                    "https://pypi.org/project/{{uni.get_text()}}"
                )
                for uni in TypeFinder("package").find_all(
                    document.uri, self.trees[document.uri]
                )
                if finder(uni) is False
            ]

        @self.feature(TEXT_DOCUMENT_HOVER)
        def hover(params: TextDocumentPositionParams) -> Hover | None:
            r"""Hover. ``render_document()`` is slow, so we use ``async``.

            :param params:
            :type params: TextDocumentPositionParams
            :rtype: Hover | None
            """
            document = self.workspace.get_document(params.text_document.uri)
            uni = PositionFinder(params.position).find(
                document.uri, self.trees[document.uri]
            )
            if uni is None:
                return None
            text = uni.get_text()
            if uni.node.type == "option":
                return Hover(
                    MarkupContent(MarkupKind.PlainText, OPTIONS.get(text, "")),
                    uni.get_range(),
                )
            if uni.node.type == "package":
                return Hover(
                    MarkupContent(MarkupKind.Markdown, render_document(text)),  # type: ignore
                    uni.get_range(),
                )

        @self.feature(TEXT_DOCUMENT_COMPLETION)
        def completions(params: CompletionParams) -> CompletionList:
            r"""Completions.

            :param params:
            :type params: CompletionParams
            :rtype: CompletionList
            """
            document = self.workspace.get_document(params.text_document.uri)
            uni = PositionFinder(params.position, right_equal=True).find(
                document.uri, self.trees[document.uri]
            )
            if uni is None:
                return CompletionList(False, [])
            text = uni.get_text()

            if uni.node.type == "package":
                return CompletionList(
                    False,
                    [
                        CompletionItem(
                            k,
                            kind=CompletionItemKind.Module,
                            documentation=MarkupContent(
                                MarkupKind.Markdown, doc
                            ),
                            insert_text=k,
                        )
                        for k, doc in get_pkginfos().items()
                        if k.startswith(text)
                    ],
                )
            # uni.node.type != "option" due to incomplete
            if text.startswith("-"):
                return CompletionList(
                    False,
                    [
                        CompletionItem(
                            x,
                            kind=CompletionItemKind.Keyword,
                            documentation=doc,
                            insert_text=x,
                        )
                        for x, doc in OPTIONS_WITH_EQUAL.items()
                        if x.startswith(text)
                    ],
                )
            document = self.workspace.get_document(params.text_document.uri)
            return get_completion_list_by_uri(
                text,
                document.uri,
                {"**/*.txt": "requirements", "*.txt": "requirements"},
            )

    def get_filetype(self, uri: str) -> FILETYPE:
        r"""Get filetype.

        :param uri:
        :type uri: str
        :rtype: FILETYPE
        """
        if self.workspace.root_uri is None:
            return "pip"
        pyproject_uri = os.path.join(self.workspace.root_uri, "pyproject.toml")
        document = self.workspace.get_document(pyproject_uri)
        pyproject_path = UNI.uri2path(document.uri)
        path = UNI.uri2path(uri)
        if path in self.get_dependencies_files(pyproject_path):
            return "pep508"
        return "pip"

    @staticmethod
    def get_dependencies_files(pyproject_path: str) -> list[str]:
        r"""Get dependencies files.

        :param pyproject_path:
        :type pyproject_path: str
        :rtype: list[str]
        """
        if not os.access(pyproject_path, os.R_OK):
            return []
        with open(pyproject_path, "rb") as f:
            data = tomli.load(f)
        dynamic = data.get("tool", {}).get("setuptools", {}).get("dynamic", {})
        files = []
        file = dynamic.get("dependencies", {}).get("file")
        if file:
            files += [
                os.path.abspath(
                    os.path.realpath(UNI.join(pyproject_path, file))
                )
            ]
        for value in dynamic.get("optional-dependencies", {}).values():
            file = value.get("file")
            if file:
                files += [
                    os.path.abspath(
                        os.path.realpath(UNI.join(pyproject_path, file))
                    )
                ]
        return files
