FROM python:3.6-slim-buster

# Install HFST and Pipenv
COPY install-packages.sh .
RUN ./install-packages.sh

# Install Python dependencies.
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
