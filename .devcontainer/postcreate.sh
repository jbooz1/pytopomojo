#!/bin/bash
set -euo pipefail

# Show git dirty status in zsh prompt
git config devcontainers-theme.show-dirty 1

sudo chown -R $(whoami): /home/vscode/.claude

# Clone or pull TopoMojo API repo
sudo chown -R $(whoami): /mnt/topomojo-api
if [ -d /mnt/topomojo-api/.git ]; then
  git -C /mnt/topomojo-api pull
else
  git clone https://github.com/cmu-sei/TopoMojo.git /mnt/topomojo-api
fi

# Source local env vars if present
ENV_FILE="$(pwd)/.devcontainer/.env"
if ! grep -qF "$ENV_FILE" "$HOME/.zshrc"; then
  echo "[ -f \"$ENV_FILE\" ] && source \"$ENV_FILE\"" >> "$HOME/.zshrc"
fi

# oh-my-zsh plugins
sed -i 's/^\(\s*plugins=(.*\)\s*)/\1 python pyenv pip)/' $HOME/.zshrc

# install project in editable mode using system Python
python -m pip install --no-cache-dir -e .

# Enable Claude Code pyright LSP plugin
CLAUDE_SETTINGS="$HOME/.claude/settings.json"
if [ ! -f "$CLAUDE_SETTINGS" ]; then
  echo '{}' > "$CLAUDE_SETTINGS"
fi
python3 - <<'EOF'
import json, os
path = os.path.expanduser("~/.claude/settings.json")
with open(path) as f:
    settings = json.load(f)
settings.setdefault("enabledPlugins", {})["pyright-lsp@claude-plugins-official"] = True
with open(path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")
EOF
