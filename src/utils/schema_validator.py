"""
JSON Schema Validator for the Early Stage GitHub Signals platform.
"""
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# JSON Schema for repository objects
REPOSITORY_SCHEMA = {
    "type": "object",
    "required": ["name", "full_name", "url", "description", "score", "signals"],
    "properties": {
        "name": {"type": "string"},
        "full_name": {"type": "string"},
        "url": {"type": "string", "format": "uri"},
        "description": {"type": ["string", "null"]},
        "score": {"type": "number", "minimum": 0, "maximum": 10},
        "signals": {
            "type": "object",
            "required": ["commit_surge", "star_velocity", "team_traction", "ecosystem_fit"],
            "properties": {
                "commit_surge": {"type": "number", "minimum": 0, "maximum": 3},
                "star_velocity": {"type": "number", "minimum": 0, "maximum": 3},
                "team_traction": {"type": "number", "minimum": 0, "maximum": 2},
                "ecosystem_fit": {"type": "number", "minimum": 0, "maximum": 2}
            }
        },
        "metrics": {
            "type": "object",
            "properties": {
                "stars": {"type": "number"},
                "stars_gained_14d": {"type": "number"},
                "commits_14d": {"type": "number"},
                "contributors_30d": {"type": "number"}
            }
        },
        "language": {"type": ["string", "null"]},
        "date_analyzed": {"type": "string", "format": "date-time"}
    }
}

# JSON Schema for the API output
API_SCHEMA = {
    "type": "object",
    "required": ["date", "date_generated", "repositories"],
    "properties": {
        "date": {"type": "string", "format": "date"},
        "date_generated": {"type": "string", "format": "date-time"},
        "repositories": {
            "type": "array",
            "items": REPOSITORY_SCHEMA
        }
    }
}


class SchemaValidator:
    """JSON Schema validator for the Early Stage GitHub Signals platform."""
    
    def __init__(self):
        try:
            # Only import if used to avoid dependency issues
            from jsonschema import validate, ValidationError
            self.validate = validate
            self.ValidationError = ValidationError
            self.has_jsonschema = True
        except ImportError:
            logger.warning("jsonschema package not found. Schema validation disabled.")
            self.has_jsonschema = False
    
    def validate_repository(self, repo: Dict[str, Any]) -> bool:
        """
        Validate a repository object against the repository schema.
        
        Args:
            repo: Repository object to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not self.has_jsonschema:
            return True
        
        try:
            self.validate(instance=repo, schema=REPOSITORY_SCHEMA)
            return True
        except self.ValidationError as e:
            logger.error(f"Repository validation error: {e}")
            return False
    
    def validate_api_output(self, data: Dict[str, Any]) -> bool:
        """
        Validate the complete API output against the API schema.
        
        Args:
            data: API data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not self.has_jsonschema:
            return True
        
        try:
            self.validate(instance=data, schema=API_SCHEMA)
            return True
        except self.ValidationError as e:
            logger.error(f"API output validation error: {e}")
            return False


def generate_schema_docs() -> str:
    """
    Generate documentation for the JSON schema.
    
    Returns:
        String with markdown documentation
    """
    docs = """# Early Stage GitHub Signals API Schema

## Repository Object

```json
{
  "name": "example-dev/tool-x",
  "full_name": "example-dev/tool-x",
  "url": "https://github.com/example-dev/tool-x",
  "description": "A next-gen developer utility for code optimization",
  "score": 8.5,
  "signals": {
    "commit_surge": 3,
    "star_velocity": 2.5,
    "team_traction": 2,
    "ecosystem_fit": 1
  },
  "metrics": {
    "stars": 127,
    "stars_gained_14d": 24,
    "commits_14d": 18,
    "contributors_30d": 3
  },
  "language": "TypeScript",
  "date_analyzed": "2025-06-06T09:15:24Z"
}
```

## API Output Schema

```json
{
  "date": "2025-06-06",
  "date_generated": "2025-06-06T09:15:24Z",
  "repositories": [
    {
      // Repository object (see above)
    }
  ]
}
```
"""
    return docs


if __name__ == "__main__":
    # Generate documentation when run directly
    print(generate_schema_docs())
