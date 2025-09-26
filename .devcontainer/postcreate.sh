#!/bin/bash
set -euo pipefail

# Show git dirty status in zsh prompt
git config devcontainers-theme.show-dirty 1

# oh-my-zsh plugins
sed -i 's/^\(\s*plugins=(.*\)\s*)/\1 python pyenv pip)/' $HOME/.zshrc

# Setup pure prompt
sudo npm install --global pure-prompt
sed -i "s|^ZSH_THEME=.*|ZSH_THEME=\"\"\n\nFPATH=$(npm root -g)/pure-prompt/functions:\$FPATH|" $HOME/.zshrc

cat >>$HOME/.zshrc <<'EOF'

# Pure prompt
autoload -U promptinit; promptinit
prompt pure

EOF

# install project in editable mode using system Python
sudo python -m pip install --no-cache-dir -e .
