# Early Stage GitHub Signals Platform

<p align="center">
  <img src="docs/assets/logo.svg" alt="Early Stage GitHub Signals Logo" width="200" height="200" />
</p>

<p align="center">
  <strong>Weekly automated reports of GitHub repositories with high startup potential</strong>
</p>

<p align="center">
  <a href="#about">About</a> •
  <a href="#features">Features</a> •
  <a href="#scoring-algorithm">Scoring Algorithm</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#reports">Reports</a> •
  <a href="#dashboard">Dashboard</a> •
  <a href="#api">API</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

## About

The Early Stage GitHub Signals Platform is a comprehensive tool designed for venture capitalists, angel investors, and startup enthusiasts to identify promising early-stage startups through their GitHub activity. By analyzing various signals from GitHub repositories, this platform generates weekly reports highlighting repositories with high startup potential.

This platform uses a sophisticated 50-point scoring algorithm to evaluate repositories across three categories:
1. **Repository signals** (20 points)
2. **Organization signals** (15 points)
3. **Community signals** (15 points)

## Features

- **Automated Data Collection**: Gathers trending repositories from GitHub and discussions from Hacker News
- **Comprehensive Scoring**: Evaluates repositories using a 50-point algorithm with multiple signals
- **Weekly Reports**: Generates detailed reports in multiple formats:
  - Markdown reports with analysis and insights
  - Interactive HTML dashboard for exploration
  - JSON API for integration with other tools
- **Trend Analysis**: Identifies patterns and trends across repositories
- **Insight Generation**: Provides context on why certain repositories are interesting
- **Caching System**: Reduces API calls and speeds up report generation

## Scoring Algorithm

The platform uses a 50-point scoring system divided into three categories:

### Repository Signals (20 points)
- **Recent Creation** (3 points): Repository created within the last 90 days
- **Professional Language** (2 points): Uses modern, production-ready languages
- **CI/CD Setup** (2 points): Has continuous integration/deployment configuration
- **Quality Documentation** (2 points): Well-documented with comprehensive README
- **Active Development** (3 points): Regular commits and updates (10+ per week)
- **External Website** (2 points): Links to an external product website
- **Startup Keywords** (3 points): Contains startup-related keywords in description
- **Y Combinator Mentions** (2 points): References to Y Combinator or other accelerators
- **Tests Present** (1 point): Includes test suites

### Organization Signals (15 points)
- **Recent Creation** (3 points): Organization created recently
- **Team Size** (3 points): Has 2-15 members (optimal startup size)
- **Multiple Repos** (2 points): Organization has multiple repositories
- **Professional Profile** (2 points): Complete organization profile
- **Organization Website** (2 points): Has website link
- **Hiring Indicators** (3 points): Mentions hiring or job openings

### Community Signals (15 points)
- **Hacker News Discussion** (5 points): Repository mentioned on Hacker News
- **Star Growth** (3 points): Rapid growth in GitHub stars
- **External Contributors** (2 points): Contributors from outside the organization
- **Issue Engagement** (2 points): Active issues and discussions
- **Fork Activity** (2 points): Multiple forks and activity on forks
- **Social Mentions** (1 point): Mentions on social media platforms

## Installation

### Prerequisites
- Python 3.8 or higher
- GitHub API Token

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/early-stage-github-signals.git
   cd early-stage-github-signals
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export GITHUB_TOKEN=your_github_token
   ```

## Usage

### Command Line

Generate a full report with all outputs:
```bash
python run.py
```

Command line options:
```
--config CONFIG       Path to configuration file (default: config.yaml)
--debug               Enable debug logging
--force-refresh       Force refresh of cached data
--skip-api            Skip API generation
--skip-html           Skip HTML generation
--skip-report         Skip Markdown report generation
--date DATE           Report date (YYYY-MM-DD)
```

### GitHub Actions

The platform is designed to run automatically every week using GitHub Actions. The workflow file is located at `.github/workflows/weekly-report.yml`.

To manually trigger a report generation:
1. Go to the repository on GitHub
2. Click on "Actions"
3. Select "Weekly GitHub Signals Report"
4. Click "Run workflow"

## Reports

Weekly reports are generated in the `reports/` directory in markdown format, containing:

- Top 25 repositories by startup potential
- Score breakdown for each repository
- Trend analysis and patterns
- Insights and observations
- Charts and visualizations

## Dashboard

An interactive HTML dashboard is generated in the `docs/` directory, providing:

- Filterable, sortable repository cards
- Score visualization
- Trend charts
- Detailed insights
- Search functionality

## API

A JSON API is generated in the `docs/api/` directory for integration with other tools:

- `latest.json`: Most recent report data
- `YYYY-MM-DD.json`: Historical report data by date
- `trends.json`: Aggregated trend data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Attribution

This project was developed with the assistance of:

- **GitHub Copilot** - AI-powered development assistance
- **GitHub Copilot Chat** - AI-powered code discussions
- **OpenAI's ChatGPT** - Helped with algorithm design

Special thanks to the open-source community and all the libraries that made this project possible.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
