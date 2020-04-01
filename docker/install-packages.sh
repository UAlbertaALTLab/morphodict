#!/bin/sh

# Install packages in Debian Buster
# Based on: https://pythonspeed.com/articles/system-packages-docker/

# Exit at the slightly error:
set -eux

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get -y upgrade

apt-get -y install --no-install-recommends hfst git

# Clean caches and the mess we've made in this script.
apt-get clean
rm -rf /var/lib/apt/lists/*
