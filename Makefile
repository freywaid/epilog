#
#
#
#
VENV = venv
BIN = $(VENV)/bin
PYTHON = $(BIN)/python3
PIP = $(BIN)/pip3

$(VENV):
	python3 -m venv venv

.PHONY: install
install: $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt

