r"""Test package"""
from requirements_language_server.packages import search_document
from requirements_language_server.packages.pypi import NOT_FOUND


class Test:
    r"""Test."""

    @staticmethod
    def test_get_document() -> None:
        r"""Test get document.

        :rtype: None
        """
        assert search_document("pip", "") != NOT_FOUND
        assert search_document("", "") == NOT_FOUND
