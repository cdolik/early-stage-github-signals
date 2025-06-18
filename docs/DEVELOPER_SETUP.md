# Developer Setup Guide

This guide will help you set up and run the Early-Stage GitHub Signals platform for local development.

## Prerequisites

- Python 3.11+
- Git
- GitHub Personal Access Token (for API access)

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourorganization/early-stage-github-signals.git
cd early-stage-github-signals
```

### 2. Create a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux
source venv/bin/activate
# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

# For development, also install development dependencies
pip install -r requirements-dev.txt
```

### 4. Set Up GitHub API Token

Create a GitHub Personal Access Token with the following permissions:
- `public_repo`
- `read:org`
- `read:user`
- `read:packages`

Then set it as an environment variable:

```bash
# On macOS/Linux
export GITHUB_TOKEN="your_token_here"

# On Windows
set GITHUB_TOKEN=your_token_here
```

For persistent configuration, add this to your shell profile file (.bashrc, .zshrc, etc.).

## Running the Platform

### Quick Start (Lite Mode)

Run the platform with minimal API calls (good for testing):

```bash
make run-lite
```

Or directly:

```bash
python weekly_gems_cli.py --debug --max-repos 5 --skip-producthunt --skip-hackernews
```

### Full Run

```bash
make run
```

Or directly:

```bash
python weekly_gems_cli.py
```

### View Dashboard

```bash
make serve-dashboard
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

## Development Workflow

### Running Tests

```bash
# Run all tests
make test

# With coverage report
make test-coverage
```

### Schema Validation

```bash
make validate-schema
```

### Code Structure

- `src/analyzers/` - Momentum scoring and analysis
- `src/collectors/` - Data collection from various sources
- `src/generators/` - Output generation for reports and API
- `src/utils/` - Helper utilities
- `schemas/` - JSON Schema definitions
- `docs/` - Documentation and dashboard UI
- `tests/` - Test suite

## Common Development Tasks

### Adding a New Collector

1. Create a new file in `src/collectors/` that extends `BaseCollector`
2. Implement the required methods: `__init__`, `get_name`, and `collect`
3. Add your collector to `src/collectors/__init__.py`

### Modifying the Scoring Algorithm

1. The core scoring logic is in `src/analyzers/momentum_scorer.py`
2. Each scoring dimension has its own method (e.g., `_score_commit_surge`)
3. Update the corresponding schema in `schemas/repository.schema.json` if needed

### Updating the Dashboard

The dashboard uses vanilla JavaScript and CSS:

- Main HTML: `docs/index.html`
- CSS: `docs/styles.css`
- JavaScript: `docs/dashboard.js`

## Troubleshooting

### API Rate Limits

GitHub API has rate limits. If you encounter rate limiting:

1. Ensure your GitHub token is set correctly
2. Use the `--lite` mode for testing
3. Check the cache directory at `data/cache/` to see what's being cached

### Schema Validation Errors

If schema validation fails:

1. Check the field names match between code and schema files
2. Verify all required fields are present
3. Run `make validate-schema` to debug

## CI/CD Pipeline

The platform uses GitHub Actions for automation:

- Weekly report generation
- Schema validation
- Dashboard deployment

## Getting Help

Refer to:
- `README.md` for general information
- `docs/CODEBASE_STATUS.md` for current issues and enhancements
- `docs/roadmap.md` for future plans
