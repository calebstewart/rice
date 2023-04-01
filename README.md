# Fedora RICE Scripts
This repository houses my automated configuration and setup scripts for Fedora.
The project was motivated by setting up laptops where I often use Fedora. This
allows me to wipe my laptop, but get back up and running comfortably quickly and
easily.

## Assumptions
The main component to this repository is an Ansible playbook which sets up my
system in a repeatable and comfortable way with SwayWM, and all the custom
bells and whistles I'm used to.

I'm not going to list out every piece of software I install. If you're curious,
you can check out the Ansible playbook for more details.

The playbook assumes you have installed Fedora (most likely Workstation) with
the default ISO. This means Gnome/GDM is by default the DM/WM. Ansible will
install and configure SwayWM, but you will need to manually select Sway from
the GDM login screen the first time after installation. I keep GDM since it's
the cleanest DM around, and is already installed by Fedora Workstation by default.

I explicitly do not attempt to remove Gnome and keep GDM, because removing Gnome
normally causes lots of harm. This is annoying, but not the end of the world.

## Installation
Installation is intended to be as simple as possible. On a base installation,
simply login and run the following:

``` sh
curl https://raw.githubusercontent.com/calebstewart/rice/main/setup.sh | sh
```

I normally detest `curl | sh` type installation commands, but seeing as this
is my own tool hosted in my own repository, I've decided to ignore my inclinations.

> NOTE: **This script should not be run with `sudo`!** The script will clone and
>       setup the RICE repo within your user's home directory, and use `sudo`
>       itself only when needed (e.g. installing software).

This script will do the following:
1. Install `git`, `python3`, `python3-pip` and `python3-venv`.
2. Clone this repository to `$HOME/.local/share/rice`.
3. Create a Python virtual environment to `$HOME/.local/share/rice/env`.
4. Install the `ricectl` package to the new environment.
5. Symlink the `ricectl` binary to `/usr/local/bin/ricectl`.
6. Install completion scripts for the current shell for `ricectl`.
6. If no config exists, a base configuration is installed to `$HOME/.config/rice/config.toml`.

The setup script will not automatically run Ansible. This is because the user may
want to configure extra Ansible tags or other changes before applying the playbook.
At this point, you

## Initial Setup
After installing the `ricectl` command, you can use the `ricectl config` commands
to customize your installation before applying the Ansible playbook. Once you have
configured your installation, you can use the following command to apply the
Ansible playbook:

``` sh
ricectl apply
```

This command will execute Ansible with your configured tags and install/configure
all requried software. After setup, it is recommended that you either reboot or
fully logout.
