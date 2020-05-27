FROM python:3.6-slim-buster

# Install HFST and any other system deps.
COPY docker/install-packages.sh /app/
RUN /app/install-packages.sh

# Install Python dependencies.
# NB: Requires requirements.txt to be GENERATED beforehand.
# (use `make` to generate everything properly).
COPY docker/requirements.txt docker/install-python-deps.sh /app/
RUN cd /app/ && ./install-python-deps.sh

ADD CreeDictionary /app/

# Run the server!
ENV DJANGO_SETTINGS_MODULE="CreeDictionary.settings"
EXPOSE 8000 8001
WORKDIR /app
CMD cd static && python -m http.server 8001 & python manage.py runserver 0.0.0.0:8000
