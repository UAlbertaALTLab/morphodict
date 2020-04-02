FROM python:3.6-slim-buster

# Install HFST and any other system deps.
COPY install-packages.sh /app/
RUN /app/install-packages.sh

# Install Python dependencies.
# NB: Requires requirements.txt to be GENERATED beforehand.
# (use `make` to generate everything properly).
COPY requirements.txt install-python-deps.sh /app/
RUN cd /app/ && ./install-python-deps.sh

# Copy the app as a tarball.
# NB: Requires:
# - CreeDictionary tarball in the build context
# (use `make` to generate this!)
# NB: since the build context (e.g., the docker/ folder) does not contain the
# app source code, copy it over first.
# Do NOT use the root directory as the build context. Builds get slooooooww.
COPY CreeDictionary.tar.gz /app/
RUN cd /app && tar xzf CreeDictionary.tar.gz && rm CreeDictionary.tar.gz
