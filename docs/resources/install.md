# Install

## [AUR](https://aur.archlinux.org/packages/python-requirements-language-server)

```sh
yay -S python-requirements-language-server
```

## [NUR](https://nur.nix-community.org/repos/Freed-Wu)

```nix
{ config, pkgs, ... }:
{
  nixpkgs.config.packageOverrides = pkgs: {
    nur = import
      (
        builtins.fetchTarball
          "https://github.com/nix-community/NUR/archive/master.tar.gz"
      )
      {
        inherit pkgs;
      };
  };
  environment.systemPackages = with pkgs;
      (
        python3.withPackages (
          p: with p; [
            nur.repos.Freed-Wu.requirements-language-server
          ]
        )
      )
}
```

## [Nix](https://nixos.org)

```sh
nix shell github:Freed-Wu/requirements-language-server
```

Run without installation:

```sh
nix run github:Freed-Wu/requirements-language-server -- --help
```

## [PYPI](https://pypi.org/project/requirements-language-server)

```sh
pip install requirements-language-server
```

See [requirements](requirements) to know `extra_requires`.
