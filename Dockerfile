FROM python:3.6-slim-buster

# Install HFST
# https://packages.debian.org/buster/hfst
#RUN apt-get install -y software-properties-common &&\
#        add-apt-repository science &&\
#        apt-get update -y &&\
#        apt-get install -y hfst
COPY libexec/install-packages.sh .
RUN ./install-packages.sh
