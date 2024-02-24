# kupferbootstrap

Kupfer Linux bootstrapping tool - drives pacstrap, makepkg, chroot, mkfs and fastboot, just to name a few.


## Documentation

Detailed docs for the main branch are available online at https://kupfer.gitlab.io/kupferbootstrap/

You can also build and view the docs locally:
```sh
cd docs/ && \
make && \
make serve
```

This will run a webserver on localhost:9999. Access it like `firefox http://localhost:9999/`


## Installation
0. If you're not on ArchLinux (i.e. don't have `pacman`, `makepkg`, etc. available in your $PATH), install Docker and add yourself to the docker group.
1. Craate a python venv: `python3 -m venv venv`
1. Activate it: `source venv/bin/activate`
1. Install KBS: `pip3 install .`

Then run `kupferbootstrap`.

### Pro Tip:

- You can add a shell alias for `$(PWD)/venv/bin/kupferbootstrap` or create a symlink to it at `/usr/local/bin/kuperbootstrap` for quick access without needing to manually source the venv script every time.
- It is recommended to abbreviate `kupferbootstrap` to `kbs` for even less typing.


## Quickstart
1. Initialize config with defaults, configure your device and flavour: `kupferbootstrap config init`
1. Initialize PKGBUILDs and caches: `kupferbootstrap packages init`
1. Build an image and packages along the way: `kupferbootstrap image build`


## Development

### Docker
Put `BUILD` (the default) into `docker_version.txt` to always rebuild kupferboostrap from this directory; otherwise the image is pulled from `registry.gitlab.com/kupfer/kupferbootstrap:$VERSION`, where `$VERSION` is the contents of `docker_version.txt`.
