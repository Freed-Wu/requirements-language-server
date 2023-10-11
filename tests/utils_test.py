r"""Test utils"""
import os

from requirements_language_server.utils import check


class Test:
    r"""Test."""

    @staticmethod
    def test_check() -> None:
        r"""Test check.

        :rtype: None
        """
        result = check(
            [os.path.join(os.path.dirname(__file__), "requirements.txt.in")]
        )
        assert result == 6
