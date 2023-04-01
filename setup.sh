#!/bin/sh
# Name: stewie-rice/setup.sh
# Description: bootstrap the and trigger the setup of the rice in a fresh Fedora installation.
# Usage: ./setup.sh [clone-path]
# Author: Caleb Stewart <caleb.stewart94@gmail.com>

BOLD=$(tput bold)
RESET=$(tput sgr0)

# Print a fatal error and exit with a non-zero exit status
fatal() {
  echo "[!] $@" >&2
  exit 1
}

if [ "$#" -gt 1 ]; then
  fatal "usage: setup.sh [git-clone-path]"
fi

# Default clone location
mkdir -p ~/.local/share
CLONE_PATH=$(realpath -m "~/.local/share/rice")

if [ "$#" -eq 1 ]; then
  CLONE_PATH=$(realpath -m  "$1")
fi

# Ensure the clone path does not exist
[ -f "$CLONE_PATH" ] || [ -d "$CLONE_PATH" ] && fatal "git clone path already exists"

# Install requirements for ansible install
echo "[+] ${BOLD}SUDO${RESET} installing git and python packages with dnf"
sudo dnf install git python3 python3-pip python3-venv || fatal "failed to install git and python3"

# Clone the rice repo
echo "[+] cloning rice repository"
git clone https://github.com/calebstewart/rice.git "$CLONE_PATH" || fatal "failed to clone rice repository"
cd "$CLONE_PATH" || fatal "failed to enter rice directory"

# Setup a virtual environment for ansible
echo "[+] setting python virtual environment"
python3 -m venv env || fatal "failed to create virtual environment"

# Install ansible in the virtual environment
echo "[+] installing python requirements"
./env/bin/pip install . || fatal "failed to install python requirements"

# Install the 'ricectl' command
echo "[+] installing ricectl command to /usr/local/bin/"
mkdir -p "$HOME/.local/bin/"
ln -s "$CLONE_PATH/env/bin/ricectl" "$HOME/.local/bin/ricectl" || fatal "failed to install ricectl script"

# Install the ricectl tab completion scripts
"$CLONE_PATH/env/bin/ricectl" --install-completion || echo "[!] failed to install ricectl completion script"

# Setup an initial user configuration with the repo location
if ! [ -f "$HOME/.config/rice/config.toml" ]; then
  mkdir -p "$HOME/.config/rice"
  echo 'repo = "'"$CLONE_PATH"'"' > "$HOME/.config/rice/config.toml"
fi
