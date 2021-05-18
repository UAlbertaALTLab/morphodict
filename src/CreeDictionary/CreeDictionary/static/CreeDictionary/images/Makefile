# Create the favicons from itwewina.svg!
#
# Usage:
# 	make -j
#
#
# Requires:
#  - Inkscape 1.0+
#  - optipng (brew install optipng)

all: itwewina-32.png itwewina-192.png itwewina-social.png

######################### .svg to .png canned recipe #########################

# see: https://www.gnu.org/software/make/manual/html_node/Canned-Recipes.html
# see: https://stackoverflow.com/a/5036468/6626414
define svg2png
inkscape --export-area-page $(PNG_EXPORT_OPTIONS) --export-type=png $< -o $@
optipng $@
endef


############################### Custom targets ###############################

itwewina-32.png: PNG_EXPORT_OPTIONS=--export-width=32 --export-height=32
itwewina-32.png: itwewina.svg
	$(svg2png)

itwewina-192.png: PNG_EXPORT_OPTIONS=--export-width=192 --export-height=192
itwewina-192.png: itwewina.svg
	$(svg2png)


############################### Pattern rules ################################

# How to create a .png from an .svg. Default settings:
%.png: %.svg
	$(svg2png)


.PHONY: all
