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
    import jsonschema
except ImportError:
    print("Error: jsonschema package not found. Please install with 'pip install jsonschema'")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def validate_json_against_schema(json_file, schema_file):
    """
    Validates a JSON file against a JSON schema
    
    Args:
        json_file (str): Path to the JSON file to validate
        schema_file (str): Path to the JSON schema file
    
    Returns:
        bool: True if validation succeeds, False otherwise
    """
    try:
        # Load JSON data
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Load schema
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        
        # Validate
        jsonschema.validate(instance=data, schema=schema)
        logger.info(f"✅ {json_file} successfully validated against {schema_file}")
        return True
    
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        return False
    
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in {json_file}: {e}")
        logger.error(f"   Error at line {e.lineno}, column {e.colno}: {e.msg}")
        return False
    
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"❌ Validation error in {json_file}: {e.message}")
        # Get more detailed path information 
        path = " → ".join([str(p) for p in e.path]) if e.path else "root"
        logger.error(f"   Path to error: {path}")
        logger.error(f"   Schema path: {e.schema_path}")
        
        # Print the instance that failed validation
        if e.instance:
            if isinstance(e.instance, dict):
                logger.error(f"   Invalid object: {json.dumps(e.instance, indent=2)[:200]}...")
            else:
                logger.error(f"   Invalid value: {e.instance}")
        return False
    
    except Exception as e:
        logger.error(f"❌ Unexpected error validating {json_file}: {e}")
        return False

def main():
    # Ensure we're running from the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Files to validate
    api_schema = "schemas/api.schema.json"
    repo_schema = "schemas/repo.schema.json"
    repository_schema = "schemas/repository.schema.json"
    latest_api = "docs/api/latest.json"
    simplified_api = "docs/api/simplified.json"
    
    # Track validation success
    success = True
    
    # Validate API files
    logger.info("Validating API files against API schema...")
    if os.path.exists(latest_api):
        success = validate_json_against_schema(latest_api, api_schema) and success
    else:
        logger.warning(f"⚠️ File not found: {latest_api}")
    
    if os.path.exists(simplified_api):
        success = validate_json_against_schema(simplified_api, api_schema) and success
    
    # Validate latest reports against repo schema
    logger.info("Validating reports against repo schema...")
    reports_dir = os.path.join(project_root, "reports")
    if os.path.exists(reports_dir):
        json_reports = [f for f in os.listdir(reports_dir) if f.endswith('.json')]
        for report in json_reports[:2]:  # Validate the most recent 2 reports
            report_path = os.path.join(reports_dir, report)
            success = validate_json_against_schema(report_path, repo_schema) and success
    
    # Exit with appropriate code
    if not success:
        logger.error("❌ Schema validation failed")
        sys.exit(1)
    else:
        logger.info("✅ All schema validations passed")
        sys.exit(0)

if __name__ == "__main__":
    main()
