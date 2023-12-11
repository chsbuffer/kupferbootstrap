# FAQ


```{contents} Table of Contents
:class: this-will-duplicate-information-and-it-is-still-useful-here
:depth: 3
```


## Which devices are currently supported?

Currently very few!  
See [the `devices` repo](https://gitlab.com/kupfer/packages/pkgbuilds/-/tree/dev/device). We use the same codenames as [postmarketOS](https://wiki.postmarketos.org/wiki/Devices) (although we prefix them with the SoC)


## How to port a new device or package?

See [Porting](../porting)

## How to build a specific package

See also: The full [`kupferbootstrap packages build` docs](/cli/packages#kupferbootstrap-packages-build)

### Example

For rebuilding `kupfer-config` and `crossdirect`, defaulting to your device's architecture

```sh
kupferbootstrap packages build [--force] [--arch $target_arch] kupfer-config crossdirect
```


### By package path
You can also use the a path snippet (`$repo/$pkgbase`) to the PKGBUILD folder as seen inside your pkgbuilds.git:

```sh
kupferbootstrap packages build [--force] main/kupfer-config cross/crossdirect
```

