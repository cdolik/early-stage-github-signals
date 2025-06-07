# LLM Prompts for Early-Stage GitHub Signals

This document provides ready-to-use prompts for interacting with LLMs like GitHub Copilot, ChatGPT, or Claude when working with the Early-Stage GitHub Signals project. These prompts are designed to help with common tasks and ensure consistent outputs.

## Analysis Prompts

### Signal Enhancement

```
Analyze these GitHub momentum signals used in our 10-point scoring system:
- Commit Surge (3 points): 10+ commits in 14 days, 3+ with "feat:" or "add" 
- Star Velocity (3 points): 10+ stars gained in 14 days
- Team Traction (2 points): 2-5 contributors with 5+ commits each in 30 days
- Dev Ecosystem Fit (2 points): Python/TypeScript/Rust or specific topics

Suggest 2-3 additional signals that would help identify promising early-stage dev tools, with specific thresholds and point values. Focus on signals that indicate genuine momentum, not vanity metrics.
```

### Repository Analysis

```
Given this repository data from our Early-Stage GitHub Signals platform:

{
  "name": "example/repo",
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
  }
}

Analyze this repository's strengths and potential as an early-stage project. What does this signal pattern suggest about its development status and community engagement?
```

## Code Enhancement Prompts

### Scoring Algorithm Enhancement

```
Review this scoring algorithm from our momentum_scorer.py:

[PASTE CODE HERE]

Suggest optimizations or refinements that would:
1. Make the scoring more adaptive to repository size/age
2. Reduce false positives from marketing-driven spikes
3. Better identify organic, sustainable growth patterns

Provide concrete implementation suggestions with Python code snippets.
```

### Schema Validation

```
Given our JSON schema for the Early-Stage GitHub Signals API:

[PASTE SCHEMA HERE]

Suggest improvements to make this schema more robust and useful for consumers. Include:
1. Any missing fields that would be valuable
2. Better field descriptions or examples
3. Additional validation rules to ensure data quality
```

## Data Analysis Prompts

### Trend Analysis

```
Here are the weekly qualifying repository counts from our platform over the past 10 weeks:
[3, 2, 4, 0, 1, 3, 5, 2, 0, 3]

And the average scores of all analyzed repositories:
[6.8, 7.1, 7.3, 6.5, 6.7, 7.2, 7.6, 7.0, 6.6, 7.2]

What patterns do you observe? Are there any insights about GitHub project cycles or seasonal trends that might explain these variations? How might we adjust our algorithm to account for these patterns?
```

### Repository Comparison

```
Compare these two repositories that both scored 8/10:

Repository A:
- Strong commit surge (3/3)
- Moderate star velocity (2/3)
- Strong team traction (2/2)
- Low ecosystem fit (1/2)

Repository B:
- Moderate commit surge (1/3)
- Strong star velocity (3/3)
- Strong team traction (2/2)
- Strong ecosystem fit (2/2)

Which repository pattern typically indicates a more promising early-stage project? What follow-up analysis would you recommend to differentiate them further?
```

## Contribution Guidelines

When adding new prompts to this file:

1. Ensure prompts are clear and specific
2. Include placeholder markers for variable content
3. Group related prompts under appropriate headings
4. Test prompts with multiple LLMs to ensure consistent results
