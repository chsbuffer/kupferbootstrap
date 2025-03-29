# kupferbootstrap

Kupfer Linux bootstrapping tool - drives pacstrap, makepkg, chroot, mkfs and fastboot, just to name a few.

## Table Of Contents

[[_TOC_]]

## Full Documentation

Detailed docs are available online at https://kupfer.gitlab.io/kupferbootstrap/

You can also build and view the docs locally:
```sh
cd docs/ && \
make && \
make serve
```

This will run a webserver on localhost:9999. Access it like `firefox http://localhost:9999/`


## Installation
0. If you're not on ArchLinux (i.e. don't have `pacman`, `makepkg`, etc. available in your $PATH), install Docker and add yourself to the `docker` group.
1. For the python installation, either run `make` or follow the manual installation steps below.

### Manual Installation
1. Craate a python venv: `python3 -m venv venv`
1. Install KBS: `venv/bin/pip3 install -e .`
1. Activate it: `source venv/bin/activate`

If you don't want to have to source the venv every time,
you can symlink `venv/bin/kupferbootstrap` into your `$PATH`.

### Try it

Then run `kupferbootstrap --help`.

### Pro Tip:

- You can add a shell alias for `$(PWD)/venv/bin/kupferbootstrap`
  or create a symlink to it inside your `$PATH` for quick access
  without needing to manually source the venv script every time, e.g.:  
  ```sh
  ln -sr venv/bin/kupferbootstrap ~/.local/bin/
  ```

  The Makefile can do this for you:  
  ```sh
  make INSTALL_TARGET=~/.local/bin/kupferbootstrap install
  ```

  Just make sure `~/.local/bin` (or wherever you chose) is in your `$PATH`.
- It is recommended to abbreviate `kupferbootstrap` to `kbs` for even less typing.


## Quickstart
1. Initialize config with defaults, configure your device and flavour: `kupferbootstrap config init`
1. Initialize PKGBUILDs and caches: `kupferbootstrap packages init`
1. Build an image and packages along the way: `kupferbootstrap image build`


## Development

### Docker
Put `BUILD` (the default) into `docker_version.txt` to always rebuild kupferbootstrap from this directory;
otherwise the image is pulled from `registry.gitlab.com/kupfer/kupferbootstrap:$VERSION`,
where `$VERSION` is the contents of `docker_version.txt`.
