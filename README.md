# portage-language-server

[![readthedocs](https://shields.io/readthedocs/portage-language-server)](https://portage-language-server.readthedocs.io)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Freed-Wu/portage-language-server/main.svg)](https://results.pre-commit.ci/latest/github/Freed-Wu/portage-language-server/main)
[![github/workflow](https://github.com/Freed-Wu/portage-language-server/actions/workflows/main.yml/badge.svg)](https://github.com/Freed-Wu/portage-language-server/actions)
[![codecov](https://codecov.io/gh/Freed-Wu/portage-language-server/branch/main/graph/badge.svg)](https://codecov.io/gh/Freed-Wu/portage-language-server)
[![DeepSource](https://deepsource.io/gh/Freed-Wu/portage-language-server.svg/?show_trend=true)](https://deepsource.io/gh/Freed-Wu/portage-language-server)

[![github/downloads](https://shields.io/github/downloads/Freed-Wu/portage-language-server/total)](https://github.com/Freed-Wu/portage-language-server/releases)
[![github/downloads/latest](https://shields.io/github/downloads/Freed-Wu/portage-language-server/latest/total)](https://github.com/Freed-Wu/portage-language-server/releases/latest)
[![github/issues](https://shields.io/github/issues/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server/issues)
[![github/issues-closed](https://shields.io/github/issues-closed/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server/issues?q=is%3Aissue+is%3Aclosed)
[![github/issues-pr](https://shields.io/github/issues-pr/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server/pulls)
[![github/issues-pr-closed](https://shields.io/github/issues-pr-closed/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server/pulls?q=is%3Apr+is%3Aclosed)
[![github/discussions](https://shields.io/github/discussions/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server/discussions)
[![github/milestones](https://shields.io/github/milestones/all/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server/milestones)
[![github/forks](https://shields.io/github/forks/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server/network/members)
[![github/stars](https://shields.io/github/stars/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server/stargazers)
[![github/watchers](https://shields.io/github/watchers/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server/watchers)
[![github/contributors](https://shields.io/github/contributors/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server/graphs/contributors)
[![github/commit-activity](https://shields.io/github/commit-activity/w/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server/graphs/commit-activity)
[![github/last-commit](https://shields.io/github/last-commit/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server/commits)
[![github/release-date](https://shields.io/github/release-date/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server/releases/latest)

[![github/license](https://shields.io/github/license/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server/blob/main/LICENSE)
[![github/languages](https://shields.io/github/languages/count/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server)
[![github/languages/top](https://shields.io/github/languages/top/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server)
[![github/directory-file-count](https://shields.io/github/directory-file-count/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server)
[![github/code-size](https://shields.io/github/languages/code-size/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server)
[![github/repo-size](https://shields.io/github/repo-size/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server)
[![github/v](https://shields.io/github/v/release/Freed-Wu/portage-language-server)](https://github.com/Freed-Wu/portage-language-server)

[![pypi/status](https://shields.io/pypi/status/portage-language-server)](https://pypi.org/project/portage-language-server/#description)
[![pypi/v](https://shields.io/pypi/v/portage-language-server)](https://pypi.org/project/portage-language-server/#history)
[![pypi/downloads](https://shields.io/pypi/dd/portage-language-server)](https://pypi.org/project/portage-language-server/#files)
[![pypi/format](https://shields.io/pypi/format/portage-language-server)](https://pypi.org/project/portage-language-server/#files)
[![pypi/implementation](https://shields.io/pypi/implementation/portage-language-server)](https://pypi.org/project/portage-language-server/#files)
[![pypi/pyversions](https://shields.io/pypi/pyversions/portage-language-server)](https://pypi.org/project/portage-language-server/#files)

Language server for [Gentoo Linux](https://www.gentoo.org)/
[Gentoo BSD](https://wiki.gentoo.org/wiki/Gentoo_BSD)/
[Gentoo Darwin](https://wiki.gentoo.org/wiki/Prefix/Darwin)'s
[`portage`](https://github.com/gentoo/portage)'s

- [`*.ebuild`](https://dev.gentoo.org/~zmedico/portage/doc/man/ebuild.5.html)
- `*.eclass`
- [`make.conf`](https://dev.gentoo.org/~zmedico/portage/doc/man/make.conf.5.html).
- [`color.map`](https://dev.gentoo.org/~zmedico/portage/doc/man/color.map.5.html)

The above files are a subtype of bash. See
[bash-language-server](https://github.com/bash-lsp/bash-language-server) to get
support of bash language server.

- [x] document hover
- [x] completion

## Document hover

![keyword](https://github.com/Freed-Wu/pkgbuild-language-server/assets/32936898/a1bb24d3-70d3-4bc5-8056-90ea0acc16cd)

## Completion

![keyword](https://github.com/Freed-Wu/pkgbuild-language-server/assets/32936898/c060690c-071b-41a0-bde5-dce338f4e779)

Read
[![readthedocs](https://shields.io/readthedocs/portage-language-server)](https://portage-language-server.readthedocs.io)
to know more.

## Similar Projects

- [gentoo-syntax](https://github.com/gentoo/gentoo-syntax): Syntax highlight
  for vim.
