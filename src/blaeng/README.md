# Generating a new site from scratch

These are all the instructions I followed to create this new version.

```
./crkeng-manage newdictsite --port 8011 -v 2 bla eng
# Add blaeng to morphodict/src/conftest.py
# Add MORPHODICT_LANGUAGE_ENDONYM to src/blaeng/site/settings.py
# Add many other details, copying from Woods Cree settings.py, including:
# MD_SOURCE_LANGUAGE_NAME MD_SOURCE_LANGUAGE_SHORT_NAME MD_ORTHOGRAPHY MD_DICTIONARY_NAME
./blaeng-manage migrate
./blaeng-manage ensurecypressadminuser --superuser
./blaeng-manage ensuretestdb
# MISSING TRANSDUCERS 

```
Generating from the instructions set!
`git clone giellalt/lang-bla`
after generating the FSTs with the default infrastructure:
```
hfst-xfst
```
And run:
```
read lexc src/fst/morphology/lexicon.lexc
define Morphology
source src/fst/bla-phonology.xfscript
define Phonology
regex ~[ $[ "+Err/Frag" ]];
define removeFragments

regex ~[ $[ "+Err/Orth" ]];
define removeNonStandardForms
regex $[ "+N" | "+V" | "+Ipc" | "+Pron" ];
define selectDictPOS
set flag-is-epsilon ON
regex [ selectDictPOS .o. removeNonStandardForms .o. removeFragments .o. Morphology .o. Phonology ];
save stack generator-gt-dict-norm.hfst
define NormativeGenerator
regex [ [ "<" | ">" | "/" ] -> 0 ];
define removeBoundaries
load src/fst/orthography/spellrelax.compose.hfst
define SpellRelax
regex [ selectDictPOS .o. removeFragments .o. Morphology .o. Phonology .o. removeBoundaries .o. SpellRelax ];
# regex [ NormativeGenerator .o. removeBoundaries .o. SpellRelax ];
invert net
save stack analyser-gt-dict-desc.hfst
define DescriptiveAnalyser
```


And then we create the `hfstol` files with:

```
hfst-fst2fst -O -i INPUT.hfst -o OUTPUT.hfstol
```

After this, `./blaeng-manage ensuretestdb` works.

```
./blaeng-manage importjsondict src/blaeng/resources/dictionary/blaeng_test_db.importjson
```
