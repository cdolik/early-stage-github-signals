#!/bin/bash
# Weekly Dev Tools Gems - MVP Run Script
# Run this script every Monday morning to generate the weekly report

# Set up environment
export PATH=$PATH:/usr/local/bin
cd "$(dirname "$0")"

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "Loading environment from .env file"
    export $(grep -v '^#' .env | xargs)
fi

# Check if GitHub token is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️ GITHUB_TOKEN not set. Some scoring features will be limited."
    echo "To set: export GITHUB_TOKEN='your_token'"
fi

echo "🚀 Running Weekly Dev Tools Gems - $(date '+%Y-%m-%d')"

# Run the weekly gems CLI
python3 ./weekly_gems_cli.py --debug

# Check exit status
if [ $? -eq 0 ]; then
    echo "✅ Successfully generated weekly report"
    
    # Show the report
    LATEST_REPORT="reports/weekly_gems_latest.md"
    if [ -f "$LATEST_REPORT" ]; then
        echo -e "\n📊 Report Preview:"
        echo "------------------------"
        cat "$LATEST_REPORT" | head -10
        echo "... (see full report in $LATEST_REPORT)"
        echo "------------------------"
    fi
    
    echo -e "\n🔍 Next steps:"
    echo "1. Review the full report in the reports folder"
    echo "2. Add VC hooks to the most promising repositories"
    echo "3. Share the report with your network"
else
    echo "❌ Error generating weekly report"
fi
