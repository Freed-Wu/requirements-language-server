r"""Api
=======
"""
import os
from gzip import decompress

from bs4 import BeautifulSoup, FeatureNotFound
from platformdirs import site_data_dir
from pypandoc import convert_text


def get_soup(filename: str) -> BeautifulSoup:
    r"""Get soup.

    :param filename:
    :type filename: str
    :rtype: BeautifulSoup
    """
    with open(
        os.path.join(
            os.path.join(site_data_dir("man"), "man5"), filename + ".5.gz"
        ),
        "rb",
    ) as f:
        html = convert_text(decompress(f.read()).decode(), "html", "man")
    try:
        soup = BeautifulSoup(html, "lxml")
    except FeatureNotFound:
        soup = BeautifulSoup(html, "html.parser")
    return soup


def init_document() -> dict[str, tuple[str, str]]:
    r"""Init document.

    :rtype: dict[str, tuple[str, str]]
    """
    items = {}
    dl = get_soup("color.map").findAll("dl")[1]
    for dt, dd in zip(dl.findAll("dt"), dl.findAll("dd")):
        items[dt.strong.text] = (
            dt.text + "\n" + dd.text.replace("\n", " ").strip(),
            "color.map",
        )
    for dl in get_soup("make.conf").findAll("dl")[:-2]:
        for dt, dd in zip(dl.findAll("dt"), dl.findAll("dd")):
            if dt.strong is None:
                continue
            items[dt.strong.text] = (
                dt.text + "\n" + dd.text.replace("\n", " ").strip(),
                "make.conf",
            )
    for dl in get_soup("ebuild").findAll("dl")[20:-2]:
        for dt, dd in zip(dl.findAll("dt"), dl.findAll("dd")):
            if dt.strong is None or dt.strong.text.endswith(":"):
                continue
            items[dt.strong.text.split()[0]] = (
                dt.text + "\n" + dd.text.replace("\n", " ").strip(),
                "ebuild",
            )
    return items
