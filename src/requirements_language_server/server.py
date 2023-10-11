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
    Position,
    Range,
    TextDocumentPositionParams,
    TextEdit,
)
from pip_cache import get_package_names
from pygls.server import LanguageServer

from . import NOT_FOUND, TEMPLATE
from .documents import get_documents
from .documents.option import OPTIONS, OPTIONS_WITH_EQUAL
from .finders import (
    InvalidPackageFinder,
    InvalidPathFinder,
    RepeatedPackageFinder,
    UnsortedRequirementFinder,
)
from .tree_sitter_lsp.complete import get_completion_list_by_uri
from .tree_sitter_lsp.diagnose import get_diagnostics
from .tree_sitter_lsp.finders import (
    ErrorFinder,
    MissingFinder,
    PositionFinder,
    TypeFinder,
)

node2range = ErrorFinder.node2range


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
        self.tree = requirements.parse("")

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
            self.tree = requirements.parse(document.source)
            diagnostics = get_diagnostics(
                [
                    UnsortedRequirementFinder(document.uri),
                    RepeatedPackageFinder(document.uri),
                    ErrorFinder(),
                    MissingFinder(),
                    InvalidPackageFinder(),
                    InvalidPathFinder(document.uri),
                ],
                self.tree,
            )
            self.publish_diagnostics(params.text_document.uri, diagnostics)

        @self.feature(TEXT_DOCUMENT_FORMATTING)
        def format(params: DocumentFormattingParams) -> list[TextEdit]:
            document = self.workspace.get_document(params.text_document.uri)
            finder = UnsortedRequirementFinder(document.uri)
            finder.find_all(self.tree)
            return finder.get_text_edits()

        @self.feature(TEXT_DOCUMENT_DEFINITION)
        def definition(params: TextDocumentPositionParams) -> list[Location]:
            node = PositionFinder(params.position).find(self.tree)
            if node is None:
                return []
            document = self.workspace.get_document(params.text_document.uri)
            finder = RepeatedPackageFinder(document.uri)
            finder.find_all(self.tree)
            return finder.get_definitions(node)

        @self.feature(TEXT_DOCUMENT_REFERENCES)
        def references(params: TextDocumentPositionParams) -> list[Location]:
            node = PositionFinder(params.position).find(self.tree)
            if node is None:
                return []
            document = self.workspace.get_document(params.text_document.uri)
            finder = RepeatedPackageFinder(document.uri)
            finder.find_all(self.tree)
            return finder.get_references(node)

        @self.feature(TEXT_DOCUMENT_DOCUMENT_LINK)
        def document_link(params: DocumentLinkParams) -> list[DocumentLink]:
            document = self.workspace.get_document(params.text_document.uri)
            return [
                DocumentLink(
                    node2range(node),
                    f"https://pypi.org/project/{node.text.decode()}",
                )
                for node in TypeFinder("package").find_all(self.tree)
            ]

        @self.feature(TEXT_DOCUMENT_HOVER)
        def hover(params: TextDocumentPositionParams) -> Hover | None:
            r"""Hover.

            :param params:
            :type params: TextDocumentPositionParams
            :rtype: Hover | None
            """
            node = PositionFinder(params.position).find(self.tree)
            if node is None:
                return None
            text = node.text.decode()
            if node.type == "option":
                return Hover(
                    MarkupContent(
                        kind=MarkupKind.PlainText, value=OPTIONS.get(text, "")
                    ),
                    node2range(node),
                )
            if node.type == "package":
                doc = self.documents.get(text, NOT_FOUND)
                # if cache is outdated
                if doc == NOT_FOUND:
                    from .documents.package import search_document

                    doc = search_document(text, TEMPLATE)
                if not doc:
                    return None
                return Hover(
                    MarkupContent(kind=MarkupKind.Markdown, value=doc),
                    node2range(node),
                )

        @self.feature(TEXT_DOCUMENT_COMPLETION)
        def completions(params: CompletionParams) -> CompletionList:
            r"""Completions.

            :param params:
            :type params: CompletionParams
            :rtype: CompletionList
            """
            node = PositionFinder(params.position).find(self.tree)
            if node is None:
                return CompletionList(False, [])
            text = node.text.decode()

            if node.type == "package":
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
            # node.type != "option" due to incomplete
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
