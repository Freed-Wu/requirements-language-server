# Configure

See customization in
<https://portage-language-server.readthedocs.io/en/latest/api/portage-language-server.html#portage_language_server.server.get_document>.

## (Neo)[Vim](https://www.vim.org)

### [coc.nvim](https://github.com/neoclide/coc.nvim)

```json
{
  "languageserver": {
    "portage": {
      "command": "portage-language-server",
      "filetypes": [
        "sh"
      ],
      "initializationOptions": {
        "method": "builtin"
      }
    }
  }
}
```

### [vim-lsp](https://github.com/prabirshrestha/vim-lsp)

```vim
if executable('portage-language-server')
  augroup lsp
    autocmd!
    autocmd User lsp_setup call lsp#register_server({
          \ 'name': 'portage',
          \ 'cmd': {server_info->['portage-language-server']},
          \ 'whitelist': ['sh'],
          \ 'initialization_options': {
          \   'method': 'builtin',
          \ },
          \ })
  augroup END
endif
```

## [Neovim](https://neovim.io)

```lua
vim.api.nvim_create_autocmd({ "BufEnter" }, {
  pattern = { "*.ebuild" "*.eclass" "make.conf" "color.map" },
  callback = function()
    vim.lsp.start({
      name = "portage",
      cmd = { "portage-language-server" }
    })
  end,
})
```

## [Emacs](https://www.gnu.org/software/emacs)

```elisp
(make-lsp-client :new-connection
(lsp-stdio-connection
  `(,(executable-find "portage-language-server")))
  :activation-fn (lsp-activate-on "*.ebuild" "*.eclass" "make.conf" "color.map")
  :server-id "portage")))
```

## [Sublime](https://www.sublimetext.com)

```json
{
  "clients": {
    "portage": {
      "command": [
        "portage-language-server"
      ],
      "enabled": true,
      "selector": "source.sh"
    }
  }
}
```
