r"""Provide ``__version__`` for
`importlib.metadata.version() <https://docs.python.org/3/library/importlib.metadata.html#distribution-versions>`_.
"""
import os

from platformdirs import user_cache_dir, user_config_dir

from ._version import __version__, __version_tuple__  # type: ignore

__all__ = ["__version__", "__version_tuple__"]

NOT_FOUND = "Not found installed package!"
# https://pip.pypa.io/en/stable/reference/requirements-file-format/#supported-options
WHITELIST = [
    "-i",
    "--index-url",
    "--extra-index-url",
    "--no-index",
    "-c",
    "--constraint",
    "-r",
    "--requirement",
    "-e",
    "--editable",
    "-f",
    "--find-links",
    "--no-binary",
    "--only-binary",
    "--prefer-binary",
    "--require-hashes",
    "--pre",
    "--trusted-host",
    "--use-feature",
    "--global-option",
    "--config-settings",
    "--hash",
]
PATH = os.path.join(user_config_dir("pip"), "template.md.j2")
CACHE = os.path.join(user_cache_dir("pip"), "pip.json")
CONFIG = {
    "template": PATH,
    "cache": CACHE,
}
if not os.path.exists(PATH):
    PATH = os.path.join(
        os.path.join(
            os.path.join(os.path.dirname(__file__), "assets"), "jinja2"
        ),
        "template.md.j2",
    )
with open(PATH, "r") as f:
    TEMPLATE = f.read()
