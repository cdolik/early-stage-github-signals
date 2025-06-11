#!/usr/bin/env python3
"""
Backfill data files in docs/data/ directory from existing API files.
This script copies API JSON data from docs/api/ to docs/data/ to ensure consistency.
"""
import os
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logger import setup_logger

logger = setup_logger("BackfillDataFiles")

def backfill_data_files():
    """
    Copy API JSON files to data directory with the same structure.
    """
    # Define directories
    api_dir = Path('docs/api')
    data_dir = Path('docs/data')
    
    # Ensure data directory exists
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all JSON files in the API directory (except simplified.json)
    api_files = [f for f in api_dir.glob('*.json') if f.name != 'simplified.json' and f.name != 'latest.json']
    
    for api_file in api_files:
        # Create corresponding data file path
        data_file = data_dir / api_file.name
        
        logger.info(f"Processing: {api_file}")
        
        # If file doesn't exist in data directory, copy it
        if not data_file.exists():
            logger.info(f"Copying {api_file} to {data_file}")
            
            try:
                # Load API data
                with open(api_file, 'r') as f:
                    api_data = json.load(f)
                
                # Write to data directory
                with open(data_file, 'w') as f:
                    json.dump(api_data, f, indent=2)
                    
                logger.info(f"Successfully created {data_file}")
            except Exception as e:
                logger.error(f"Error copying {api_file} to {data_file}: {e}")
        else:
            logger.info(f"File {data_file} already exists, skipping")
    
    logger.info("Backfill complete.")

if __name__ == "__main__":
    backfill_data_files()
