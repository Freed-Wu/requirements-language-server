r"""Test package"""
from requirements_language_server.packages import search_package_names
from requirements_language_server.packages.pypi import NOT_FOUND


class Test:
    r"""Test."""

    @staticmethod
    def test_get_document() -> None:
        r"""Test get document.

        :rtype: None
        """
        assert search_package_names("pip", False)["pip"] != NOT_FOUND
        assert search_package_names("pip", True)["pip"] != NOT_FOUND
        assert search_package_names("", False)[""] == NOT_FOUND
