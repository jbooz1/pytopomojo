#!/bin/bash
set -euo pipefail

SSH_AGENT_DIR=/ssh-agent
HOST_AGENT_SOCKET="$SSH_AGENT_DIR/host-agent.sock"
DESKTOP_SOCKET="/run/host-services/ssh-auth.sock"
PROXY_SOCKET="$SSH_AGENT_DIR/proxy.sock"

mkdir -p "$SSH_AGENT_DIR"

if [ -L "$PROXY_SOCKET" ] || [ -S "$PROXY_SOCKET" ]; then
  rm -f "$PROXY_SOCKET"
fi

select_socket() {
  local candidate=$1
  if [ -S "$candidate" ] && [ -r "$candidate" ]; then
    echo "$candidate"
  fi
}

CHOSEN_SOCKET="$(select_socket "$HOST_AGENT_SOCKET")"
if [ -z "$CHOSEN_SOCKET" ]; then
  CHOSEN_SOCKET="$(select_socket "$DESKTOP_SOCKET")"
fi

if [ -n "$CHOSEN_SOCKET" ]; then
  ln -sfn "$CHOSEN_SOCKET" "$PROXY_SOCKET"
  echo "[devcontainer] SSH agent socket linked to $CHOSEN_SOCKET" >&2
else
  cat >&2 <<'MSG'
[devcontainer] Warning: no SSH agent socket detected.\
Ensure an SSH agent is running on the host and SSH_AUTH_SOCK is exported before starting the dev container.
MSG
fi
