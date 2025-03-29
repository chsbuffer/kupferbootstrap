# Installation

1. Install Python 3, pip, venv and git.


   On Arch: `pacman -S base-devel python python-pip git --needed --noconfirm`

   If you're on a non-arch distro (i.e. you don't have pacman and pacstrap), you'll also need docker.

   ```{Hint}
   After installing Docker you will have to add your user to the `docker` group:

   `sudo usermod -aG docker "$(whoami)"`

   Then restart your desktop session for the new group to take effect.
   ```

2. Pick which Kupferbootstrap branch to clone: usually `dev`

3. Clone the repository:
   ```sh
   git clone -b INSERT_BRANCHNAME_HERE https://gitlab.com/kupfer/kupferbootstrap
   ```

4. Change into the folder:
   ```sh
   cd kupferbootstrap
   ```

5. Install:
   ```sh
   make install
   ```
   this will effectively run the following steps for you:

   5.1. Create a venv:
      ```sh
      python -m venv venv
      ```
   5.1. Install `kupferbootstrap`:
      ```sh
      venv/bin/pip3 install -e .
      ```
   5.1. Symlink `kupferbootstrap` into your `$PATH`:
      ```sh
      sudo ln -s "$(pwd)/venv/bin/kupferbootstrap" ~/.local/bin/
      ```

   ```{Hint}
   You can override the path and name that the kupferboostrap script file is symlinked to like so.

   Just make sure the destination directory is in your `$PATH`!

   ```sh
   make INSTALL_TARGET=~/.local/bin/my_custom_kbs_alias install
   ```
1. You should now be able to run `kupferbootstrap --help`!
