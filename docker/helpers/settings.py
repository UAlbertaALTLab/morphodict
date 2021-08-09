from pathlib import Path

from .app import App

DIR = Path(__file__).parent.parent


# Port assignments and UIDs are tracked at:
# https://github.com/UAlbertaALTLab/deploy.altlab.dev/blob/master/docs/application-registry.tsv

APP_INFO = {
    "crkeng": {"name": "itwewina", "port": 8011, "uwsgi_stats_port": 9011},
    "cwdeng": {"name": "itwiwina", "port": 8012, "uwsgi_stats_port": 9012},
    "srseng": {"name": "gunaha", "port": 8013, "uwsgi_stats_port": 9013},
    "arpeng": {"port": 8014, "uwsgi_stats_port": 9014},
}

APPS = [App(k, **v) for k, v in APP_INFO.items()]
