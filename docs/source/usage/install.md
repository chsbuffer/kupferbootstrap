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
   pipx install -e .
   ```
   this will effectively run the following steps for you:

   1. Create a venv:
      ```sh
      python -m venv venv
      ```
   2. Install `kupferbootstrap` in editable mode:
      ```sh
      venv/bin/pip3 install -e .
      ```
   3. Symlink `kupferbootstrap` into your `$PATH`:
      ```sh
      sudo ln -s "$(pwd)/venv/bin/kupferbootstrap" ~/.local/bin/
      ```

   ```{Hint}
   For ease of use, we recommend aliasing `kupferbootstrap` to `kbs`.
   
   E.g. by putting the following into your `~/.bashrc`:
   
   ```sh
   alias kbs=kupferbootstrap
   ```
1. You should now be able to run `kupferbootstrap --help`!
