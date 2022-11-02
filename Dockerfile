ARG ARCH=

# Pull base image
FROM ubuntu:latest

# Labels
LABEL MAINTAINER="https://github.com/jwillmer/"

# Setup external package-sources
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-setuptools \
    python3-pip \
    python3-virtualenv \
    nano \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* 

# RUN pip install setuptools
RUN pip3 install pytz influxdb-client nut2

# Environment vars
ENV PYTHONIOENCODING=utf-8

# Copy files
ADD nut-influxdbv2-exporter.py /
ADD get.sh /

# Run
CMD ["/bin/bash","/get.sh"]
