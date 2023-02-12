SOURCES = $(wildcard src/fixedint/*.py)

# Some dummy file to convey if source files have been updated
TARGET = .updated

default: install

install: ${TARGET}

${TARGET}: ${SOURCES}
	pip install -e .
	@touch ${TARGET}

.PHONY: test

test:
	cd test && python -m unittest
