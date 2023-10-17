r"""Test utils."""
import os

from tree_sitter_requirements import parse

from requirements_language_server.tree_sitter_lsp.diagnose import check
from requirements_language_server.utils import DIAGNOSTICS_FINDERS


class Test:
    r"""Test."""

    @staticmethod
    def test_check() -> None:
        r"""Test check.

        :rtype: None
        """
        result = check(
            [os.path.join(os.path.dirname(__file__), "requirements.txt.in")],
            DIAGNOSTICS_FINDERS,
            parse,
        )
        assert result > 0
