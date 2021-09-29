# Don’t load these settings files from new dictionaries, because they’ll
# try to set BASE_DIR, which is already set up for itwêwina.
#
# TODO: Figure out how to run tests against multiple dictionary sites.
collect_ignore = [
    "arpeng/site/settings.py",
    "crkeng/site/settings_mobile.py",
    "cwdeng/site/settings.py",
    "hdneng/site/settings.py",
    "srseng/site/settings.py",
    "srseng/site/settings_mobile.py",
]
