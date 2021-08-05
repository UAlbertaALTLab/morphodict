# Useful defaults to have enabled for essentially all Makefiles

# Enable bashisms, and if one part of a shell command fails, exit with an
# error instead of going on to the next command.
SHELL = /bin/bash -eu

# If an error is encountered building while building a file, delete the
# output, so that it doesn’t seem to valid on the next run of make.
.DELETE_ON_ERROR:
