# Procfile for development work: use foreman(1) to run all the dictionary
# applications at once
#
# Note that foreman will by default read and apply your .env file,
# overriding any local environment variables set in your shell. One
# workaround is to tell it to read /dev/null instead, e.g.,
#
#     USE_TEST_DB=True foreman start -e /dev/null

rollup: npx rollup --config --watch
arpeng: ./arpeng-manage runserver 0.0.0.0:8007
crkeng: ./crkeng-manage runserver 0.0.0.0:8000
cwdeng: ./cwdeng-manage runserver 0.0.0.0:8005
srseng: ./srseng-manage runserver 0.0.0.0:8009
hdneng: ./hdneng-manage runserver 0.0.0.0:8010
lacombe:  ./crkLacombeeng-manage runserver 0.0.0.0:8016
blaeng: ./blaeng-manage runserver 0.0.0.0:8011
stoeng: ./stoeng-manage runserver 0.0.0.0:8018
ciweng: ./ciweng-manage runserver 0.0.0.0:8019
