# 📁 Folder Structure

```
📦 early-stage-github-signals
├── 📄 README.md                    # Main project documentation
├── 📄 requirements.txt             # Python dependencies
├── 📄 requirements-dev.txt         # Development dependencies
├── 📄 Makefile                     # Build automation
├── 📄 config.yaml                  # Configuration settings
│
├── 📂 src/                         # Core analysis engine
│   ├── 📄 __init__.py
│   ├── 📄 main.py                  # Main application entry
│   │
│   ├── 📂 analyzers/               # Scoring algorithms
│   │   ├── 📄 __init__.py
│   │   ├── 📄 momentum_scorer.py   # Main scoring engine
│   │   ├── 📄 startup_scorer.py    # Startup-specific scoring
│   │   ├── 📄 trend_analyzer.py    # Trend analysis
│   │   └── 📄 insights_generator.py # Insight generation
│   │
│   ├── 📂 collectors/              # Data gathering
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base_collector.py    # Base collector class
│   │   ├── 📄 github_collector.py  # GitHub API integration
│   │   ├── 📄 hackernews_collector.py # HN data collection
│   │   ├── 📄 producthunt_collector.py # PH data collection
│   │   └── 📄 trending_collector.py # Trending repositories
│   │
│   ├── 📂 generators/              # Output generation
│   │   ├── 📄 __init__.py
│   │   ├── 📄 api_generator.py     # JSON API generation
│   │   ├── 📄 html_generator.py    # HTML report generation
│   │   ├── 📄 json_generator.py    # Data file generation
│   │   ├── 📄 report_generator.py  # Report formatting
│   │   └── 📄 weekly_gems_generator.py # Weekly summaries
│   │
│   ├── 📂 utils/                   # Utility functions
│   │   ├── 📄 __init__.py
│   │   ├── 📄 cache.py            # Caching utilities
│   │   ├── 📄 config.py           # Configuration handling
│   │   └── 📄 generate_metrics.py # Metrics utilities
│   │
│   └── 📂 validators/              # Data validation
│       ├── 📄 __init__.py
│       └── 📄 schema_validator.py  # JSON schema validation
│
├── 📂 docs/                       # GitHub Pages dashboard
│   ├── 📄 index.html              # Main dashboard page
│   ├── 📄 about.html              # About page
│   ├── 📄 styles.css              # Dashboard styling
│   ├── 📄 dashboard.js            # Dashboard functionality
│   ├── 📄 history.js              # Historical data handling
│   ├── 📄 DASHBOARD_IMPLEMENTATION.md # Implementation guide
│   ├── 📄 SCORING.md              # Scoring methodology
│   ├── 📄 FOLDER_STRUCTURE.md     # This file
│   │
│   ├── 📂 api/                    # JSON data endpoints
│   │   ├── 📄 latest.json         # Current scored repositories
│   │   ├── 📄 simplified.json     # Minimal dataset
│   │   ├── 📄 2025-06-06.json     # Historical snapshots
│   │   ├── 📄 2025-06-10.json
│   │   ├── 📄 2025-06-11.json
│   │   └── 📄 README.md           # API documentation
│   │
│   ├── 📂 assets/                 # Static assets
│   │   ├── 📄 logo.svg            # Project logo
│   │   ├── 📄 logo.png            # PNG fallback
│   │   ├── 📂 css/                # Additional stylesheets
│   │   └── 📂 js/                 # Additional scripts
│   │
│   └── 📂 data/                   # Dashboard data files
│       ├── 📄 _last_week_scores.json # Previous scores
│       ├── 📄 2025-06-06.json     # Daily snapshots
│       ├── 📄 2025-06-10.json
│       └── 📄 2025-06-11.json
│
├── 📂 schemas/                    # JSON schema definitions
│   ├── 📄 api.schema.json         # API response schema
│   ├── 📄 repo.schema.json        # Repository data schema
│   ├── 📄 repository.schema.json  # Extended repo schema
│   ├── 📄 simplified.schema.json  # Simplified data schema
│   └── 📄 weekly_gems.schema.json # Weekly report schema
│
├── 📂 scripts/                   # Automation tools
│   ├── 📄 backfill_data_files.py # Data backfill utility
│   ├── 📄 commit_dashboard.sh    # Dashboard deployment
│   └── 📄 validate_schema.py     # Schema validation
│
├── 📂 reports/                   # Generated reports
│   ├── 📄 weekly_gems_2025-06-06.json # Weekly data
│   ├── 📄 weekly_gems_2025-06-06.md   # Weekly markdown
│   ├── 📄 weekly_gems_latest.md       # Latest report
│   └── 📄 ...                         # Additional reports
│
├── 📂 tests/                     # Test suite
│   ├── 📄 __init__.py
│   ├── 📄 test_integration.py    # Integration tests
│   ├── 📄 test_json_delta.py     # Data validation tests
│   ├── 📄 test_json_generator.py # Generator tests
│   ├── 📄 test_metrics.py        # Metrics validation
│   └── 📂 fixtures/              # Test data fixtures
│
├── 📂 templates/                 # Report templates
│   ├── 📂 html/                  # HTML templates
│   └── 📂 markdown/              # Markdown templates
│
├── 📂 data/cache/                # Runtime cache
│
└── 📂 .github/                   # GitHub configuration
    └── 📂 workflows/             # GitHub Actions
        ├── 📄 weekly-report.yml  # Weekly data collection
        ├── 📄 test.yml           # Test automation
        └── 📄 deploy.yml         # Deployment automation
```

## File Purposes

### Main Files
- `index.html`: Core dashboard UI with HTML structure
- `styles.css`: All styling for the dashboard, including responsive design
- `dashboard.js`: JavaScript that powers the dashboard functionality

### Data Files
- `/api/latest.json`: Most recent repository data
- `/api/simplified.json`: Simplified data format for faster loading

### Documentation
- `DASHBOARD_IMPLEMENTATION.md`: Details on the dashboard implementation
- `DEVELOPER_SETUP.md`: Instructions for setting up the development environment

## Organization Principles

1. **Separation of Concerns**: HTML structure, CSS styling, and JavaScript functionality are kept in separate files
2. **API Versioning**: All API endpoints are in the `/api` folder for clean organization
3. **Static Assets**: All images, icons, and other static files are in the `/assets` folder
4. **Historical Data**: Previous data snapshots are stored in the `/data` folder

## Disclaimer

This dashboard is not an official GitHub project. It uses public GitHub API data to analyze repository momentum.
