r"""Test utils."""
import os

from tree_sitter_lsp.diagnose import check
from tree_sitter_requirements import parse

from requirements_language_server.finders import DIAGNOSTICS_FINDER_CLASSES
from requirements_language_server.utils import get_filetype


class Test:
    r"""Test."""

    @staticmethod
    def test_check() -> None:
        r"""Test check.

        :rtype: None
        """
        result = check(
            [os.path.join(os.path.dirname(__file__), "requirements.txt.in")],
            parse,
            DIAGNOSTICS_FINDER_CLASSES,
            get_filetype,
        )
        assert result > 0
