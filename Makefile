VENV := venv
KUPFERBOOTSTRAP := $(VENV)/bin/kupferbootstrap
PYTHON := python3
INSTALL_BINARY_NAME := kupferbootstrap
INSTALL_TARGET := ${HOME}/.local/bin/$(INSTALL_BINARY_NAME)

.PHONY: KBS_HELP install
DEFAULT: KBS_HELP

$(VENV)/bin/pip3:
	$(PYTHON) -m venv $(VENV)

$(KUPFERBOOTSTRAP): $(VENV)/bin/pip3 pyproject.toml requirements.txt
	$(VENV)/bin/pip3 install -r requirements.txt

KBS_HELP: $(KUPFERBOOTSTRAP)
	$(KUPFERBOOTSTRAP) --help

install: $(INSTALL_TARGET)

$(INSTALL_TARGET): $(KUPFERBOOTSTRAP)
	mkdir -p "$$(dirname "$(INSTALL_TARGET)")"
	ln -srvf "$(KUPFERBOOTSTRAP)" "$(INSTALL_TARGET)"
