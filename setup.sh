#!/bin/sh
# Name: stewie-rice/setup.sh
# Description: bootstrap the and trigger the setup of the rice in a fresh Fedora installation.
# Usage: ./setup.sh [desktop|laptop]
# Author: Caleb Stewart <caleb.stewart94@gmail.com>

# Print a fatal error and exit with a non-zero exit status
fatal() {
  echo "[!] $@" >&2
  exit 1
}

TAGS=$1
if [ "$#" -ne 1 ]; then
  fatal "usage: $0 [desktop|laptop|tag]"
fi

# Install requirements for ansible install
echo "[+] installing git and python packages"
dnf install git python3 python3-pip python3-venv

# Clone the rice repo
echo "[+] cloning rice repository"
rm -rf /opt/rice >/dev/null 2>/dev/null
git clone https://github.com/calebstewart/stewie-rice.git /opt/rice || fatal "failed to clone rice repository"
cd /opt/rice || fatal "failed to enter rice directory"

# Setup a virtual environment for ansible
echo "[+] setting python virtual environment"
python3 -m venv env || fatal "failed to create virtual environment"

# Install ansible in the virtual environment
echo "[+] installing python requirements"
./env/bin/pip install . || fatal "failed to install python requirements"

# Install the 'ricectl' command
echo "[+] installing ricectl command"
ln -s /opt/rice/ricectl /usr/local/bin/ricectl || fatal "failed to install ricectl script"

# Apply ansible roles
echo "[+] applying ansible roles"
./ricectl apply
