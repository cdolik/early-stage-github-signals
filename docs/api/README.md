# API Documentation

The Early-Stage GitHub Signals platform provides JSON API endpoints that can be used to access repository data programmatically.

## API Endpoints

### Latest Data

**Endpoint**: `/api/latest.json`

Contains the most recent set of analyzed repositories with full details.

### Simplified Data

**Endpoint**: `/api/simplified.json`

Contains a streamlined version of the latest data with only essential fields.

### Historical Data

**Endpoint**: `/data/{YYYY-MM-DD}.json`

Contains historical data snapshots for specific dates.

## Schema Documentation

### Repository Object

```json
{
  "name": "example-dev/tool-x",
  "full_name": "example-dev/tool-x",
  "repo_url": "https://github.com/example-dev/tool-x",
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

#### Field Definitions

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `name` | string | Repository name in format "owner/repo" | Yes |
| `full_name` | string | Full repository name | Yes |
| `repo_url` | string | Repository URL | Yes |
| `description` | string | Repository description | Yes |
| `score` | number | Overall score (0-10) | Yes |
| `signals` | object | Contains the individual signal scores | Yes |
| `signals.commit_surge` | number | Commit activity score (0-3) | Yes |
| `signals.star_velocity` | number | Star growth velocity score (0-3) | Yes |
| `signals.team_traction` | number | Team collaboration score (0-2) | Yes |
| `signals.ecosystem_fit` | number | Developer ecosystem fit score (0-2) | Yes |
| `metrics` | object | Raw metrics used in scoring | No |
| `metrics.stars` | number | Total stars | No |
| `metrics.stars_gained_14d` | number | Stars gained in last 14 days | No |
| `metrics.commits_14d` | number | Commits in last 14 days | No |
| `metrics.contributors_30d` | number | Contributors in last 30 days | No |
| `language` | string | Primary programming language | Yes |
| `ecosystem` | string | Category (Frontend, Backend, DevOps, Data/AI, DevTools) | Yes |
| `date_analyzed` | string | ISO 8601 datetime when repository was analyzed | Yes |
| `score_change` | number | Score change since last analysis | No |
| `trend` | array/string | Score trend data | No |
| `why_matters` | string | Explanation of why this repository matters | No |

### API Response Object

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

#### Field Definitions

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `date` | string | Report date in YYYY-MM-DD format | Yes |
| `date_generated` | string | Generation timestamp in ISO 8601 format | Yes |
| `repositories` | array | Array of repository objects | Yes |

## Using the API

### Example: Fetch Latest Data

```javascript
// Using fetch API in JavaScript
fetch('https://example.com/early-stage-github-signals/api/latest.json')
  .then(response => response.json())
  .then(data => {
    // Process data
    console.log(`Found ${data.repositories.length} repositories`);
    
    // Get repositories with score >= 8
    const highPotential = data.repositories
      .filter(repo => repo.score >= 8)
      .sort((a, b) => b.score - a.score);
      
    console.log('High potential repositories:', highPotential);
  });
```

### Example: Python Client

```python
import requests
import json

def get_high_potential_repos(min_score=7):
    """Get repositories with high potential."""
    url = "https://example.com/early-stage-github-signals/api/latest.json"
    response = requests.get(url)
    data = response.json()
    
    high_potential = [
        repo for repo in data["repositories"] 
        if repo["score"] >= min_score
    ]
    
    return sorted(high_potential, key=lambda x: x["score"], reverse=True)

if __name__ == "__main__":
    repos = get_high_potential_repos()
    print(f"Found {len(repos)} high-potential repositories")
    
    for repo in repos:
        print(f"{repo['name']} ({repo['score']}/10): {repo['description']}")
```

## Rate Limits and Usage Guidelines

The API is for informational purposes and does not employ rate limiting. However, we recommend:

1. Caching responses locally when possible
2. Limiting requests to once per hour for live applications
3. Using the simplified API endpoint for lightweight applications

## Status Codes

- **200 OK**: Request was successful
- **404 Not Found**: Requested resource does not exist
- **500 Internal Server Error**: Server-side error

## Questions and Support

For questions or support regarding the API, please open an issue on the GitHub repository.
