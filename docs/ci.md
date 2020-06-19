Continuous Integration
======================

We use continuous integration (CI) to test and check our code on every
`git push`.


Serivces
--------

 - TravisCI — runs unit and integration tests
 - codecov — measures and tracks code coverage
 - Cypress — stores test recordings
 - GitHub Actions — reformats Python and JavaScript code on the default branch
 - redeploy (proprietary) — pulls the latest code on the production server


Cypress
-------

On TravisCI, the integration test run using this rule:

    npm run test:ci

Which, in turn, does the following:

 - `USE_TEST_DB=true pipenv run dev &` — Starts the Django server in the **background**
 - `wait-on tcp:127.0.0.1:8000` — waits for the Django server to respond to HTTP requests
 - `$(npm bin)/cypress run $CYPRESS_OPTS` — runs the Cypress integration
   tests

`$CYPRESS_OPTS` is intended to be either empty or `--record`. If set to
`--record`, it will upload recordings to the Cypress Dashboard. Note
that **if there is no more room for recordings** on our Cypress plan, **the
build will fail**.
