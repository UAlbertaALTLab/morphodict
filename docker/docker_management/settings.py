from pathlib import Path

from docker_management.app import App

DIR = Path(__file__).parent.parent

# Port assignments are tracked at:
# https://github.com/UAlbertaALTLab/deploy.altlab.dev/blob/master/docs/application-registry.tsv
#
# If you want to run the Cypress tests on the staging container, use
# the following:
#
#     CYPRESS_BASE_URL=http://localhost:8001 npx cypress open
#
# See: https://docs.cypress.io/guides/guides/environment-variables.html#We-can-move-this-into-a-Cypress-environment-variable

APP_INFO = {
    "crkeng": {"name": "itwewina", "port": 8011, "uwsgi_stats_port": 9011},
    "cwdeng": {"name": "itwiwina", "port": 8012, "uwsgi_stats_port": 9012},
    "srseng": {"name": "gunaha", "port": 8013, "uwsgi_stats_port": 9013},
    "arpeng": {"port": 8014, "uwsgi_stats_port": 9014},
}


APPS = [App(k, **v) for k, v in APP_INFO.items()]
