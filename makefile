PYTHON := python3
VENV_DIR := .venv

.PHONY: venv activate deactivate clean

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -e .
	@echo "\n***Run 'source $(VENV_DIR)/bin/activate' to activate the venv.***"


clean:
	rm -rf $(VENV_DIR)
