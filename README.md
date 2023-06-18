# requirements-language-server

[![readthedocs](https://shields.io/readthedocs/requirements-language-server)](https://requirements-language-server.readthedocs.io)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Freed-Wu/requirements-language-server/main.svg)](https://results.pre-commit.ci/latest/github/Freed-Wu/requirements-language-server/main)
[![github/workflow](https://github.com/Freed-Wu/requirements-language-server/actions/workflows/main.yml/badge.svg)](https://github.com/Freed-Wu/requirements-language-server/actions)
[![codecov](https://codecov.io/gh/Freed-Wu/requirements-language-server/branch/main/graph/badge.svg)](https://codecov.io/gh/Freed-Wu/requirements-language-server)
[![DeepSource](https://deepsource.io/gh/Freed-Wu/requirements-language-server.svg/?show_trend=true)](https://deepsource.io/gh/Freed-Wu/requirements-language-server)

[![github/downloads](https://shields.io/github/downloads/Freed-Wu/requirements-language-server/total)](https://github.com/Freed-Wu/requirements-language-server/releases)
[![github/downloads/latest](https://shields.io/github/downloads/Freed-Wu/requirements-language-server/latest/total)](https://github.com/Freed-Wu/requirements-language-server/releases/latest)
[![github/issues](https://shields.io/github/issues/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server/issues)
[![github/issues-closed](https://shields.io/github/issues-closed/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server/issues?q=is%3Aissue+is%3Aclosed)
[![github/issues-pr](https://shields.io/github/issues-pr/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server/pulls)
[![github/issues-pr-closed](https://shields.io/github/issues-pr-closed/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server/pulls?q=is%3Apr+is%3Aclosed)
[![github/discussions](https://shields.io/github/discussions/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server/discussions)
[![github/milestones](https://shields.io/github/milestones/all/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server/milestones)
[![github/forks](https://shields.io/github/forks/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server/network/members)
[![github/stars](https://shields.io/github/stars/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server/stargazers)
[![github/watchers](https://shields.io/github/watchers/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server/watchers)
[![github/contributors](https://shields.io/github/contributors/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server/graphs/contributors)
[![github/commit-activity](https://shields.io/github/commit-activity/w/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server/graphs/commit-activity)
[![github/last-commit](https://shields.io/github/last-commit/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server/commits)
[![github/release-date](https://shields.io/github/release-date/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server/releases/latest)

[![github/license](https://shields.io/github/license/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server/blob/main/LICENSE)
[![github/languages](https://shields.io/github/languages/count/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server)
[![github/languages/top](https://shields.io/github/languages/top/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server)
[![github/directory-file-count](https://shields.io/github/directory-file-count/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server)
[![github/code-size](https://shields.io/github/languages/code-size/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server)
[![github/repo-size](https://shields.io/github/repo-size/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server)
[![github/v](https://shields.io/github/v/release/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server)

[![pypi/status](https://shields.io/pypi/status/requirements-language-server)](https://pypi.org/project/requirements-language-server/#description)
[![pypi/v](https://shields.io/pypi/v/requirements-language-server)](https://pypi.org/project/requirements-language-server/#history)
[![pypi/downloads](https://shields.io/pypi/dd/requirements-language-server)](https://pypi.org/project/requirements-language-server/#files)
[![pypi/format](https://shields.io/pypi/format/requirements-language-server)](https://pypi.org/project/requirements-language-server/#files)
[![pypi/implementation](https://shields.io/pypi/implementation/requirements-language-server)](https://pypi.org/project/requirements-language-server/#files)
[![pypi/pyversions](https://shields.io/pypi/pyversions/requirements-language-server)](https://pypi.org/project/requirements-language-server/#files)

Language server for
[requirements.txt](https://pip.pypa.io/en/stable/reference/requirements-file-format).

- [x] document hover: requires [pip](https://github.com/pypa/pip).
- [x] completion: requires [pip-cache](https://github.com/brunobeltran/pip-cache).
  Must `pip-cache update` before.
- [x] diagnostic: requires [pip-compile](https://github.com/jazzband/pip-tools).

## Screenshots

### Document Hover

![module](https://github.com/Freed-Wu/requirements-language-server/assets/32936898/0e74a423-b07a-459a-8fb4-10789f245265)

![option](https://github.com/Freed-Wu/requirements-language-server/assets/32936898/78a7b5ec-a9dd-46c2-b22b-4dc0123b6f0e)

### Completion

![module](https://github.com/Freed-Wu/requirements-language-server/assets/32936898/d3a258ef-3d99-4666-a015-cc516bdb58fd)

![option](https://github.com/Freed-Wu/requirements-language-server/assets/32936898/1a8de48c-9138-4a0c-97a4-0c7ea3030be0)

![file](https://github.com/Freed-Wu/requirements-language-server/assets/32936898/da7e162d-fa82-461a-a8b4-09db684e766c)

### Diagnostic

![module](https://user-images.githubusercontent.com/32936898/194537147-bf4b4528-2594-46df-b05c-56c38c419920.png)

## Usage

### Vim/Neovim

#### [coc.nvim](https://github.com/neoclide/coc.nvim)

```json
{
  "languageserver": {
    "requirements": {
      "command": "requirements-language-server",
      "filetypes": [
        "requirements"
      ]
    }
  }
}
```

#### [vim-lsp](https://github.com/prabirshrestha/vim-lsp)

```vim
if executable('requirements-language-server')
  augroup lsp
    autocmd!
    autocmd User lsp_setup call lsp#register_server({
          \ 'name': 'requirements',
          \ 'cmd': {server_info->['requirements-language-server']},
          \ 'whitelist': ['requirements'],
          \ })
  augroup END
endif
```

### Neovim

```lua
vim.api.nvim_create_autocmd({ "BufEnter" }, {
  pattern = { "requirements*.txt*" },
  callback = function()
    vim.lsp.start({
      name = "requirements",
      cmd = { "requirements-language-server" }
    })
  end,
})
```

### Emacs

```elisp
(make-lsp-client :new-connection
(lsp-stdio-connection
  `(,(executable-find "requirements-language-server")))
  :activation-fn (lsp-activate-on "requirements*.txt*")
  :server-id "requirements")))
```

### Sublime

```json
{
  "clients": {
    "requirements": {
      "command": [
        "requirements-language-server"
      ],
      "enabled": true,
      "selector": "source.requirements"
    }
  }
}
```

## Customization

You can customize the document hover template. A default template is
[here](https://github.com/Freed-Wu/requirements-language-server/tree/main/src/requirements_language_server/assets/jinja2/template.md.j2).
The syntax rule is [jinja](https://docs.jinkan.org/docs/jinja2/templates.html).
The template path is decided by your OS:

```shell
$ requirements-language-server --print-config template
/home/wzy/.config/pip/template.md.j2
```

You can generate cache by `requirements-language-server --generate-cache` to
fasten document hover and completion. Every time you change template, the cache
must be regenerated.

```shell
$ requirements-language-server --print-config cache
/home/wzy/.cache/pip/pip.json
```

## Related Projects

- [requirements.txt.vim](https://github.com/raimon49/requirements.txt.vim):
  syntax highlight for vim
- [vim-polyglot](https://github.com/sheerun/vim-polyglot): contains above
- [bat](https://github.com/sharkdp/bat): syntax highlight for less
