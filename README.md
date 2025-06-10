# Early Stage GitHub Signals Platform

> **Find promising developer tools through code momentum signals before they go mainstream**

[![Dashboard](https://img.shields.io/badge/Dashboard-Live-brightgreen)](https://cdolik.github.io/early-stage-github-signals/)
[![GitHub Actions](https://github.com/cdolik/early-stage-github-signals/workflows/Weekly%20GitHub%20Signals%20Report/badge.svg)](https://github.com/cdolik/early-stage-github-signals/actions)
[![Tests](https://github.com/cdolik/early-stage-github-signals/workflows/Tests/badge.svg)](https://github.com/cdolik/early-stage-github-signals/actions)
[![Schema Validation](https://github.com/cdolik/early-stage-github-signals/workflows/Validate%20Schema/badge.svg)](https://github.com/cdolik/early-stage-github-signals/actions)
[![Last Updated](https://img.shields.io/badge/Last%20Updated-2025--06--07-blue)](https://cdolik.github.io/early-stage-github-signals/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What It Does

Early Stage GitHub Signals is a powerful signal engine that identifies promising developer tools in their early phases. The platform analyzes GitHub activity using a comprehensive 10-point scoring system that evaluates commit surge, star velocity, team traction, and ecosystem fit to surface high-potential projects weeks before they gain mainstream attention.

### 🚀 [**View Live Dashboard**](https://cdolik.github.io/early-stage-github-signals/) | [**Dashboard Implementation Guide**](docs/DASHBOARD_IMPLEMENTATION.md)

> **Want updates?** ⭐️ Star or 👀 Watch this repo to follow weekly signals.

## ✨ Key Features

- **🔍 Multi-Source Discovery**: GitHub Trending + Product Hunt + Hacker News
- **📊 10-Point Scoring**: Focused on meaningful momentum signals
- **🎯 Quality Threshold**: Only surfaces repos scoring 7+/10 points
- **📈 Investor-Grade Dashboard**: VC Mode, trend visualization, and momentum signals
- **🔄 Weekly Updates**: Fresh data every week with momentum change tracking
- **🤖 Weekly Automation**: GitHub Actions generates reports automatically
- **💻 Professional Dashboard**: Clean, VC-friendly interface
- **📱 Mobile Responsive**: Works on all devices
- **📄 [Project at a glance](PROJECT_STATUS.md)**: Current status and investor brief
- **📄 [Codebase Status Report (June 2025)](docs/CODEBASE_STATUS.md)**: Technical health assessment

---

## 🏆 Focused 10-Point Scoring System

Our algorithm focuses exclusively on momentum signals that matter:

1. **Commit Surge (3 pts)**: 10+ commits in 14 days, 3+ with "feat:" or "add"
2. **Star Velocity (3 pts)**: 10+ stars gained in 14 days  
3. **Team Traction (2 pts)**: 2-5 contributors with 5+ commits each in 30 days
4. **Dev Ecosystem Fit (2 pts)**: Python/TypeScript/Rust OR topics like "devops", "cli", "sdk"

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- GitHub Personal Access Token

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/early-stage-github-signals.git
cd early-stage-github-signals

# Install dependencies
pip install -r requirements.txt

# Set your GitHub token
export GITHUB_TOKEN="your_github_token"
```

### Running the Platform

```bash
# Generate this week's report
./run_weekly_gems.sh

# Quick test run (minimal API usage)
python weekly_gems_cli.py --debug --max-repos 5 --skip-hackernews
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--debug` | Enable debug logging |
| `--max-repos N` | Limit analysis to N repositories |
| `--min-stars N` | Minimum stars for consideration |
| `--skip-hackernews` | Skip Hacker News data collection |
| `--skip-producthunt` | Skip Product Hunt data collection |
| `--skip-api` | Skip API file generation |

### API Usage Optimization

The platform is designed to respect GitHub's API rate limits (5000 requests/hour). The `--lite` mode is recommended for development and testing to minimize API usage.

## 📊 Sample Output

The platform identifies startups like:

| Repository | Score | Why Interesting |
|------------|-------|-----------------|
| ai-startup/platform | 9/10 | 14 commits in last week, 25+ stars gained, 3 active contributors |
| fintech-co/api | 38/50 | Professional setup, active development |
| saas-tool/app | 35/50 | Strong community, has product website |

## 🔄 Automation

The platform runs automatically every Monday via GitHub Actions:

1. **Collects** trending repositories from GitHub API
2. **Analyzes** each repo using the 50-point algorithm  
3. **Generates** reports in multiple formats
4. **Deploys** updated dashboard to GitHub Pages

## 🛠️ Architecture

```
GitHub API → Data Collection → Scoring Algorithm → Report Generation → GitHub Pages
```

- **Collectors**: GitHub API integration
- **Analyzers**: 50-point scoring system
- **Generators**: Dashboard, API, reports
- **Automation**: GitHub Actions workflows

## 📈 Use Cases

### For VCs
- **Early deal flow**: Discover startups before competition
- **Technical due diligence**: Assess team execution quality
- **Market timing**: Identify emerging trends

### For Developers
- **Trend spotting**: See what technologies are gaining traction
- **Competition analysis**: Monitor similar projects
- **Inspiration**: Discover innovative approaches

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run with debug logging
python src/main.py --debug --dry-run
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with GitHub API and modern web technologies
- Inspired by the need for better early-stage startup discovery
- Thanks to the open source community

---

**⭐ Star this repo if you find it useful!**

*Built with ❤️ for the startup ecosystem*

---

## 💼 **For VCs**

### **Why Use Early-Stage GitHub Signals?**
- **Discover Hidden Gems**: Identify promising startups early.
- **Data-Driven Decisions**: Leverage insights for smarter investments.
- **Stay Ahead**: Monitor trends and emerging technologies.

### **Sample Insights**
- **Top Scored Startups**: Fintech API, Test Startup
- **Trending Technologies**: AI, Blockchain, SaaS

---

## 📚 **API Documentation**

### **Endpoints**
- `/api/latest.json`: Latest startup scores and insights.

### **Example Response**
```json
{
  "repositories": [
    {
      "name": "test-startup",
      "score": 45,
      "language": "Python"
    },
    {
      "name": "fintech-api",
      "score": 50,
      "language": "JavaScript"
    }
  ]
}
```

---

## 🤝 **Contributing**

### **Add New Scoring Criteria**
1. Modify `src/analyzers/startup_scorer.py`.
2. Add tests in `tests/test_integration.py`.

### **Development Setup**
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run tests:
   ```bash
   pytest
   ```

---

## ❤️ **Footer**

Built with ❤️ for startup discovery.

- [Live Dashboard](https://cdolik.github.io/early-stage-github-signals/)
- [API Documentation](https://cdolik.github.io/early-stage-github-signals/api/latest.json)
- [Reports](https://cdolik.github.io/early-stage-github-signals/reports/)
