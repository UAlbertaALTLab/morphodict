# Fakes

This directory contains fake versions of libraries that we don’t have on
mobile right now due to compilation difficulty. These fake modules can be
imported, but no code in them can actually be called.

Deciding not to call code is fairly straightforward to do through creating
Django settings variables and adding `if` statements throughout. But not
even *importing* the code gets trickier, because some import stuff happens
before the Django settings are configured. Hence, this workaround.
