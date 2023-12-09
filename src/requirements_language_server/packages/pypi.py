r"""PYPI
========
"""
import os
from contextlib import suppress
from typing import Any

from jinja2 import Template
from pip._internal.commands.show import _PackageInfo, search_packages_info
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


def render_document(
    metadata: dict[str, Any],
    info: _PackageInfo | None = None,
    template: str = TEMPLATE,
) -> str:
    r"""Render document.

    :param metadata:
    :type metadata: dict[str, Any]
    :param info:
    :type info: _PackageInfo | None
    :param template:
    :type template: str
    :rtype: str
    """
    return Template(template).render(metadata=metadata, info=info)


def search_package_names(
    name: str,
    search: bool = True,
    use_info: bool | None = None,
    template: str = TEMPLATE,
) -> dict[str, str]:
    r"""Search package names.

    :param name:
    :type name: str
    :param search:
    :type search: bool
    :param use_info:
    :type use_info: bool | None
    :param template:
    :type template: str
    :rtype: dict[str, str]
    """
    if use_info is None:
        use_info = not search
    package_names = {
        pkgname: NOT_FOUND
        for pkgname in (get_package_names(name) if search else [name])
    }
    count = len(package_names)
    for pkg in ENV.iter_installed_distributions():
        if pkg.canonical_name not in package_names:
            continue
        info = None
        if use_info:
            with suppress(IndexError):
                info = next(iter(search_packages_info([pkg.canonical_name])))
        package_names[pkg.canonical_name] = render_document(
            pkg.metadata_dict, info, template
        )
        count -= 1
        if count == 0:
            break
    return package_names
