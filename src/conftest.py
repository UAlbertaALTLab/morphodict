# don’t load these settings files, because they’ll try to set BASE_DIR. To be
# revisited when figuring out how to run tests against multiple dictionary
# sites.
collect_ignore = [
    "arpeng/site/settings.py",
    "cwdeng/site/settings.py",
    "srseng/site/settings.py",
]
