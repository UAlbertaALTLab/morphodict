FROM python:3.9-slim-buster

LABEL maintainer="Eddie Antonio Santos <Eddie.Santos@nrc-cnrc.gc.ca>"

# (2021-01-15): This Dockerfile was derived from Gūnáhà:
#  - https://github.com/UAlbertaALTLab/gunaha/blob/master/Dockerfile
#
# Changes:
#
#  - use Gunicorn instead of uwsgi; I'm not sure why I chose uwsgi for Gūnáhà,
#    but I've got itwêwina working with Gunicorn, so I'm gonna stick with that
#


# Directories:
#
# /app — the app code will live here
#

# Choose an ID that will be consistent across all machines in the network
# To avoid overlap with user IDs, use an ID over
# /etc/login.defs:/UID_MAX/, which defaults to 60,000
ARG UID_GID=60003
ARG EXPOSE_PORT=8000

ARG NODE_VERSION=v12.20.2

# Install Node + npm
# (note: default npm is too old for the apt-install'd version of NodeJS??!?!?!)
WORKDIR /tmp
ADD https://nodejs.org/dist/${NODE_VERSION}/node-${NODE_VERSION}-linux-x64.tar.gz /tmp/node.tar.gz
RUN tar xf node.tar.gz\
 && mv node-${NODE_VERSION}-linux-x64 /opt/node
ENV PATH="/opt/node/bin:${PATH}"

# Create the user/group for the application
RUN groupadd --system --gid ${UID_GID} itwewina \
 && useradd --no-log-init --system --gid itwewina --uid ${UID_GID} itwewina --create-home
# Install and build dependencies,
# then remove build-time dependencies to keep the image slim!
RUN set -ex \
 && BUILD_DEPS=" \
    build-essential \
    tini \
    " \
 && apt-get update \
 && apt-get install -y --no-install-recommends $BUILD_DEPS \
 && pip install pipenv \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir /data/ /app/ \
 && chown itwewina /data /app

USER itwewina

WORKDIR /app/
ADD --chown=itwewina . /app/

# Install Python and NodeJS apps
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy\
 && npm install --only=production

# Build the application:
ENV NODE_ENV=production
RUN npm run build \
 && /app/.venv/bin/python CreeDictionary/manage.py collectstatic --noinput

# Gunicorn will listen on this port:
EXPOSE ${EXPOSE_PORT}

# Among other things -- see
# https://github.com/krallin/tini#tini---a-tiny-but-valid-init-for-containers
# -- this makes typing Ctrl-C into docker-compose work
ENTRYPOINT ["tini", "--"]

WORKDIR /app/CreeDictionary
ENV EXPOSE_PORT=${EXPOSE_PORT}

CMD /app/.venv/bin/gunicorn \
    --access-logfile - \
    --bind 0.0.0.0:${EXPOSE_PORT} \
    CreeDictionary.wsgi:application
