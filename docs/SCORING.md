# 📊 Scoring Methodology

## Overview
The Early-Stage GitHub Signals scoring system uses a 10-point scale to evaluate repository momentum across four key dimensions.

## Signal Breakdown

### 📈 Commit Surge (3 points)
**What it measures:** Development velocity and feature work quality
- **Trigger:** 10+ commits in 14 days
- **Bonus:** 3+ commits with "feat:" or "add" prefixes
- **Weight:** 30% of total score

### ⭐ Star Velocity (3 points)  
**What it measures:** Community traction and word-of-mouth growth
- **Trigger:** 10+ stars gained in 14 days
- **Analysis:** Rate of change vs. absolute numbers
- **Weight:** 30% of total score

### 👥 Team Traction (2 points)
**What it measures:** Sustainable development beyond solo projects
- **Trigger:** 2-5 contributors with 5+ commits each in 30 days
- **Sweet spot:** Small, active teams (not one-person shows or large enterprises)
- **Weight:** 20% of total score

### 🛠️ Dev-Tool Ecosystem Fit (2 points)
**What it measures:** Developer infrastructure relevance
- **Languages:** Python, TypeScript, Rust, Go
- **Topics:** "devops", "cli", "sdk", "api", "tools"
- **Focus:** Infrastructure that developers build with/on
- **Weight:** 20% of total score

## Scoring Scale

| Score Range | Classification | Description |
|-------------|----------------|-------------|
| **8.0 - 10.0** | 🔥 **Excellent** | High momentum across all signals |
| **6.0 - 7.9** | 🌟 **Good** | Strong momentum in most areas |
| **4.0 - 5.9** | ⚡ **Moderate** | Some promising signals |
| **2.0 - 3.9** | 📈 **Low** | Early stage, limited signals |
| **0.0 - 1.9** | 🌱 **Minimal** | Just starting, watching |

## Why These Signals Matter

### **Commit Patterns**
- Reveals active development vs. abandoned projects
- Feature commits indicate product advancement
- Consistent activity suggests sustainable development

### **Star Growth**
- Indicates market resonance and developer interest
- Velocity matters more than absolute numbers
- Word-of-mouth signal for quality/usefulness

### **Team Dynamics**
- Multi-contributor projects more likely to scale
- Excludes hobby projects and enterprise repos
- Sweet spot: startup-size teams (2-5 active devs)

### **Developer Tool Focus**
- Filters for infrastructure vs. end-user applications
- Focuses on tools that enable other developers
- Higher likelihood of VC interest and B2B potential

## Data Sources

- **GitHub API:** Repository metrics, commits, contributors
- **Hacker News:** Discussion signals and launch tracking
- **Product Hunt:** Product launch momentum

## Refresh Schedule

- **Data collection:** Every Monday at 6 AM UTC
- **Score calculation:** Real-time during collection
- **Dashboard update:** Automatic deployment via GitHub Actions

---

*This methodology is open source and continuously refined based on community feedback and market validation.*
