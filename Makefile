.PHONY: install run debug clean lint

VENV = .venv

install: $(VENV)

$(VENV): pyproject.toml	
	uv sync

run: $(VENV)
	uv run main.py $(ARG)

debug: $(VENV)
	uv run -m pdb main.py $(ARG)

clean:
	rm -rf __pycache__
	rm -rf .mypy_cache

lint: $(VENV)
	uv run flake8 *.py
	uv run mypy *.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs