import os

from requirements_language_server.server import (
    RequirementsLanguageServer as Server,
)

server = Server("")
file = os.path.join(os.path.dirname(__file__), "requirements.txt.in")


class Test:
    @staticmethod
    def test_check() -> None:
        diagnostics = server.lint(file)[file]
        assert len(diagnostics)

    @staticmethod
    def test_searcher() -> None:
        assert server.searcher.installed != {}
