#!/bin/bash
# run_pipeline.sh - Automate GitHub Signals collection and dashboard hosting

# Colors for console output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}===== GitHub Signals Pipeline =====${NC}"
echo -e "${YELLOW}Starting data collection and processing...${NC}"

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
  if [ -f .env ]; then
    echo "Loading GitHub token from .env file"
    export $(grep -v '^#' .env | xargs)
  else
    echo -e "${RED}ERROR: GITHUB_TOKEN not found. Set it in .env file or export it.${NC}"
    exit 1
  fi
fi

# Display token preview
if [ -n "$GITHUB_TOKEN" ]; then
  TOKEN_PREVIEW="${GITHUB_TOKEN:0:4}..."
  echo -e "Using GitHub token: ${TOKEN_PREVIEW}"
else
  echo -e "${RED}ERROR: GITHUB_TOKEN still not set${NC}"
  exit 1
fi

# Run the data collection process
echo -e "${YELLOW}Collecting GitHub data...${NC}"
python3 weekly_gems_cli.py --debug

# Check if the run was successful
if [ $? -ne 0 ]; then
  echo -e "${RED}ERROR: Data collection failed${NC}"
  exit 1
fi

# Validate the output files
echo -e "${YELLOW}Validating output files...${NC}"
LATEST_JSON=docs/api/latest.json

if [ -f "$LATEST_JSON" ]; then
  echo "Found latest.json file"
  
  # Check if file has valid JSON
  if ! jq empty "$LATEST_JSON" 2>/dev/null; then
    echo -e "${RED}ERROR: latest.json contains invalid JSON${NC}"
    exit 1
  fi
  
  # Check if repositories array exists and isn't empty
  REPO_COUNT=$(jq '.repositories | length' "$LATEST_JSON")
  if [ "$REPO_COUNT" -eq 0 ]; then
    echo -e "${RED}WARNING: No repositories found in output${NC}"
  else
    echo -e "${GREEN}Found $REPO_COUNT repositories in output${NC}"
  fi
  
  # Check for zero-value metrics
  ALL_ZEROS=$(jq '.repositories | map(.stars == 0 and .forks == 0) | all' "$LATEST_JSON")
  if [ "$ALL_ZEROS" = "true" ]; then
    echo -e "${RED}WARNING: All repositories have zero stars and forks${NC}"
    echo "This may indicate an issue with GitHub API access or data processing"
  fi
  
else
  echo -e "${RED}ERROR: latest.json file not found${NC}"
  exit 1
fi

# Serve the dashboard
echo -e "${GREEN}Starting dashboard server...${NC}"
echo "Dashboard will be available at: http://localhost:8000"
cd docs && python3 -m http.server 8000
