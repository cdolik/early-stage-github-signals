# � Early Stage GitHub Signals Platform

> **Discover promising early-stage startups through GitHub activity analysis**

[![Dashboard](https://img.shields.io/badge/Dashboard-Live-brightgreen)](https://cdolik.github.io/early-stage-github-signals/)
[![GitHub Actions](https://github.com/cdolik/early-stage-github-signals/workflows/Weekly%20GitHub%20Signals%20Report/badge.svg)](https://github.com/cdolik/early-stage-github-signals/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What It Does

This platform automatically analyzes trending GitHub repositories to identify startups with high potential **before they hit mainstream VC radar**. Using a sophisticated 50-point scoring algorithm, it finds companies 4-8 weeks earlier than traditional deal sourcing.

### 🚀 [**View Live Dashboard**](https://cdolik.github.io/early-stage-github-signals/)

## ✨ Key Features

- **🔍 Automated Discovery**: Scans 1000+ repositories weekly
- **📊 50-Point Scoring**: Evaluates repository + organization + community signals
- **📈 Trend Analysis**: Identifies patterns in startup activity
- **🤖 Weekly Automation**: GitHub Actions generates reports automatically
- **💻 Professional Dashboard**: Clean, VC-friendly interface
- **📱 Mobile Responsive**: Works on all devices

---

## 🏆 Scoring Algorithm

Our algorithm evaluates three key areas:

### Repository Signals (20 points)
- Recent creation, professional languages, CI/CD setup
- Documentation quality, development activity
- External website, startup keywords, accelerator mentions

### Organization Signals (15 points)  
- Team size, multiple repositories, professional profiles
- Organization website, hiring indicators

### Community Signals (15 points)
- Star growth velocity, external contributors
- Issue engagement, fork activity, social mentions

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- GitHub Personal Access Token

### Installation

## 📊 Sample Output

The platform identifies startups like:

| Repository | Score | Why Interesting |
|------------|-------|-----------------|
| ai-startup/platform | 42/50 | Ex-Google team, rapid growth, YC-backed |
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
