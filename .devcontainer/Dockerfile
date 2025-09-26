# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        software-properties-common \
        ca-certificates \
        curl \
        gnupg \
        dirmngr \
        lsb-release \
        build-essential \
        nodejs \
        npm \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        python3.13 \
        python3.13-venv \
        python3.13-dev \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
ENV PATH=/opt/venv/bin:$PATH

RUN python3.13 -m venv "$VIRTUAL_ENV" \
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

WORKDIR /workspace
