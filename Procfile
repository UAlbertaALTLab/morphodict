# Procfile for development work: use foreman(1) to run all the dictionary
# applications at once
#
# Note that foreman will by default read and apply your .env file,
# overriding any local environment variables set in your shell. One
# workaround is to tell it to read /dev/null instead, e.g.,
#
#     USE_TEST_DB=True foreman start -e /dev/null

rollup: npx rollup --config --watch
arpeng: ./arpeng-manage runserver
crkeng: ./crkeng-manage runserver
cwdeng: ./cwdeng-manage runserver
srseng: ./srseng-manage runserver
hdneng: ./hdneng-manage runserver
lacombe:  ./crk-Lacombeeng-manage runserver
