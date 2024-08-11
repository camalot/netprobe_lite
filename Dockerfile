# Dockerfile for netprobe_lite
# https://github.com/plaintextpackets/netprobe_lite/

# Default to amd64 if no build argument is provided
ARG BASE_IMAGE_ARCH=amd64
# Default to Python 3.12 if no build argument is provided
ARG PYTHON_VERSION=3.12
# slim-bookworm
FROM ${BASE_IMAGE_ARCH}/python:${PYTHON_VERSION}-alpine

ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV NP_MODULE=FULL

WORKDIR /netprobe_lite

# Copy application code
COPY ./src/ /app/

RUN \
    apk update && \
    && apk add --no-cache git curl build-base tcl tk \
    && mkdir -p /app /data \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/setup/requirements.txt \
    && apk del git build-base \
    && chmod +x /app/setup/entrypoint.sh \
    && rm -rf /app/setup

# RUN apt-get update \
#     && apt-get install -y iputils-ping \
#     && apt-get install -y traceroute \
#     && apt-get clean \
#     && pip install -r /netprobe_lite/setup/requirements.txt --break-system-packages \
#     && rm -rf /root/.cache/pip \
#     && chmod +x /netprobe_lite/entrypoint.sh \
#     && rm -rf /netprobe_lite/setup

ENTRYPOINT [ "/bin/bash", "/app/entrypoint.sh" ]
