TOP_DIR := $(shell git rev-parse --show-toplevel)

include ${TOP_DIR}/src/mk/common.mk

all: itwewina-social.png
.PHONY: all

clean::
	rm -f itwewina-social.png

include ${TOP_DIR}/src/mk/svg2png.mk
