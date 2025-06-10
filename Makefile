# Early-Stage GitHub Signals Platform Makefile

.PHONY: all install run run-lite test test-coverage lint format metrics serve validate-schema open-dashboard docs clean pre-commit-install

# Default target
all: install test

# Install dependencies
install:
	pip install -r requirements.txt

run:
	python3 weekly_gems_cli.py

run-lite:
	python3 weekly_gems_cli.py --debug --max-repos 5 --skip-producthunt --skip-hackernews

test: validate-schema
	python3 -m pytest

test-coverage:
	python3 -m pytest --cov=src --cov-report=term --cov-report=html

metrics:
	python3 src/utils/generate_metrics.py --write docs/metrics.md

serve:
	cd docs && python3 -m http.server 8000

validate-schema:
	pip install jsonschema
	python3 scripts/validate_schema.py

validate-json: validate-schema

serve-dashboard:
	cd docs && python3 -m http.server 8000

open-dashboard: serve-dashboard
	open http://localhost:8000

dashboard: validate-schema serve-dashboard

docs: metrics

# Install pre-commit hooks
pre-commit-install:
	pip install pre-commit
	pre-commit install

# Run pre-commit checks manually
pre-commit:
	pre-commit run --all-filespre-commit install
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
