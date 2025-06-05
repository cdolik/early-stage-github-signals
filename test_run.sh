#!/bin/bash
# Quick test script for the Early Stage GitHub Signals platform

echo "Running GitHub Signals platform in test mode..."
python3 run.py --debug --lite --max-repos 5 --skip-hackernews
