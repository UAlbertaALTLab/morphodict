Files in this directory are not checked in because they are collected here by
`manage.py collectstatic` from the `static` directories of each app, as well as
from `STATICFILES_DIRS`.

See https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#collectstatic

Note that you may need to build some of the JS/CSS assets with `npx rollup
-c` first, before running `collectstatic`.
