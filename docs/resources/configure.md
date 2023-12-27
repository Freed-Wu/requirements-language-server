# Configure

You can customize the document hover template. A default template is
[here](https://github.com/Freed-Wu/requirements-language-server/tree/main/src/requirements_language_server/assets/jinja2/template.md.j2).
The syntax rule is [jinja](https://docs.jinkan.org/docs/jinja2/templates.html).
The template path is decided by your OS:

- `~/.config/pip/template.md.j2`
- For windows, change `~/.config` to `~/AppData/Local`
- For macOS, change `~/.config` to `~/Library`

## (Neo)[Vim](https://www.vim.org)

For vim:

- Change `~/.config/nvim` to `~/.vim`
- Change `init.vim` to `vimrc`

### [coc.nvim](https://github.com/neoclide/coc.nvim)

`~/.config/nvim/coc-settings.json`:

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

`~/.config/nvim/init.vim`:

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

`~/.config/nvim/init.lua`:

```lua
vim.api.nvim_create_autocmd({ "BufEnter" }, {
  pattern = { "requirements.txt", "requirements/*.txt" },
  callback = function()
    vim.lsp.start({
      name = "requirements",
      cmd = { "requirements-language-server" }
    })
  end,
})
```

## [Emacs](https://www.gnu.org/software/emacs)

`~/.emacs.d/init.el`:

```lisp
(make-lsp-client :new-connection
(lsp-stdio-connection
  `(,(executable-find "requirements-language-server")))
  :activation-fn (lsp-activate-on "requirements.txt" "requirements/*.txt")
  :server-id "requirements")))
```

## [Helix](https://helix-editor.com/)

`~/.config/helix/languages.toml`:

```toml
[[language]]
name = "requirements"
language-servers = [ "requirements-language-server",]

[language_server.requirements-language-server]
command = "requirements-language-server"
```

## [KaKoune](https://kakoune.org/)

### [kak-lsp](https://github.com/kak-lsp/kak-lsp)

`~/.config/kak-lsp/kak-lsp.toml`:

```toml
[language_server.requirements-language-server]
filetypes = [ "requirements",]
command = "requirements-language-server"
```

## [Sublime](https://www.sublimetext.com)

`~/.config/sublime-text-3/Packages/Preferences.sublime-settings`:

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

## [Visual Studio Code](https://code.visualstudio.com/)

[An official support of generic LSP client is pending](https://github.com/microsoft/vscode/issues/137885).

### [vscode-glspc](https://gitlab.com/ruilvo/vscode-glspc)

`~/.config/Code/User/settings.json`:

```json
{
  "glspc.serverPath": "requirements-language-server",
  "glspc.languageId": "requirements.txt"
}
```
