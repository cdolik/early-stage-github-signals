#!/bin/bash
# deployment.sh
# Script to run the data pipeline and deploy to GitHub Pages

set -e  # Exit on any error

# Change to the directory where the script is located
cd "$(dirname "$0")"

echo "🚀 Starting Early Stage GitHub Signals deployment process..."
echo "💻 Running on $(uname -a)"
echo "📅 Date: $(date)"

# 1. Load environment variables
if [ -f ".env" ]; then
    echo "📁 Loading environment variables from .env"
    export $(grep -v '^#' .env | xargs)
else
    echo "⚠️ No .env file found"
    if [ -z "$GITHUB_TOKEN" ]; then
        echo "❌ GITHUB_TOKEN is not set. Please create a .env file or set it in the environment."
        exit 1
    fi
fi

# 2. Run the data pipeline
echo "🔄 Running data pipeline..."
python3 weekly_gems_cli.py --debug
if [ $? -ne 0 ]; then
    echo "❌ Data pipeline failed"
    exit 1
fi

# 3. Validate data quality
echo "✅ Validating data quality..."
python3 scripts/validate_data_quality.py
if [ $? -ne 0 ]; then
    echo "❌ Data quality validation failed"
    exit 1
fi

# 4. Copy the latest report to README for GitHub Pages
echo "📋 Updating GitHub Pages README..."
cp reports/weekly_gems_latest.md docs/README.md

# 5. Add date to index.html if it's not already there
latest_date=$(date +"%Y-%m-%d")
if ! grep -q "$latest_date" docs/index.html; then
    echo "📆 Adding today's date to index.html..."
    sed -i '' "s/<h1>Early Stage GitHub Signals<\/h1>/<h1>Early Stage GitHub Signals - $latest_date<\/h1>/" docs/index.html
fi

# 6. Commit changes to GitHub Pages (if git is available and in a git repo)
if command -v git &> /dev/null && [ -d ".git" ]; then
    echo "🔄 Committing changes to GitHub Pages..."
    git add docs/
    git add reports/
    git commit -m "Update GitHub Pages with data from $latest_date"
    
    echo "🌐 Changes committed! To deploy, push to the main branch:"
    echo "git push origin main"
else
    echo "⚠️ Not a git repository or git not available. Skipping commit step."
    echo "🌐 To deploy to GitHub Pages, commit the changes in the 'docs/' folder."
fi

echo "✨ Deployment preparation complete!"
echo "📊 View the dashboard locally: python3 -m http.server 8000 --directory docs"
