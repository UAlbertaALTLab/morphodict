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


define svg2png
inkscape --export-area-page $(PNG_EXPORT_OPTIONS) --export-type=png $< -o $@
optipng $@
endef

itwewina-32.png: PNG_EXPORT_OPTIONS=--export-width=32 --export-height=32
itwewina-32.png: itwewina.svg
	$(svg2png)

itwewina-192.png: PNG_EXPORT_OPTIONS=--export-width=192 --export-height=192
itwewina-192.png: itwewina.svg
	$(svg2png)

.PHONY: all
