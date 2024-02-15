r"""Test package"""

from requirements_language_server.packages import NOT_FOUND, render_document


class Test:
    r"""Test."""

    @staticmethod
    def test_get_document() -> None:
        r"""Test get document.

        :rtype: None
        """
        assert render_document("pip") != NOT_FOUND  # type: ignore
