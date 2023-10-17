r"""Server
==========
"""
from typing import Any

import tree_sitter_requirements as requirements
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
from pip_cache import get_package_names
from pygls.server import LanguageServer

from . import NOT_FOUND, TEMPLATE
from .documents import get_documents
from .documents.option import OPTIONS, OPTIONS_WITH_EQUAL
from .finders import InvalidPackageFinder, RepeatedPackageFinder
from .tree_sitter_lsp.complete import get_completion_list_by_uri
from .tree_sitter_lsp.diagnose import get_diagnostics
from .tree_sitter_lsp.finders import PositionFinder, TypeFinder
from .utils import DIAGNOSTICS_FINDERS, FORMATTING_FINDER


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
        self.trees = {}

        @self.feature(INITIALIZE)
        def initialize(params: InitializeParams) -> None:
            r"""Initialize.

            :param params:
            :type params: InitializeParams
            :rtype: None
            """
            opts = params.initialization_options
            self.template = getattr(opts, "template", TEMPLATE)
            self.documents = get_documents()

        @self.feature(TEXT_DOCUMENT_DID_OPEN)
        @self.feature(TEXT_DOCUMENT_DID_CHANGE)
        def did_change(params: DidChangeTextDocumentParams) -> None:
            r"""Did change.

            :param params:
            :type params: DidChangeTextDocumentParams
            :rtype: None
            """
            document = self.workspace.get_document(params.text_document.uri)
            self.trees[document.uri] = requirements.parse(document.source)
            diagnostics = get_diagnostics(
                DIAGNOSTICS_FINDERS,
                document.uri,
                self.trees[document.uri],
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
            finder = FORMATTING_FINDER
            finder.find_all(document.uri, self.trees[document.uri])
            return finder.get_text_edits()

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
            r"""Hover.

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
                doc = self.documents.get(text, NOT_FOUND)
                # if cache is outdated
                if doc == NOT_FOUND:
                    from .documents.package import search_document

                    doc = search_document(text, TEMPLATE)
                if not doc:
                    return None
                return Hover(
                    MarkupContent(MarkupKind.Markdown, doc),
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
            uni = PositionFinder(params.position).find(
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
                            x,
                            kind=CompletionItemKind.Module,
                            # even if cache is outdated,
                            # we still don't find because it is too slow
                            documentation=MarkupContent(
                                kind=MarkupKind.Markdown,
                                value=self.documents.get(x, NOT_FOUND),
                            ),
                            insert_text=x,
                        )
                        for x in get_package_names(text)
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
                            documentation=OPTIONS_WITH_EQUAL[x],
                            insert_text=x,
                        )
                        for x in OPTIONS_WITH_EQUAL
                        if x.startswith(text)
                    ],
                )
            document = self.workspace.get_document(params.text_document.uri)
            return get_completion_list_by_uri(document.uri, text, "*.txt")
