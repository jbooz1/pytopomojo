# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/devcontainers/python:3.13-bullseye

ARG DEBIAN_FRONTEND=noninteractive

# Switch to root for configuring image
USER root

# Custom Cert Support
COPY .devcontainer/certs/ /usr/local/share/ca-certificates/custom/

RUN find /usr/local/share/ca-certificates/custom -type f ! -name '*.crt' -delete \
    && if find /usr/local/share/ca-certificates/custom -type f -name '*.crt' -print -quit | grep -q .; then \
    update-ca-certificates; \
    fi

ENV NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt \
    AWS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    PIP_CERT=/etc/ssl/certs/ca-certificates.crt

# Install packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        build-essential \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x bullseye main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Python configurations
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel isort

COPY pytopomojo/requirements.txt /tmp/pip-build/requirements.txt

RUN python -m pip install --no-cache-dir -r /tmp/pip-build/requirements.txt \
    && rm -rf /tmp/pip-build

# Install prettier
RUN npm install -g prettier @prettier/plugin-python \
    && npm cache clean --force

# Switch back to vscode user
USER vscode

WORKDIR /workspaces
