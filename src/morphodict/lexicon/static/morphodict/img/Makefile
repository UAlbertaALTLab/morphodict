TOP_DIR := $(shell git rev-parse --show-toplevel)

include ${TOP_DIR}/src/mk/common.mk

all: morphodict-default-logo-32.png morphodict-default-logo-192.png
.PHONY: all

include ${TOP_DIR}/src/mk/svg2png.mk

morphodict-default-logo-32.png: PNG_EXPORT_OPTIONS=--export-width=32 --export-height=32
morphodict-default-logo-32.png: morphodict-default-logo.svg
	$(svg2png)
clean::
	rm -f morphodict-default-logo-32.png

morphodict-default-logo-192.png: PNG_EXPORT_OPTIONS=--export-width=192 --export-height=192
morphodict-default-logo-192.png: morphodict-default-logo.svg
	$(svg2png)
clean::
	rm -f morphodict-default-logo-192.png
