r"""Pip
=======
"""

import asyncio
from collections.abc import Collection, Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from threading import Thread

from aiohttp import ClientSession, TCPConnector
from jinja2 import Template
from lsp_tree_sitter.completer import PackageSearcher
from marisa_trie import Trie
from pip._internal.metadata import get_default_environment
from pip._internal.metadata.base import BaseDistribution
from pip._vendor.packaging.requirements import InvalidRequirement, Requirement
from pip._vendor.packaging.utils import canonicalize_name
from platformdirs import user_config_path


def get_template(name: str = "requirements.md.jinja") -> Template:
    path = user_config_path("pip") / name
    if not path.exists():
        path = Path(__file__).parent.parent / "assets" / "jinja" / name
    return Template(path.read_text())


@dataclass
class PypiRequirement:
    name: str


@dataclass
class PypiDistribution:
    canonical_name: str
    metadata_dict: dict[str, str | list[str]]
    requires_dist: tuple[str, ...] = ()

    def iter_dependencies(
        self, extras: Collection[str] = ()
    ) -> Iterable[Requirement]:
        for require in self.requires_dist:
            try:
                yield PypiRequirement(Requirement(require).name)
            except InvalidRequirement:
                continue

    @classmethod
    def from_json(cls, info: dict) -> "PypiDistribution":
        project_urls = info.get("project_urls") or {}
        return PypiDistribution(
            canonical_name=canonicalize_name(info.get("name") or ""),
            metadata_dict={
                "summary": info.get("summary") or "",
                "version": info.get("version") or "",
                "license": info.get("license") or "",
                "author": info.get("author") or "",
                "author_email": info.get("author_email") or "",
                "requires_python": info.get("requires_python") or "",
                "project_url": [
                    f"{label}, {url}" for label, url in project_urls.items()
                ],
                "provides_extra": info.get("provides_extra") or [],
            },
            requires_dist=info.get("requires_dist") or (),
        )

    @staticmethod
    async def get_package_distribution(name: str) -> dict:
        url = f"https://pypi.org/pypi/{name}/json"
        conn = TCPConnector(ssl=False)
        async with (
            ClientSession(connector=conn) as session,
            session.get(url) as resp,
        ):
            resp.raise_for_status()
            return (await resp.json()).get("info", {})

    @classmethod
    async def from_name(cls, name: str) -> "PypiDistribution":
        return cls.from_json(await cls.get_package_distribution(name))


@dataclass
class PipSearcher(PackageSearcher):
    kind: str = "package"
    selector: str = ""
    label: str = "variable"
    url_template: str = "https://pypi.org/project/{}/"
    template: Template = field(default_factory=get_template)
    pkginfos: dict[str, str] = field(default_factory=dict)
    installed: dict[str, BaseDistribution] = field(
        default_factory=lambda: {
            dist.canonical_name: dist
            for dist in get_default_environment().iter_all_distributions()
        }
    )
    has_requires: bool = True
    has_required_by: bool = True
    trie: Trie | None = None

    def __post_init__(self) -> None:
        Thread(
            target=asyncio.run, args=(self.build_trie(),), daemon=True
        ).start()
        for name, dist in self.installed.items():
            Thread(
                target=self.update_pkginfos, args=(name, dist), daemon=True
            ).start()

    def has_package(self, name: str) -> bool:
        return name in self.pkginfos

    def get_package_url(self, name: str) -> str:
        return self.url_template.format(name)

    def get_package_version(self, name: str) -> str:
        return (
            self.installed[name].metadata_dict["version"]
            if name in self.installed
            else ""
        )

    def get_package_names(self, name: str) -> dict[str, str]:
        if self.trie is None:
            return {}
        return {
            pkgname: self.pkginfos[pkgname] for pkgname in self.trie.keys(name)
        }

    def get_package_document(self, name: str) -> str:
        if self.pkginfos[name] == "":
            if name in self.installed:
                dist = self.installed[name]
                self.pkginfos[name] = self.render_document(dist)
            else:
                Thread(
                    target=asyncio.run,
                    args=(self.update_pkginfos_pypi(name),),
                    daemon=True,
                ).start()
        return self.pkginfos[name]

    def render_document(
        self, dist: BaseDistribution | PypiDistribution
    ) -> str:
        if self.has_requires:
            requires = sorted(
                (req.name for req in dist.iter_dependencies()),
                key=str.lower,
            )
        if self.has_required_by:
            required_by = sorted(
                self.get_requiring_packages(dist), key=str.lower
            )
        return self.template.render(
            dist=dist, requires=requires, required_by=required_by
        )

    def get_requiring_packages(
        self, current_dist: BaseDistribution | PypiDistribution
    ) -> Iterator[str]:
        return (
            dist.metadata["Name"] or "UNKNOWN"
            for dist in self.installed.values()
            if current_dist.canonical_name
            in {canonicalize_name(d.name) for d in dist.iter_dependencies()}
        )

    def update_pkginfos(self, name: str, dist: BaseDistribution) -> None:
        self.pkginfos[name] = self.render_document(dist)

    async def update_pkginfos_pypi(self, name: str) -> None:
        dist = await PypiDistribution.from_name(name)
        self.pkginfos[name] = self.render_document(dist)

    async def build_trie(self) -> None:
        for project in await self.get_pkgnames():
            name = project.get("name", "")
            self.pkginfos[name] = self.pkginfos.get(name, "")
        self.trie = Trie(self.pkginfos)

    @staticmethod
    async def get_pkgnames() -> list[dict]:
        r"""Update pkgnames. IO bound.

        `<https://stackoverflow.com/questions/21419009/json-api-for-pypi-how-to-list-packages/51420285#51420285>`_
        """

        url = "https://pypi.org/simple/"
        headers = {"Accept": "application/vnd.pypi.simple.v1+json"}

        conn = TCPConnector(ssl=False)
        async with (
            ClientSession(connector=conn) as session,
            session.get(url, headers=headers) as resp,
        ):
            resp.raise_for_status()
            return (await resp.json()).get("projects", [])
