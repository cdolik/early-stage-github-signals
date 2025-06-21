# Early-Stage GitHub Signals Platform Makefile

.PHONY: all setup install dev install-dev run run-lite test test-coverage lint format metrics serve validate-schema validate-data open-dashboard docs clean pre-commit-install deploy

# Default target
all: install test

# Setup full development environment
setup: install-dev
	@echo "Creating .env file from example if it doesn't exist..."
	@test -f .env || (test -f .env.example && cp .env.example .env && echo ".env created from .env.example" || echo ".env.example not found, skipping .env creation")
	@echo "✅ Development environment setup complete"
	@echo "⚠️  Don't forget to add your GITHUB_TOKEN to .env file"

# Install dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev: install
	pip install -r requirements-dev.txt
	pre-commit install || echo "⚠️ pre-commit not available, skipping hook installation"

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

validate-data:
	python3 scripts/validate_data_quality.py

serve-dashboard:
	cd docs && python3 -m http.server 8000

open-dashboard: serve-dashboard
	@echo "Opening dashboard in browser..."
	@(open http://localhost:8000 || python3 -c "import webbrowser; webbrowser.open('http://localhost:8000')") || echo "⚠️  Could not automatically open browser"

dashboard: validate-schema serve-dashboard

docs: metrics

# Install pre-commit hooks
pre-commit-install:
	pip install pre-commit
	pre-commit install

# Run pre-commit checks manually
pre-commit:
	pre-commit run --all-files
	
lint:
	black . --check
	flake8 || echo "⚠️  flake8 not installed or not configured"
	
format:
	black . || echo "⚠️  black not installed, run 'pip install black' to install"

clean:
	rm -rf data/cache/*.json
	rm -f metrics_table.md

# Deploy to GitHub Pages
deploy: validate-schema validate-data
	./deployment.sh
