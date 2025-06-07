# Early-Stage GitHub Signals Platform Makefile

.PHONY: all install run run-lite test test-coverage lint format metrics serve docs clean pre-commit-install

# Default target
all: install test

# Install dependencies
install:
	pip install -r requirements.txt

run:
	python weekly_gems_cli.py

run-lite:
	python weekly_gems_cli.py --debug --max-repos 5 --skip-producthunt --skip-hackernews

test:
	python -m pytest

test-coverage:
	python -m pytest --cov=src --cov-report=term --cov-report=html

metrics:
	python src/utils/generate_metrics.py --write docs/metrics.md

serve:
	cd docs && python3 -m http.server 8000

docs: metrics

# Install pre-commit hooks
pre-commit-install:
	pre-commit install
	python src/generators/html_generator.py
	
lint:
	black . --check
	flake8
	
format:
	black .

clean:
	rm -rf data/cache/*.json
	rm -f metrics_table.md
	
install-dev: install
	pip install -r requirements-dev.txt
