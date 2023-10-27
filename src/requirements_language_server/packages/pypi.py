r"""PYPI
========
"""
import os
from typing import Any

from jinja2 import Template
from pip._internal.metadata import get_environment
from pip_cache import get_package_names
from platformdirs import user_config_dir

NOT_FOUND = "Not found installed package!"
ENV = get_environment(None)
PATH = os.path.join(user_config_dir("pip"), "template.md.j2")
if not os.path.exists(PATH):
    PATH = os.path.join(
        os.path.join(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets"),
            "jinja2",
        ),
        "template.md.j2",
    )
with open(PATH, "r") as f:
    TEMPLATE = f.read()


def render_document(metadata: dict[str, Any], template: str = TEMPLATE) -> str:
    r"""Render document.

    :param metadata:
    :type metadata: dict[str, Any]
    :param template:
    :type template: str
    :rtype: str
    """
    return Template(template).render(metadata=metadata)


def search_document(pkgname: str, template: str = TEMPLATE) -> str:
    r"""Search document.

    :param pkgname:
    :type pkgname: str
    :param template:
    :type template: str
    :rtype: str
    """
    for pkg in ENV.iter_installed_distributions():
        if pkg.canonical_name == pkgname:
            metadata = pkg.metadata_dict
            return render_document(metadata, template)
    return NOT_FOUND


def search_package_names(name: str) -> dict[str, str]:
    r"""Search package names.

    :param name:
    :type name: str
    :rtype: dict[str, str]
    """
    package_names = {pkgname: NOT_FOUND for pkgname in get_package_names(name)}
    for pkg in ENV.iter_installed_distributions():
        if pkg.canonical_name.startswith(name):
            metadata = pkg.metadata_dict
            package_names[pkg.canonical_name] = render_document(metadata)
    return package_names
