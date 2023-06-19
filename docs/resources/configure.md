# Configure

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

## (Neo)[Vim](https://www.vim.org)

### [coc.nvim](https://github.com/neoclide/coc.nvim)

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

### [vim-lsp](https://github.com/prabirshrestha/vim-lsp)

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

## [Neovim](https://neovim.io)

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

## [Emacs](https://www.gnu.org/software/emacs)

```elisp
(make-lsp-client :new-connection
(lsp-stdio-connection
  `(,(executable-find "requirements-language-server")))
  :activation-fn (lsp-activate-on "requirements*.txt*")
  :server-id "requirements")))
```

## [Sublime](https://www.sublimetext.com)

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
