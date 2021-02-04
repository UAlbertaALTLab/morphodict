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
ARG UID_GID=60002
ARG WSGI_USER=itwewina

# Create the user/group for the application
RUN groupadd --system --gid ${UID_GID} ${WSGI_USER} \
 && useradd --no-log-init --system --gid ${WSGI_USER} --uid ${UID_GID} ${WSGI_USER} --create-home

# TODO: move package.json dependences from build and test
#  - [ ] must document in development guide

# Install and build dependencies,
# then remove build-time dependencies to keep the image slim!
RUN set -ex \
 && BUILD_DEPS=" \
    build-essential \
    nodejs \
    " \
 && apt-get update \
 && apt-get install -y --no-install-recommends $BUILD_DEPS \
 && pip install pipenv \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir /data/ /app/ \
 && chown ${WSGI_USER} /data /app

USER ${WSGI_USER}

# Setup Python deps
ADD Pipfile /app/Pipfile
ADD Pipfile.lock /app/Pipfile.lock

WORKDIR /app/

RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

# Copy the application files. Make sure .dockerignore is setup properly so it
# doesn't copy unnecessary files
ADD . /app/
RUN npm ci \
 && npm run build \

# Gunicorn will listen on this port:
EXPOSE 8000

# TODO: put static files in a good place
# These should be built and

# Where to find the WSGI file
CMD /app/.venv/bin/gunicorn --bind 127.0.0.1:8000 CreeDictionary.wsgi:application
