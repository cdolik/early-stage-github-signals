"""
JSON Schema Validator for the Early Stage GitHub Signals platform.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def validate_repo(repo: dict) -> None:
    """Validate a repository object against the repo schema."""
    schema_path = Path(__file__).parents[2] / "schemas/repo.schema.json"
    schema = json.load(open(schema_path))
    try:
        from jsonschema import validate, ValidationError
        validate(instance=repo, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Schema validation failed: {e.message}")
    except ImportError:
        logger.warning("jsonschema package not found. Schema validation disabled.")


class SchemaValidator:
    """JSON Schema validator for the Early Stage GitHub Signals platform."""
    
    def __init__(self, schema_dir: str = None):
        """
        Initialize the schema validator.
        
        Args:
            schema_dir: Directory containing schema files (defaults to project schemas/)
        """
        if schema_dir is None:
            # Default to project's schemas directory
            project_root = Path(__file__).parent.parent.parent
            schema_dir = project_root / "schemas"
        else:
            schema_dir = Path(schema_dir)
            
        self.schema_dir = schema_dir
        
        try:
            # Only import if used to avoid dependency issues
            from jsonschema import validate, ValidationError, RefResolver
            self.validate = validate
            self.ValidationError = ValidationError
            self.RefResolver = RefResolver
            self.has_jsonschema = True
        except ImportError:
            logger.warning("jsonschema package not found. Schema validation disabled.")
            self.has_jsonschema = False
    
    def _load_schema(self, schema_name: str) -> Dict[str, Any]:
        """
        Load a schema from the schemas directory.
        
        Args:
            schema_name: Name of the schema file (without extension)
            
        Returns:
            Loaded schema dictionary
        """
        schema_path = self.schema_dir / f"{schema_name}.schema.json"
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
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
            schema = self._load_schema("repository")
            resolver = self._create_resolver(schema)
            self.validate(instance=repo, schema=schema, resolver=resolver)
            return True
        except (self.ValidationError, FileNotFoundError) as e:
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
            schema = self._load_schema("api")
            resolver = self._create_resolver(schema)
            self.validate(instance=data, schema=schema, resolver=resolver)
            return True
        except (self.ValidationError, FileNotFoundError) as e:
            logger.error(f"API output validation error: {e}")
            return False

    def _create_resolver(self, schema: Dict[str, Any]):
        """
        Create a resolver for schema references.
        
        Args:
            schema: The main schema
            
        Returns:
            RefResolver instance
        """
        # Load all schema files in the directory for resolution
        store = {}
        for schema_file in self.schema_dir.glob("*.schema.json"):
            with schema_file.open() as f:
                store[schema_file.name] = json.load(f)
        
        return self.RefResolver(
            base_uri=self.schema_dir.as_uri() + "/",
            referrer=schema,
            store=store
        )
    
    def get_validation_errors(self, data: Dict[str, Any], schema_name: str) -> List[str]:
        """
        Get detailed validation errors for debugging.
        
        Args:
            data: Data to validate
            schema_name: Name of the schema to validate against
            
        Returns:
            List of error messages
        """
        if not self.has_jsonschema:
            return []
        
        try:
            schema = self._load_schema(schema_name)
            resolver = self._create_resolver(schema)
            self.validate(instance=data, schema=schema, resolver=resolver)
            return []
        except self.ValidationError as e:
            return [str(e)]
        except FileNotFoundError as e:
            return [f"Schema not found: {e}"]
