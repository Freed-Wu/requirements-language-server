r"""Api
=======
"""
import json

from jinja2 import Template
from pip._internal.commands.show import search_packages_info
from pip._internal.metadata import get_environment

from . import CACHE, NOT_FOUND, TEMPLATE


def search_document(pkgname: str, template: str) -> str:
    r"""Search document.

    :param pkgname:
    :type pkgname: str
    :param template:
    :type template: str
    :rtype: str
    """
    try:
        info = list(search_packages_info([pkgname]))[0]
        output = Template(template).render(info=info)
    except IndexError:
        output = NOT_FOUND
    return output


def generate_cache() -> None:
    r"""Generate cache.

    :rtype: None
    """
    documents = {
        pkgname: search_document(pkgname, TEMPLATE)
        for pkgname in [
            x.canonical_name
            for x in get_environment(None).iter_installed_distributions()
        ]
    }
    with open(CACHE, "w") as f:
        json.dump(documents, f)
