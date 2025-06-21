#!/bin/bash
# run.sh - Simple entry point for Early Stage GitHub Signals
# This script provides a user-friendly interface for common operations

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Check if .env file exists, create from example if not
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "⚠️  .env file not found, creating from .env.example"
    cp .env.example .env
    echo "⚠️  Please edit .env to add your GitHub token"
fi

# Check if requirements are installed
if ! python3 -c "import dotenv" &> /dev/null; then
    echo "⚠️  Python dependencies not installed, installing now..."
    pip install -r requirements.txt
fi

# Display menu
echo "🚀 Early Stage GitHub Signals"
echo "----------------------------"
echo "1. Run lightweight analysis (5 repos)"
echo "2. Generate full report"
echo "3. View dashboard"
echo "4. Run tests"
echo "5. Setup development environment"
echo "6. Deploy to GitHub Pages"
echo "q. Quit"
echo

# Get user choice
read -p "Enter your choice: " choice

case $choice in
    1)
        echo "Running lightweight analysis..."
        python3 weekly_gems_cli.py --debug --max-repos 5 --skip-producthunt --skip-hackernews
        ;;
    2)
        echo "Generating full report..."
        python3 weekly_gems_cli.py
        ;;
    3)
        echo "Starting dashboard server..."
        cd docs && python3 -m http.server 8000 &
        echo "Opening browser..."
        sleep 2
        open http://localhost:8000 || python3 -c "import webbrowser; webbrowser.open('http://localhost:8000')" || xdg-open http://localhost:8000
        echo "Press Ctrl+C to stop the server when finished"
        wait
        ;;
    4)
        echo "Running tests..."
        python3 -m pytest
        ;;
    5)
        echo "Setting up development environment..."
        pip install -r requirements.txt -r requirements-dev.txt
        pre-commit install || echo "pre-commit not installed, skipping"
        echo "✅ Development environment setup complete"
        ;;
    6)
        echo "Deploying to GitHub Pages..."
        ./deployment.sh
        ;;
    q|Q)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo
echo "✅ Done!"
