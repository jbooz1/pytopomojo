#!/bin/bash
set -euo pipefail

# Show git dirty status in zsh prompt
git config devcontainers-theme.show-dirty 1

# oh-my-zsh plugins
sed -i 's/^\(\s*plugins=(.*\)\s*)/\1 python pyenv pip)/' $HOME/.zshrc

# install project in editable mode using system Python
python -m pip install --no-cache-dir -e .
