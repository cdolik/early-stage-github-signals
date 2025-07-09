#!/usr/bin/env python3
"""
Validation script to verify JSON data quality
Checks that metrics and scores are non-zero in the latest dashboard data
"""
import os
import json
import sys
from pathlib import Path

def main():
    print("🔍 Validating JSON data quality...")
    
    # Define paths
    project_root = Path(__file__).parent.parent
    api_dir = project_root / "docs" / "api"
    latest_json_path = api_dir / "latest.json"
    
    if not latest_json_path.exists():
        print(f"❌ Error: {latest_json_path} does not exist")
        sys.exit(1)
    
    # Load JSON data
    try:
        with open(latest_json_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {latest_json_path}: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading {latest_json_path}: {str(e)}")
        sys.exit(1)
    
    # Verify structure
    if 'repositories' not in data:
        print("❌ Error: 'repositories' key not found in JSON data")
        sys.exit(1)
    
    if not data['repositories']:
        print("❌ Error: No repositories found in the data")
        sys.exit(1)
    
    # Check metrics and scores
    all_scores_zero = True
    all_metrics_zero = True
    repos_checked = 0
    
    print(f"\nChecking {len(data['repositories'])} repositories:")
    
    for repo in data['repositories']:
        repos_checked += 1
        name = repo.get('name', 'Unknown')
        full_name = repo.get('full_name', name)
        
        # Check score
        score = repo.get('score', 0)
        if score > 0:
            all_scores_zero = False
        
        # Check metrics
        metrics = repo.get('metrics', {})
        metrics_non_zero = False
        
        for metric_name, value in metrics.items():
            if metric_name not in ['avg_issue_resolution_days'] and value > 0:
                metrics_non_zero = True
                break
        
        if metrics_non_zero:
            all_metrics_zero = False
        
        # Report on this repository
        status = "✅" if score > 0 and metrics_non_zero else "⚠️"
        print(f"{status} {full_name}: Score={score}, Has metrics={metrics_non_zero}")
    
    # Overall assessment
    print("\n=== Validation Results ===")
    if all_scores_zero:
        print("❌ CRITICAL: All repository scores are zero!")
    else:
        print("✅ Some repositories have non-zero scores.")
    
    if all_metrics_zero:
        print("❌ CRITICAL: All repository metrics are zero!")
    else:
        print("✅ Some repositories have non-zero metrics.")
    
    # Final verdict
    if all_scores_zero or all_metrics_zero:
        print("\n❌ VALIDATION FAILED: Data quality issues detected.")
        sys.exit(1)
    else:
        print("\n✅ VALIDATION PASSED: Data quality looks good!")
        sys.exit(0)

if __name__ == "__main__":
    main()
