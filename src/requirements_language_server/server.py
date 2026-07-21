r"""Server
==========
"""

import os

from lsp_tree_sitter.completer import PackageCompleter, SchemaCompleter
from lsp_tree_sitter.linter import PackageLinter, PathLinter
from lsp_tree_sitter.server import TreeSitterLanguageServer
from pip._internal.commands import create_command
from tree_sitter import Language, Parser
from tree_sitter_requirements import language as get_language_ptr
from tree_sitter_requirements import queries

from .searcher.pip import PipSearcher


class RequirementsLanguageServer(TreeSitterLanguageServer):
    def __init__(self, *args, **kwargs) -> None:
        parser = Parser()
        language = Language(get_language_ptr())
        parser.language = language

        path_linter = PathLinter.from_queries(language, queries, "markup.link")
        code_file = os.path.join(
            os.path.dirname(__file__), "assets", "jq", "main.jq"
        )
        self.options = self.get_options()

        def schema_gettter(path: str):
            return self.options

        schema_completer = SchemaCompleter.from_files(
            code_file, schema_gettter
        )
        self.searcher = PipSearcher()

        def searcher_getter(path: str) -> PipSearcher:
            return self.searcher

        query = PackageLinter.queries_to_query(
            language, queries, "highlights.scm"
        )
        package_linter = PackageLinter(query, searcher_getter)
        package_completer = PackageCompleter(searcher_getter)

        super().__init__(
            parser,
            (path_linter, package_linter),
            (schema_completer, package_completer),
            *args,
            **kwargs,
        )

    @staticmethod
    def get_options(
        whitelist: tuple[str, ...] = (
            "-i",
            "--index-url",
            "--extra-index-url",
            "--no-index",
            "-c",
            "--constraint",
            "-r",
            "--requirement",
            "-e",
            "--editable",
            "-f",
            "--find-links",
            "--no-binary",
            "--only-binary",
            "--prefer-binary",
            "--require-hashes",
            "--pre",
            "--trusted-host",
            "--use-feature",
            "--global-option",
            "--config-settings",
            "--hash",
        ),
    ):
        r"""https://pip.pypa.io/en/stable/reference/requirements-file-format/#supported-options"""
        return {
            opt
            + (
                "=" if option.nargs and opt in option._long_opts else ""
            ): option.help if option.help else ""
            for option in create_command("install").parser.option_list_all
            if (option._short_opts + option._long_opts)[0] in whitelist
            for opt in option._short_opts + option._long_opts
        }
