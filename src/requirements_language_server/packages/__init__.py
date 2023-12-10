r"""Packages
============
"""
import os
from threading import Thread
from typing import Iterator
from xmlrpc.client import ServerProxy

from jinja2 import Template
from pip._internal.metadata import get_default_environment
from pip._internal.metadata.base import BaseDistribution
from pip._vendor.packaging.utils import NormalizedName, canonicalize_name
from platformdirs import user_config_dir

proxy = ServerProxy("https://pypi.python.org/pypi")
pkginfos: dict[NormalizedName, str] = {}
NOT_FOUND = "Not found installed package!"
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
installed: dict[NormalizedName, BaseDistribution] = {
    dist.canonical_name: dist
    for dist in get_default_environment().iter_all_distributions()
}


def get_pkginfos() -> dict[NormalizedName, str]:
    r"""Get pkginfos.

    :rtype: dict[NormalizedName, str]
    """
    return pkginfos


def get_requiring_packages(current_dist: BaseDistribution) -> Iterator[str]:
    r"""Get requiring packages.

    :param current_dist:
    :type current_dist: BaseDistribution
    :rtype: Iterator[str]
    """
    return (
        dist.metadata["Name"] or "UNKNOWN"
        for dist in installed.values()
        if current_dist.canonical_name
        in {canonicalize_name(d.name) for d in dist.iter_dependencies()}
    )


async def update_pkginfos() -> None:
    r"""Update pkginfos.

    :rtype: None
    """
    global pkginfos
    Thread(target=update_installed_pkginfos).start()
    for pkgname in proxy.list_packages():  # type: ignore
        if pkgname not in pkginfos:
            pkginfos[pkgname] = NOT_FOUND


def render_document(
    pkgname: NormalizedName,
    has_requires: bool = True,
    has_required_by: bool = True,
):
    r"""Render document.

    :param pkgname:
    :type pkgname: NormalizedName
    :param has_requires:
    :type has_requires: bool
    :param has_required_by:
    :type has_required_by: bool
    """
    if dist := installed.get(pkgname):
        requires = required_by = None
        if has_requires:
            requires = sorted(
                (req.name for req in dist.iter_dependencies()), key=str.lower
            )
        if has_required_by:
            required_by = sorted(get_requiring_packages(dist), key=str.lower)
        return Template(TEMPLATE).render(
            dist=dist, requires=requires, required_by=required_by
        )
    return NOT_FOUND


def update_installed_pkginfos(
    has_requires: bool = False, has_required_by: bool = False
) -> None:
    r"""Update installed pkginfos.

    :param has_requires:
    :type has_requires: bool
    :param has_required_by:
    :type has_required_by: bool
    :rtype: None
    """
    global pkginfos
    for dist in installed.values():
        pkgname = dist.canonical_name
        pkginfos[pkgname] = render_document(
            pkgname, has_requires, has_required_by
        )
