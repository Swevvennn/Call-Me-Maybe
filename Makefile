PY = python3
SRC = source
MAIN = main.py

run:
	./script_CMM.sh start

.PHONY: all clean install lint

clean:
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf .mypy_cache
	rm -rf data/output

install:
	./script_CMM.sh

lint:
	$(PY) -m flake8 src
	$(PY) -m mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(PY) -m flake8 src
	$(PY) -m mypy src --strict

debug:
	$(PY) -m pdb -m main
