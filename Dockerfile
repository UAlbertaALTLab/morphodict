FROM python:3.6-slim-buster

# Install HFST and Pipenv
COPY libexec/install-packages.sh .
RUN ./install-packages.sh

# Install Python dependencies.
COPY Pipfile.lock .
RUN pipenv install --skip-lock --clear
