# 📊 Early-Stage GitHub Signals

An investor-grade radar for surfacing high-potential open-source developer tools before they reach mainstream awareness. Built on GitHub momentum signals and real-time scoring.

[![Dashboard](https://img.shields.io/badge/Dashboard-Live-brightgreen)](https://cdolik.github.io/early-stage-github-signals/)
[![GitHub Actions](https://github.com/cdolik/early-stage-github-signals/workflows/Weekly%20GitHub%20Signals%20Report/badge.svg)](https://github.com/cdolik/early-stage-github-signals/actions)
[![Tests](https://github.com/cdolik/early-stage-github-signals/workflows/Tests/badge.svg)](https://github.com/cdolik/early-stage-github-signals/actions)
[![Schema Validation](https://github.com/cdolik/early-stage-github-signals/workflows/Validate%20Schema/badge.svg)](https://github.com/cdolik/early-stage-github-signals/actions)
[![Last Updated](https://img.shields.io/badge/Last%20Updated-2025--06--12-blue)](https://cdolik.github.io/early-stage-github-signals/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Live Demo
https://cdolik.github.io/early-stage-github-signals/

## 🧠 What It Does
- Scores early-stage GitHub repos using a 10-point momentum system
- Highlights top movers weekly via an investor-optimized dashboard
- Uses data from GitHub, Hacker News, and Product Hunt

### 🚀 [**View Live Dashboard**](https://cdolik.github.io/early-stage-github-signals/) | [**Dashboard Implementation Guide**](docs/DASHBOARD_IMPLEMENTATION.md)

> **Want updates?** ⭐️ Star or 👀 Watch this repo to follow weekly signals.

## � Scoring System
Momentum score = Commit Surge + Star Velocity + Team Traction + Ecosystem Fit

Our algorithm focuses exclusively on momentum signals that matter:

- **Commit Surge (3 pts)**: 10+ commits in 14 days, 3+ with "feat:" or "add"
- **Star Velocity (3 pts)**: 10+ stars gained in 14 days  
- **Team Traction (2 pts)**: 2-5 contributors with 5+ commits each in 30 days
- **Dev Ecosystem Fit (2 pts)**: Python/TypeScript/Rust OR topics like "devops", "cli", "sdk"

## 🧰 Stack
- Frontend: HTML/CSS/JS (no framework), hosted on GitHub Pages
- Backend: Python data pipeline
- CI: GitHub Actions (test, schema validation, generator)

## ⚙️ Local Development
```bash
make install
make serve  # Runs local dashboard
make generate  # Generates latest API files
make test  # Runs test suite
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

## 🤝 Disclaimer

Not affiliated with GitHub Inc. This is a community-driven open-source effort.

## 📁 Folder Structure
- `src/`: Scoring logic, analyzers, generators
- `docs/`: GitHub Pages dashboard + API output
- `schemas/`: JSON schema definitions
- `scripts/`: CLI and utility scripts

## ✅ Go-Live Checklist

### 1. **Commit Final Updates**
```bash
git add .
git commit -m "feat: finalize signal-first v1 with animations, accessibility, and documentation"
git push origin main
```

### 2. **Verify on GitHub Pages**

Open: https://cdolik.github.io/early-stage-github-signals/
Confirm:
- All cards fade in
- Sparkline animation on hover 
- Modal opens on click
- Footer and search function work
- Score model info appears and is readable on mobile/desktop

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
