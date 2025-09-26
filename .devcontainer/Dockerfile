# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/devcontainers/python:3.13-bullseye

ARG DEBIAN_FRONTEND=noninteractive

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

ENV VIRTUAL_ENV=/opt/venv
ENV PATH=/opt/venv/bin:$PATH

RUN python -m venv "$VIRTUAL_ENV" \
    && "$VIRTUAL_ENV/bin/pip" install --no-cache-dir --upgrade pip setuptools wheel isort \
    && chown -R vscode:vscode "$VIRTUAL_ENV"

COPY pytopomojo/requirements.txt /tmp/pip-build/requirements.txt

RUN "$VIRTUAL_ENV/bin/pip" install --no-cache-dir -r /tmp/pip-build/requirements.txt \
    && rm -rf /tmp/pip-build \
    && chown -R vscode:vscode "$VIRTUAL_ENV"

RUN npm install -g prettier @prettier/plugin-python \
    && npm cache clean --force

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspaces
