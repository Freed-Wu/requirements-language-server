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
from platformdirs import user_cache_dir, user_config_dir

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
CACHE_PATH = os.path.join(user_cache_dir("pip"), "requirements.txt")
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


def update_pkginfos() -> None:
    r"""Update pkginfos.

    :rtype: None
    """
    global pkginfos
    for pkgname in installed:
        Thread(target=render_document, args=(pkgname, False, False)).start()
    Thread(target=update_pkgnames).start()


def update_pkgnames():
    r"""Update pkgnames."""
    global pkginfos
    is_updated = False
    pkgnames: list[NormalizedName]
    if os.path.isfile(CACHE_PATH):
        with open(CACHE_PATH) as f:
            pkgnames = [pkgname.strip() for pkgname in f.readlines()]  # type: ignore
    else:
        # IO bound
        pkgnames = proxy.list_packages()  # type: ignore
        is_updated = True
    for pkgname in pkgnames:  # type: ignore
        if pkgname not in pkginfos:
            pkginfos[pkgname] = NOT_FOUND
    if not is_updated:
        pkgnames = proxy.list_packages()  # type: ignore
        if pkgnames != []:
            with open(CACHE_PATH, "w") as f:
                f.writelines(pkgname + "\n" for pkgname in pkgnames)


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
    global pkginfos
    pkginfo = pkginfos.get(pkgname)
    # cache hit
    if pkginfo and not (pkginfo.find("1. ...") and pkginfo.find("2. ...")):
        return pkginfo
    if dist := installed.get(pkgname):
        requires = required_by = None
        if has_requires:
            requires = sorted(
                (req.name for req in dist.iter_dependencies()), key=str.lower
            )
        if has_required_by:
            required_by = sorted(get_requiring_packages(dist), key=str.lower)
        pkginfos[pkgname] = Template(TEMPLATE).render(
            dist=dist, requires=requires, required_by=required_by
        )
        return pkginfos[pkgname]
    return NOT_FOUND
