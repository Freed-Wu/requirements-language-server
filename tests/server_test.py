r"""Test server"""
import os

from requirements_language_server.server import diagnostic


class Test:
    r"""Test."""

    @staticmethod
    def test_diagnostic() -> None:
        r"""Test diagnostic.

        :rtype: None
        """
        assert diagnostic(
            os.path.join(os.path.dirname(__file__), "requirements.txt.in")
        ) == {2: "Could not find a version that matches autopep7"}
