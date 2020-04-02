FROM python:3.6-slim-buster

# Install HFST and any other system deps.
COPY install-packages.sh /app/
RUN /app/install-packages.sh

# Install Python dependencies.
# NB: Requires requirements.txt to be GENERATED beforehand.
# (use `make` to generate everything properly).
COPY requirements.txt install-python-deps.sh /app/
RUN cd /app/ && ./install-python-deps.sh
