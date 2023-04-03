# Fedora RICE Scripts
RICE scripts for configuring a Fedora desktop environment.

## Overview
This repo houses two components: an Ansible playbook and a command line utility.
The Ansible playbook is responsible for doing 98% of the configuration and
installation on the system. The `core` tag will setup some common tooling, the
SwayWM window manager with all my presets and scripts, and a functioning
development environment. Other tags may or may not be available for special
situations such as a laptop or macbook specific hardware configuration.

The command line utility is called `ricectl` and is meant to make the process
of iteratively applying and updating the RICE configuration and tools easier.
The `ricectl` command can be used to easily execute Ansible, update the
local RICE repository, and add/remove ansible tags.

## Installation
The installation process is expected to be run on a fresh installation of
Fedora. I have tested this from a default Fedora Workstation ISO in Gnome, but
it should in theory work from other spins or builds as well. Simply login to
the system, start a terminal and run the following:

``` sh
curl https://raw.githubusercontent.com/calebstewart/rice/main/setup.sh | sh
```

> NOTE: You should not run this with `sudo`. Instead, the setup script will use `sudo`
>       when needed, and mark log entries requiring administrative access with `SUDO`.

The setup script will ensure we have Python and git installed, and then clone
the RICE repository to `$HOME/.local/share/rice`. Next, it will setup a virtual
environment in `$HOME/.local/share/rice/env` for installing Ansible and `ricectl`.

After the `ricectl` and `ansible` packages are installed, the script will symlink
the `ricectl` binary to `/usr/local/bin` so that you have access to it normally.

The last thing the setup script does is run `ricectl status`, which will show the
current commit and tags that you have configured. At this point, you can add or
remove tags with the `ricectl add-tag` and `ricectl remove-tag` commands.

Once you have configured your tags, you are ready to apply the Ansible playbook!
Simply the following to kick off ansible. You will be prompted for the `BECOME`
password, which is your user password, which is used to elevate permissions as
needed.

``` sh
ricectl apply
```

## Updating (pulling changes)
For system packages, the `ricectl apply` command will perform a full `dnf` upgrade.
You can update the `ricectl` command itself and the Ansible playbooks with the
`ricectl sync` command.

## Pushing Changes
If you have made modifications to the ansible playbook, and want to push those
changes back to the remote repository, you'll need to navigate to
`$HOME/.local/share/rice`, make a commit, and push using standard `git` commands.
You will have to authenticate to GitHub. By default, the `setup.sh` script clones
the repository with `https`, but you can change the URL to use SSH (and therefore
SSH keys) with this command:

``` sh
cd ~/.local/share/rice
git remote set-url origin git@github.com:calebstewart/rice.git
```
