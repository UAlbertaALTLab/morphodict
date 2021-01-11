all: itwewina-32.png itwewina-192.png


itwewina-32.png: itwewina.svg
	inkscape --export-area-page -w 32 -h 32 --export-type=png $< -o $@
	optipng $@

itwewina-192.png: EXPORT_SIZE=192
itwewina-192.png: itwewina.svg
	inkscape --export-area-page -w 192 -h 192 --export-type=png $< -o $@
	optipng $@
