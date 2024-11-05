## Phrase translation

The process to update the auto-translated phrases is as follows:

 1. First, get the latest FSTs. In the `lang-crk` repo, `cd src && make -f
    quick.mk fsts.zip`

 2. Copy the generated `transcriptor-cw-eng*` files to
    `morphodict/resources/fst` in this repo.

 3. Run the unit tests: `pipenv run pytest src`

 4. The english phrase FSTs are used:
    - By the `importjsondict` django command, which populates the auto definitions
      for every inflected wordform when passed the `--translate-wordforms` flag (which is the default).  **There is no separate command to populate translated wordforms since 2022**.
    - During search, when building a `PhraseAnalyzedQuery` or an `AnalyzedQuery`
    - In the fst_tool admin interface
  
