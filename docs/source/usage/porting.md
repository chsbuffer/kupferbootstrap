# Porting
## Porting devices

### Homework
Before you can get started porting a device, you'll need to do some research:

1. Familiarize yourself with git basics.
1. Familiarize yourself with Arch Linux packaging, i.e. `PKGBUILD`s and `makepkg`
1. Familiarize yourself with the postmarketOS port of the device.
   ```{warning}
    If there is no postmarketOS port yet, you'll probably need to get deep into kernel development.  
    We suggest [starting with a port to pmOS](https://wiki.postmarketos.org/wiki/Porting_to_a_new_device) then, especially if you're not familiar with the process already.
    ```

### Porting
1. Navigate to your pkgbuilds checkout
1. Follow the [general package porting guidelines](#porting-packages) to create a device-, kernel- and probably also a firmware-package for the device and SoC. Usually this roughly means porting the postmarketOS APKBUILDs to our PKGBUILD scheme.  
   You can get inspiration by comparing existing Kupfer ports (e.g. one of the SDM845 devices) to the [postmarketOS packages](https://gitlab.com/postmarketOS/pmaports/-/tree/master/device) for that device.
   Usually you should start out by copying and then customizing the Kupfer packages for a device that's as similar to yours as possible, i.e. uses the same or a related SoC, if something like that is already available in Kupfer.
   ```{hint} Package Repos:
   Device packages belong into `device/`, kernels into `linux/` and firmware into `firmware/`.
   ```
1. When submitting your MR, please include some information:
    - what you have found to be working, broken, and not tested (and why)
    - any necessary instructions for testing
    - whether you'd be willing to maintain the device long-term (test kernel upgrades, submit device package updates, etc.)


### Gotchas

Please be aware of these gotchas:
- As of now, Kupfer only really supports platforms using Android's `aboot` bootloader, i.e. ex-Android phones. In order to support other boot modes (e.g. uboot on the Librem5 and Pine devices), we'll need to port and switch to postmarketOS's [boot-deploy](https://gitlab.com/postmarketOS/boot-deploy) first and add support for EFI setups to Kupferbootstrap.


## Porting packages

### Homework
Before you can get started, you'll need to do some research:

1. Familiarize yourself with git basics.
1. Familiarize yourself with Arch Linux packaging, i.e. `PKGBUILD`s and `makepkg`

### Development

```{warning}
Throughout the process, use git to version your changes.  
- Don't procrastinate using git or committing until you're "done" or "have got something working", you'll regret it.  
- Don't worry about a "clean" git history while you're developing; we can squash it up later.
- \[Force-]Push your changes regularly, just like committing. Don't wait for perfection.
```
1. Create a new git branch for your package locally.
   ```{hint}
   It might be a good ideaa to get into the habit of prefixing branch names with \[a part of] your username and a slash like so:  
   `myNickname/myFeatureNme`  
   This makes it easier to work in the same remote repo with multiple people.
   ```
1. 
   ```{note}
   The pkgbuilds git repo contains multiple package repositories, represented by folders at the top level (`main`, `cross`, `phosh`, etc.).  
   ```
   Try to choose a sensible package repo for your new packages and create new folders for each `pkgbase` inside the repo folder.
1. Navigate into the folder of the new package and create a new `PKGBUILD`; fill it with life!
1. **`_mode`**: Add the build mode at the top of the PKGBUILD.
   ```{hint}
   If you're unsure what to pick, go with `_mode=host`. It'll use `crossdirect` to get speeds close to proper cross-compiling.
   ```
   This determines whether it's built using a foreign-arch chroot (`_mode=host`) executed with qemu-user, or using real cross-compilation (`_mode=cross`) from a host-architecture chroot, but the package's build tooling has to specifically support the latter, so it's mostly useful for kernels and uncompiled packages.
1. **`_nodeps`**: (Optional) If your package doesn't require its listed dependencies to build
   (usually because you're packaging a meta-package or only configs or scripts)
   you can add `_nodeps=true` as the next line after the `_mode=` line to speed up packaging.
   `makedeps` are still installed anyway.
1. Test building it with `kupferbootstrap packages build $pkgbname`
1. For any files and git repos downloaded by your PKGBUILD,
   add them to a new `.gitignore` file in the same directory as your `PKGBUILD`.  
   ```{hint}
   Don't forget to `git add` the new `.gitignore` file!
   ```
1. Run `kupferbootstrap packages check` to make sure the formatting for your PKGBUILDs is okay.
   ```{warning}
   This is **not** optional. MRs with failing CI will **not** be merged.
   ```

### Pushing
1. Fork the Kupfer pkgbuilds repo on Gitlab using the Fork button
1. Add your fork's **SSH** URI to your local git repo as a **new remote**: `git remote add fork git@gitlab...`
1. `git push -u fork $branchname` it

### Submitting the MR
When you're ready, open a Merge Request on the Kupfer pkgbuilds repo.

```{hint}
Prefix the MR title with `Draft: ` to indicate a Work In Progress state.
```

