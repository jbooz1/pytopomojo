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
    PIP_CERT=/etc/ssl/certs/ca-certificates.crt \
    NPM_CONFIG_PREFIX=/usr/local \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Add new Yarn GPG key
RUN mkdir -p /etc/apt/keyrings && \
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor -o /etc/apt/keyrings/yarn.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/yarn.gpg] https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list

# Install system packages
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    build-essential \
    nodejs \
    npm

COPY pytopomojo/requirements.txt /tmp/pip-build/requirements.txt

# Install Python packages
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip setuptools wheel isort \
    && python -m pip install -r /tmp/pip-build/requirements.txt

# Install pyright for Claude Code LSP plugin
RUN --mount=type=cache,target=/root/.npm \
    npm install -g pyright

# Configure ZSH History
RUN mkdir -p "/home/vscode/.history" && touch "/home/vscode/.history/zsh_history" && \
    chown -R vscode:vscode /home/vscode/.history && \
    cat >> /home/vscode/.zshrc <<'EOF'
# Persistent zsh history for devcontainer
# Use a dedicated history directory (backed by a Docker volume)
mkdir -p "/home/vscode/.history"
export HISTFILE="/home/vscode/.history/zsh_history"
export HISTSIZE=50000      # in-memory commands
export SAVEHIST=100000     # on-disk commands
# History behavior options
setopt APPEND_HISTORY          # append to history file, don't overwrite
setopt INC_APPEND_HISTORY      # write each command as it's entered
setopt SHARE_HISTORY           # share history across sessions
setopt HIST_IGNORE_DUPS        # ignore immediate duplicates
setopt HIST_IGNORE_ALL_DUPS    # drop older duplicates
setopt HIST_IGNORE_SPACE       # ignore commands starting with a space
setopt HIST_REDUCE_BLANKS      # trim extra spaces
setopt HIST_VERIFY             # don't immediately execute recalled commands
# DEVCONTAINER ZSH HISTORY END
EOF

# Switch back to vscode user
USER vscode

# Install Claude Code using native installer
RUN curl -fsSL https://claude.ai/install.sh | bash

WORKDIR /workspaces
