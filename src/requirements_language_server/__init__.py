r"""Provide ``__version__`` for
`importlib.metadata.version() <https://docs.python.org/3/library/importlib.metadata.html#distribution-versions>`_.
"""
import os

from platformdirs import user_cache_dir, user_config_dir

try:
    from ._version import __version__, __version_tuple__  # type: ignore
except ImportError:  # for setuptools-generate
    __version__ = "rolling"
    __version_tuple__ = (0, 0, 0, __version__, "")

__all__ = ["__version__", "__version_tuple__"]

NOT_FOUND = "Not found installed package!"
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
