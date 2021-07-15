SHELL = /bin/bash -eu
.DELETE_ON_ERROR:

# Makefile to build {generator-gt-norm,analyser-gt-{norm,desc}}.hfstol from a
# single .hfst file.


# Path to checkout of <https://github.com/UAlbertaALTLab/fst-exchange>, which
# contains pre-built FSTs for things that aren’t yet integrated into the Giella
# infrastructure
FST_EXCHANGE = $(HOME)/src/fst-exchange
# Path to checkout of https://github.com/giellalt/lang-srs
LANG_SRS = $(HOME)/src/lang-srs

.PHONY: all test

test: all
	echo istsiy | hfst-optimized-lookup analyser-gt-desc.hfstol
	echo īstsīy | hfst-optimized-lookup analyser-gt-norm.hfstol
	echo ītsīy+V+I+Ipfv+SbjSg1 | hfst-optimized-lookup generator-gt-norm.hfstol

all: generator-gt-norm.hfstol analyser-gt-norm.hfstol analyser-gt-desc.hfstol

generator-gt-norm.hfst: $(FST_EXCHANGE)/srs-generator-gt-norm.hfst
	cp $< $@

analyser-gt-desc.hfst: spellrelax.hfst
	hfst-compose -F -1 generator-gt-norm.hfst -2 $< \
	    | hfst-invert -o $@

spellrelax.hfst: $(LANG_SRS)/src/orthography/spellrelax.regex
	hfst-regexp2fst --semicolon --input $< --output $@

analyser-gt-norm.hfst: generator-gt-norm.hfst
	hfst-invert --input $< --output $@


%.hfstol: %.hfst
	hfst-fst2fst --optimized-lookup-unweighted --input $< --output $@

clean::
	rm -f *.hfst *.hfstol
