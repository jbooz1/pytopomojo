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

# oh-my-zsh plugins
sed -i 's/^\(\s*plugins=(.*\)\s*)/\1 python pyenv pip)/' $HOME/.zshrc

# install project in editable mode using system Python
python -m pip install --no-cache-dir -e .
