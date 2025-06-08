#!/bin/bash
# Script to commit and push the investor-grade dashboard changes

# Display header
echo "========================================"
echo "Investor-Grade Dashboard Commit Process"
echo "========================================"

# Show status
echo -e "\n📋 Current Git Status:"
git status

# Ask for confirmation
echo -e "\n⚠️  This will commit all the investor-grade dashboard changes to main."
read -p "Continue? (y/n): " confirm

if [[ $confirm != "y" && $confirm != "Y" ]]; then
    echo "Commit process canceled."
    exit 0
fi

# Stage files
echo -e "\n📦 Staging files..."
git add docs/index.html docs/styles.css docs/dashboard.js
git add docs/DASHBOARD_IMPLEMENTATION.md README.md
git add scripts/validate_schema.py Makefile

# Show what's staged
echo -e "\n🔍 Files staged for commit:"
git diff --name-only --cached

# Ask for final confirmation
read -p "Proceed with commit? (y/n): " final_confirm

if [[ $final_confirm != "y" && $final_confirm != "Y" ]]; then
    echo "Commit process canceled."
    exit 0
fi

# Commit
echo -e "\n💾 Committing changes..."
git commit -m "feat: implement investor-grade dashboard UX improvements

- Replace email form with GitHub-native CTA
- Enhance metrics panel with icons and better styling
- Improve empty states with meaningful context
- Update visual hierarchy and typography
- Add comprehensive documentation updates"

# Push
echo -e "\n🚀 Pushing to main..."
git push origin main

echo -e "\n✅ Process completed!"
echo "Next: Verify the GitHub Pages deployment and create Phase 2 & 3 issues"
