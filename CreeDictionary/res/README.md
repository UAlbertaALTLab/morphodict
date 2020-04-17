# Data files

> Convenient variable `utils.shared_res_dir` is a `pathlib.Path` object that refers to this directory

## test_db_words.txt

newline separated cree words that goes into `test_db.sqlite3`

Comments should be added using preceding hash sign.

Empty lines are allowed and will be ignored

After editing the file `$ manage-db build-test-db [-m|--multi-processing N]` to rebuild the test database.

## crk.altlabel.tsv

labels for fst tags categorized by user-friendliness. The source [`crk.altlabel`](https://gtsvn.uit.no/langtech/trunk/langs/crk/inc/paradigms/crk.altlabel) file.

## W_aggr_corp_morph_log_freq.txt

Morpheme frequencies, used in result sorting. Sits at `/data/texts/crk/dicts/itwewina/` on Sapir and is subject to updates. 