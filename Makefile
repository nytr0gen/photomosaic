VENV=.venv

PYTHON_BIN=python3
PIP_BIN=$(VENV)/bin/pip

all: install

$(VENV): $(VENV)/bin/activate
$(VENV)/bin/activate: requirements.txt
	test -d $(VENV) || $(PYTHON_BIN) -m venv $(VENV)
	$(PIP_BIN) install -r $<
	touch $@

install: $(VENV)

run: install

help:
	@cat README.md

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
