#!/usr/bin/env python3
"""
Schema Validation Script for GitHub Signals API
Validates that the generated API output conforms to the defined schema
"""

import json
import sys
import os
import logging
from pathlib import Path

try:
    from jsonschema import validate, ValidationError, RefResolver
except ImportError:
    print("Error: jsonschema package not found. Please install with 'pip install jsonschema'")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Set paths relative to project root
HERE = Path(__file__).parent
PROJECT_ROOT = HERE.parent
REPO_SCHEMA = PROJECT_ROOT / "schemas" / "repository.schema.json"
API_SCHEMA = PROJECT_ROOT / "schemas" / "api.schema.json"
SIMPLIFIED_SCHEMA = PROJECT_ROOT / "schemas" / "simplified.schema.json"
WEEKLY_GEMS_SCHEMA = PROJECT_ROOT / "schemas" / "weekly_gems.schema.json"

def validate_json(json_path: Path, schema_path: Path):
    """
    Validate a JSON file against a schema.
    
    Args:
        json_path: Path to the JSON file to validate
        schema_path: Path to the schema file
        
    Raises:
        ValueError: If validation fails
    """
    try:
        with json_path.open() as f:
            data = json.load(f)
        
        with schema_path.open() as f:
            schema = json.load(f)
        
        # Create a resolver for schema references
        schema_dir = schema_path.parent
        
        # Load all schema files in the directory for resolution
        store = {}
        for schema_file in schema_dir.glob("*.schema.json"):
            with schema_file.open() as f:
                store[schema_file.name] = json.load(f)
        
        resolver = RefResolver(
            base_uri=schema_dir.as_uri() + "/",
            referrer=schema,
            store=store
        )
        
        validate(instance=data, schema=schema, resolver=resolver)
        logger.info(f"✅ {json_path.name} successfully validated")
        
    except ValidationError as e:
        raise ValueError(f"{json_path.name}: {e.message}")
    except FileNotFoundError as e:
        raise ValueError(f"File not found: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {json_path.name}: {e}")

def validate_json_against_schema(json_file, schema_file):
    """
    Legacy function for backward compatibility
    """
    try:
        json_path = Path(json_file)
        schema_path = Path(schema_file)
        validate_json(json_path, schema_path)
        return True
    except ValueError as e:
        logger.error(f"❌ {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

def main():
    # Ensure we're running from the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Track validation success
    success = True
    
    # Validate API files against their respective schemas
    logger.info("Validating API files against their schemas...")
    
    # Validate latest.json against API schema
    latest_file = PROJECT_ROOT / "docs" / "api" / "latest.json"
    if latest_file.exists():
        success = validate_json_against_schema(str(latest_file), str(API_SCHEMA)) and success
    else:
        logger.warning(f"⚠️ File not found: {latest_file}")
    
    # Validate simplified.json against simplified schema
    simplified_file = PROJECT_ROOT / "docs" / "api" / "simplified.json"
    if simplified_file.exists():
        success = validate_json_against_schema(str(simplified_file), str(SIMPLIFIED_SCHEMA)) and success
    else:
        logger.warning(f"⚠️ File not found: {simplified_file}")
    
    # Validate data files against API schema
    logger.info("Validating data files against API schema...")
    data_dir = PROJECT_ROOT / "docs" / "data"
    if data_dir.exists():
        json_files = [f for f in data_dir.iterdir() if f.suffix == '.json' and not f.name.startswith('_')]
        for data_file in json_files[:2]:  # Validate the most recent 2 files
            success = validate_json_against_schema(str(data_file), str(API_SCHEMA)) and success
    
    # Validate weekly reports against weekly gems schema  
    logger.info("Validating weekly reports against weekly gems schema...")
    reports_dir = PROJECT_ROOT / "reports"
    if reports_dir.exists():
        json_reports = [f for f in reports_dir.iterdir() if f.suffix == '.json']
        for report in json_reports[:2]:  # Validate the most recent 2 reports
            success = validate_json_against_schema(str(report), str(WEEKLY_GEMS_SCHEMA)) and success
    
    # Exit with appropriate code
    if not success:
        logger.error("❌ Schema validation failed")
        sys.exit(1)
    else:
        logger.info("✅ All schema validations passed")
        sys.exit(0)

if __name__ == "__main__":
    main()
