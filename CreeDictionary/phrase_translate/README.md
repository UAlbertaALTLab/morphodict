## Phrase translation

The process to update the auto-translated phrases is as follows:

 1. First, get the latest FSTs. In the `lang-crk` repo, `cd src && make -f
    quick.mk fsts.zip`

 2. Copy the generated `transcriptor-cw-eng*` files to
    `CreeDictionary/res/fst` in this repo.

 3. Run the unit tests: `pipenv run pytest CreeDictionary`

 4. Run the translation script in jsonl-only mode to get a file containing
    all the translations for review:

        pipenv run CreeDictionary/manage.py translatewordforms --jsonl-only translations.jsonl

    You will need to run this against a database that has had the full
    dictionary imported for this to be very useful.

 5. Commit and make a pull request

 6. After the pull request passes tests, is reviewed, merged, and
    auto-deployed to `itw.altlab.dev`, SSH there and run

        cd /opt/docker-compose/itwewina/cree-intelligent-dictionary/docker \
          && docker-compose exec itwewina ./manage.py translatewordforms

    If the process fails partway with a “Database is Locked” error, you can
    make a copy of the database, run the translation against it, then copy
    the database back, at the risk of losing any changes made to the
    production database between the two copies. Currently those lost
    changes would be limited to user account creation and password updates.
