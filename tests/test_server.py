r"""Test server."""

import os

from requirements_language_server.server import RequirementsLanguageServer


class Test:
    r"""Test."""

    @staticmethod
    def test_get_dependencies_files() -> None:
        r"""Test get dependencies files.

        :rtype: None
        """
        result = RequirementsLanguageServer.get_dependencies_files(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "pyproject.toml"
            )
        )
        assert result != []
