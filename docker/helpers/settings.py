from pathlib import Path

from .app import App

# The directory containing the docker-compose file
DOCKER_COMPOSE_DIR = Path(__file__).parent.parent


# Port assignments and UIDs are tracked at:
# https://github.com/UAlbertaALTLab/deploy.altlab.dev/blob/master/docs/application-registry.tsv

APP_INFO = {
    "crkeng": {"port": 8011, "uwsgi_stats_port": 9011},
    "cwdeng": {"port": 8012, "uwsgi_stats_port": 9012},
    "srseng": {"port": 8013, "uwsgi_stats_port": 9013},
    "arpeng": {"port": 8014, "uwsgi_stats_port": 9014},
    "hdneng": {"port": 8015, "uwsgi_stats_port": 9015},
    "lacombe": {"port": 8016, "uwsgi_stats_port": 9016},
}

APPS = [App(k, **v) for k, v in APP_INFO.items()]
