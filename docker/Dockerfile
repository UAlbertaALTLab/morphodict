# = CHANGELOG =
#
# 2021-02-19:
#
#  - Use a multi-stage build to keep the application image small
#
# 2021-01-15:
#
#  - This Dockerfile was derived from Gūnáhà:
#    https://github.com/UAlbertaALTLab/gunaha/blob/master/Dockerfile
#  - use Gunicorn instead of uwsgi; I'm not sure why I chose uwsgi for Gūnáhà,
#    but I've got itwêwina working with Gunicorn, so I'm gonna stick with that
#

################################ Build stage #################################
FROM python:3.9-slim-buster AS builder

LABEL maintainer="Eddie Antonio Santos <Eddie.Santos@nrc-cnrc.gc.ca>"

ARG MORPHODICT_UID_GID=60006
ARG NODE_VERSION=v12.20.2

# Install Node + npm
# (note: default npm is too old for the apt install'd version of NodeJS??!?!?!)
WORKDIR /tmp
ADD https://nodejs.org/dist/${NODE_VERSION}/node-${NODE_VERSION}-linux-x64.tar.gz /tmp/node.tar.gz
RUN tar xf node.tar.gz \
 && mv node-${NODE_VERSION}-linux-x64 /opt/node
ENV PATH="/opt/node/bin:${PATH}"

# Create the non-root user/group that will own the application code
RUN groupadd --gid ${MORPHODICT_UID_GID} morphodict \
 && useradd --no-log-init --gid morphodict \
    --uid ${MORPHODICT_UID_GID} morphodict --create-home
# Install and build dependencies,
# then remove build-time dependencies to keep the image slim!
RUN set -ex \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    libfoma0 \
    git `# for installing python packages direct from github` \
 && rm -rf /var/cache/apt \
 && pip install pipenv \
 && mkdir /app/ \
 && chown morphodict /app

USER morphodict

WORKDIR /app/

# Install Python and NodeJS dependencies
ADD Pipfile Pipfile.lock package.json package-lock.json /app/
# On Andrew’s linux machine, docker builds were sometimes ridiculously slow
# without this option. npm would try to download/install(?) too many packages
# all at once and some sort of resource would get exhausted leading to hangs.
RUN echo maxsockets=4 > ~/.npmrc
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy \
 && npm install --loglevel=verbose --only=production

# Add everything else now:
ADD --chown=morphodict . /app/

# pre-compile all .py files
RUN python -m compileall -q .

# Build the application:
ENV NODE_ENV=production
RUN npm run build \
 && set -eu \
 `# the docker image contains assets for all language pairs` \
 && for MANAGE_COMMAND in *-manage; do \
        echo ${MANAGE_COMMAND} collectstatic && \
        /app/.venv/bin/python `# .venv python sees libs from pipenv` \
            ./${MANAGE_COMMAND} collectstatic --noinput; \
    done

############################# Application image ##############################

FROM python:3.9-slim-buster
LABEL maintainer="Eddie Antonio Santos <Eddie.Santos@nrc-cnrc.gc.ca>"

# Choose an ID that will be consistent across all machines in the network
# To avoid overlap with user IDs, use an ID over
# /etc/login.defs:/UID_MAX/, which defaults to 60,000
ARG MORPHODICT_UID_GID=60006
ARG MORPHODICT_RUN_UID_GID=60007
ARG TINI_VERSION=v0.19.0

RUN set -ex \
 && apt-get update \
 && apt-get install -y --no-install-recommends tini libfoma0 \
 && rm -rf /var/cache/apt

# Create the user/group that will run the application code
RUN set -xv ; groupadd --gid ${MORPHODICT_RUN_UID_GID} morphodict-run \
 && useradd --no-log-init --gid morphodict-run \
    --uid ${MORPHODICT_RUN_UID_GID} morphodict-run --create-home
# Create the non-root user/group that will own the application code;
# this user also belongs to the runtime group
RUN set -xv ; groupadd --gid ${MORPHODICT_UID_GID} morphodict \
 && useradd --no-log-init --gid morphodict -G morphodict-run \
    --uid ${MORPHODICT_UID_GID} morphodict --create-home

# Copy over the built application from the builder:
COPY --from=builder --chown=morphodict /app /app

COPY docker/app.sh /app

USER morphodict-run
WORKDIR /app
# Activate the Python virtual environment
ENV VIRTUAL_ENV="/app/.venv"
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
ENV PYTHONPATH="/app/src"

# uWSGI will bind HTTP to this port:
EXPOSE 8000
# uWSGI stats are accessible on this port
# I view them with this command:
#
#    $ nc 127.0.0.1 9191 | jq
#
EXPOSE 9191

# Among other things, tini makes typing Ctrl-C into docker-compose work
# see: https://github.com/krallin/tini#tini---a-tiny-but-valid-init-for-containers
ENTRYPOINT ["tini", "--"]
# Startup takes a bit of conditional logic, which we wrap it into a shell script
# instead of inlining it here.
CMD ["/app/app.sh"]
