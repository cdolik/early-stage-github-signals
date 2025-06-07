#!/usr/bin/env python3
"""
Generate performance metrics for Early-Stage GitHub Signals project.
Reads historical JSON data from docs/data/*.json and calculates key metrics.
"""

import os
import json
import glob
from datetime import datetime, timedelta
import statistics
from collections import defaultdict

def load_json_files():
    """Load all JSON files from the data directory."""
    data_dir = os.path.join('docs', 'data')
    json_files = glob.glob(os.path.join(data_dir, '*.json'))
    
    all_data = []
    for file in json_files:
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                # Extract date from filename
                filename = os.path.basename(file)
                date_str = filename.split('.')[0]
                if date_str.lower() != 'latest':
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    data['date'] = date
                    all_data.append(data)
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    return all_data

def calculate_metrics(all_data):
    """Calculate performance metrics from JSON data."""
    if not all_data:
        print("No data files found.")
        return None
    
    # Prepare data structure
    all_scores = []
    all_qualifying_counts = defaultdict(int)  # week -> count
    
    recent_scores = []
    recent_qualifying_counts = defaultdict(int)  # week -> count
    
    # Calculate current date and 30 days ago
    current_date = datetime.now()
    thirty_days_ago = current_date - timedelta(days=30)
    
    # Process each data file
    for data in all_data:
        date = data.get('date')
        is_recent = date >= thirty_days_ago if date else False
        
        # Calculate week number for grouping
        week_number = date.isocalendar()[1] if date else 0
        year = date.year if date else 0
        week_key = f"{year}-W{week_number}"
        
        if 'repositories' in data:
            repos = data['repositories']
            for repo in repos:
                score = repo.get('score', 0)
                is_qualifying = score >= 7
                
                # Add to all-time metrics
                all_scores.append(score)
                if is_qualifying:
                    all_qualifying_counts[week_key] += 1
                
                # Add to recent metrics if applicable
                if is_recent:
                    recent_scores.append(score)
                    if is_qualifying:
                        recent_qualifying_counts[week_key] += 1
    
    # Calculate aggregate metrics
    metrics = {
        'last_30d': {
            'avg_qualifying': round(sum(recent_qualifying_counts.values()) / max(1, len(recent_qualifying_counts)), 1) if recent_qualifying_counts else 0,
            'median_score': round(statistics.median(recent_scores), 1) if recent_scores else 0,
            'highest_score': round(max(recent_scores), 1) if recent_scores else 0
        },
        'all_time': {
            'avg_qualifying': round(sum(all_qualifying_counts.values()) / max(1, len(all_qualifying_counts)), 1) if all_qualifying_counts else 0,
            'median_score': round(statistics.median(all_scores), 1) if all_scores else 0,
            'highest_score': round(max(all_scores), 1) if all_scores else 0
        }
    }
    
    return metrics

def generate_markdown_table(metrics):
    """Generate a markdown table from metrics."""
    if not metrics:
        return "No metrics data available."
    
    md = "| Metric | Last 30 days | All-time |\n"
    md += "|--------|--------------|----------|\n"
    md += f"| Avg repos ≥7/10 | {metrics['last_30d']['avg_qualifying']} | {metrics['all_time']['avg_qualifying']} |\n"
    md += f"| Median momentum score | {metrics['last_30d']['median_score']} | {metrics['all_time']['median_score']} |\n"
    md += f"| Highest weekly score | {metrics['last_30d']['highest_score']} | {metrics['all_time']['highest_score']} |\n"
    
    return md

def main():
    """Main function to generate metrics and output markdown."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate performance metrics for GitHub signals")
    parser.add_argument('--write', type=str, help='Path to write the markdown table')
    parser.add_argument('--json-dir', type=str, default='docs/data', help='Directory containing JSON data files')
    args = parser.parse_args()
    
    print("Generating performance metrics...")
    all_data = load_json_files()
    metrics = calculate_metrics(all_data)
    
    if metrics:
        md_table = generate_markdown_table(metrics)
        print("\nMarkdown Table for PROJECT_STATUS.md:")
        print("\n" + md_table)
        
        # Write to specified file if requested
        if args.write:
            with open(args.write, 'w') as f:
                f.write(md_table)
            print(f"\nTable saved to {args.write}")
        else:
            # Default output
            with open('metrics_table.md', 'w') as f:
                f.write(md_table)
            print("\nTable saved to metrics_table.md")
    else:
        print("Failed to generate metrics.")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
