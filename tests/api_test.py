r"""Test api"""
from requirements_language_server import NOT_FOUND
from requirements_language_server.api import search_document


class Test:
    r"""Test."""

    @staticmethod
    def test_get_document() -> None:
        r"""Test get document.

        :rtype: None
        """
        assert search_document("pip", "") != NOT_FOUND
        assert search_document("", "") == NOT_FOUND
