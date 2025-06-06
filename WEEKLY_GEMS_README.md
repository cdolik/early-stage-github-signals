# Weekly Dev Tools Gems

> **Discover promising early-stage dev tools startups through GitHub momentum signals**

## 🎯 What It Does

This platform identifies early-stage developer tools startups with high momentum using a focused 10-point scoring system. It helps you find high-potential projects **before they hit mainstream VC radar**.

## ✨ Key Features

- **🔍 Multi-Source Discovery**: GitHub Trending + Product Hunt + Hacker News
- **📊 10-Point Scoring**: Focused on meaningful momentum signals
- **🔥 Quality Threshold**: Only surfaces repos scoring 7+/10 points 
- **💻 Weekly Report**: Clean, VC-friendly markdown output
- **⚡ Fast Execution**: 30-minute weekly workflow

## 🏆 Focused 10-Point Scoring System

Our algorithm focuses exclusively on momentum signals that matter:

1. **Commit Surge (3 pts)**: 10+ commits in 14 days, 3+ with "feat:" or "add"
2. **Star Velocity (3 pts)**: 10+ stars gained in 14 days  
3. **Team Traction (2 pts)**: 2-5 contributors with 5+ commits each in 30 days
4. **Dev Ecosystem Fit (2 pts)**: Python/TypeScript/Rust OR topics like "devops", "cli", "sdk"

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- GitHub Personal Access Token (optional, enhances scoring accuracy)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/early-stage-github-signals.git
cd early-stage-github-signals

# Install dependencies
pip install -r requirements.txt

# Set your GitHub token (optional but recommended)
export GITHUB_TOKEN="your_github_token"
```

### Running the Platform

```bash
# Generate this week's report
./run_weekly_gems.sh
```

## 📊 Sample Output

```markdown
# Weekly Dev Tools Gems - 2025-06-03
*USA-focused, GitHub ecosystem, seed-stage*

*Quality threshold: 7+/10 points*

1. **[ai-startup/platform](https://github.com/ai-startup/platform)** - 8/10 points
   - Signals: 15 commits in last 14 days (4 feature commits), 300 stars gained in last 14 days
   - VC Hook: An AI platform for startups to automate workflows
```

## 🔄 Weekly Workflow

1. **Monday Morning (20 minutes)**
   - Run `./run_weekly_gems.sh` to generate the weekly report
   - Review the discoveries and add VC hooks if needed

2. **Monday Afternoon (10 minutes)**
   - Share the report with your network
   - Track interesting discoveries for follow-up

## 🛠️ Architecture

The platform is designed for simplicity and efficiency:

- **Collectors**: Scrape GitHub Trending, Product Hunt, and Hacker News
- **Analyzer**: Apply the 10-point momentum scoring system
- **Generator**: Produce the weekly markdown report

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
