# Create the favicons from itwewina.svg!
#
# Usage:
# 	make -j
#
#
# Requires:
#  - Inkscape 1.0+
#  - optipng (brew install optipng)

all: itwewina-32.png itwewina-192.png


itwewina-32.png: itwewina.svg
	inkscape --export-area-page -w 32 -h 32 --export-type=png $< -o $@
	optipng $@

itwewina-192.png: itwewina.svg
	inkscape --export-area-page -w 192 -h 192 --export-type=png $< -o $@
	optipng $@

.PHONY: all
