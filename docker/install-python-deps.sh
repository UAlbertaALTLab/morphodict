#!/bin/sh
# -*- coding: UTF-8 -*-

# Install dependencies just for the Python application
# Based on: https://pythonspeed.com/articles/system-packages-docker/

# Exit at the slightlest error:
set -eux

export DEBIAN_FRONTEND=noninteractive


# Pip invokes gcc/g++, but they are not runtime deps ¯\_(ツ)_/¯
apt-get update
apt-get -y upgrade
apt-get -y install --no-install-recommends gcc g++

# Actually do the pip installin'
python3 -m pip install -r requirements.txt

# Clean caches and the mess we've made in this script.
apt-get -y remove gcc g++
apt-get -y autoremove
apt-get clean
rm -rf /var/lib/apt/lists/*
