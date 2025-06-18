# src/analyzers/venture_scorer.py
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone

class VentureScorer:
    """
    A sophisticated scoring mechanism designed to identify early-stage OSS projects
    with high venture potential. It prioritizes quality signals over raw quantity,
    focusing on indicators of strong teams, novel solutions, and emerging traction.
    """

    # Define weights for different scoring criteria
    # These would be fine-tuned based on backtesting and investor feedback
    WEIGHTS = {
        "stars_velocity": 0.15,          # Rapid star growth
        "forks_velocity": 0.10,          # Growing community interest in contributing/extending
        "contributor_growth": 0.20,      # Expanding and active contributor base
        "issue_resolution_rate": 0.10,   # Healthy project maintenance and responsiveness
        "commit_frequency": 0.10,        # Active development
        "novelty_signal": 0.25,          # Uniqueness, problem-solution fit (harder to quantify, may need NLP/manual input)
        "founder_signal": 0.10,          # Experienced or reputable founders/core team (may need external data)
        "documentation_quality": 0.05,   # Good documentation indicates maturity
        "recent_activity_bonus": 0.05    # Bonus for very recent significant activity
    }

    # Define thresholds for "high signal"
    THRESHOLDS = {
        "min_stars_for_velocity": 50,
        "min_commits_for_frequency": 10,
        "min_contributors_for_growth": 2,
        "ideal_issue_resolution_days": 7, # Issues resolved within a week
        "recent_activity_window_days": 30 # Look at activity in the last month
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config if config else {}
        # Potentially load more specific configs or API keys if needed for external data

    def _normalize(self, value: float, max_value: float, min_value: float = 0.0) -> float:
        """Normalize a value to a 0-1 scale."""
        if max_value == min_value:
            return 0.0 if value <= min_value else 1.0 # Handle division by zero or flat data
        return max(0.0, min(1.0, (value - min_value) / (max_value - min_value)))

    def _calculate_velocity(self, current_value: int, previous_value: int, days_diff: int) -> float:
        """Calculate per-day velocity."""
        if days_diff <= 0:
            return 0.0
        return (current_value - previous_value) / days_diff

    def score_repository(self, repo_data: Dict[str, Any], history_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Scores a single repository based on venture potential.

        Args:
            repo_data: Current data for the repository.
                       Expected keys: 'stars', 'forks', 'open_issues_count', 'closed_issues_count',
                                      'commits_this_month', 'contributors_count', 'description',
                                      'topics', 'created_at', 'pushed_at', 'owner_type', 'owner_is_org_member' (example custom signal)
            history_data: Historical data for the repository (e.g., from previous weeks/months)
                          to calculate velocities. Example: [{'date': 'YYYY-MM-DD', 'stars': X, 'forks': Y}]

        Returns:
            A dictionary containing the overall score and a breakdown of individual signal scores.
            {
                "score": float (0-10 scale),
                "signals": {
                    "stars_velocity_score": float,
                    "forks_velocity_score": float,
                    # ... other signal scores
                },
                "justification": "A brief explanation of why this repo is promising."
            }
        """
        # Extract relevant fields
        now = datetime.now(timezone.utc)
        signals = {}
        justifications = []
        score = 0.0
        # 1. Star velocity
        stars = repo_data.get("stargazers_count", 0)
        stars_14d = repo_data.get("stars_gained_14d", 0)
        star_velocity = self._normalize(stars_14d, 100, 0)
        signals["star_velocity"] = star_velocity
        if stars_14d >= self.THRESHOLDS["min_stars_for_velocity"]:
            justifications.append(f"High star velocity: {stars_14d} stars in last 14d.")
            score += self.WEIGHTS["stars_velocity"] * star_velocity
        # 2. Fork velocity
        forks = repo_data.get("forks_count", 0)
        forks_14d = repo_data.get("forks_gained_14d", 0)
        fork_velocity = self._normalize(forks_14d, 20, 0)
        signals["fork_velocity"] = fork_velocity
        if forks_14d > 0:
            score += self.WEIGHTS["forks_velocity"] * fork_velocity
        # 3. Contributor growth
        contributors_30d = repo_data.get("contributors_30d", 0)
        contributor_growth = self._normalize(contributors_30d, 10, 0)
        signals["contributor_growth"] = contributor_growth
        if contributors_30d >= self.THRESHOLDS["min_contributors_for_growth"]:
            justifications.append(f"Active contributor growth: {contributors_30d} contributors in last 30d.")
            score += self.WEIGHTS["contributor_growth"] * contributor_growth
        # 4. Issue resolution rate
        avg_issue_days = repo_data.get("avg_issue_resolution_days", 30)
        issue_resolution = self._normalize(self.THRESHOLDS["ideal_issue_resolution_days"], avg_issue_days, 1)
        signals["issue_resolution_rate"] = issue_resolution
        if avg_issue_days <= self.THRESHOLDS["ideal_issue_resolution_days"]:
            justifications.append(f"Fast issue resolution: avg {avg_issue_days:.1f} days.")
            score += self.WEIGHTS["issue_resolution_rate"] * issue_resolution
        # 5. Commit frequency
        commits_14d = repo_data.get("commits_14d", 0)
        commit_frequency = self._normalize(commits_14d, 50, 0)
        signals["commit_frequency"] = commit_frequency
        if commits_14d >= self.THRESHOLDS["min_commits_for_frequency"]:
            justifications.append(f"Sustained commit activity: {commits_14d} commits in last 14d.")
            score += self.WEIGHTS["commit_frequency"] * commit_frequency
        # 6. Novelty signal (Qualitative or NLP-driven) ---
        novelty = repo_data.get("novelty_signal", 0.0)
        signals["novelty_signal"] = novelty
        if novelty > 0.5:
            justifications.append("Novelty: project shows unique or emerging technology.")
            score += self.WEIGHTS["novelty_signal"] * novelty
        # 7. Founder signal (External Data or Heuristics) ---
        founder = repo_data.get("founder_signal", 0.0)
        signals["founder_signal"] = founder
        if founder > 0.5:
            justifications.append("Strong founder signal.")
            score += self.WEIGHTS["founder_signal"] * founder
        # 8. Documentation quality
        doc_quality = repo_data.get("documentation_quality", 0.0)
        signals["documentation_quality"] = doc_quality
        if doc_quality > 0.5:
            justifications.append("Good documentation quality.")
            score += self.WEIGHTS["documentation_quality"] * doc_quality
        # 9. Recent activity bonus
        last_commit = repo_data.get("last_commit_date")
        if last_commit:
            try:
                last_commit_dt = datetime.strptime(last_commit, "%Y-%m-%dT%H:%M:%SZ")
                days_since = (now - last_commit_dt).days
                if days_since <= self.THRESHOLDS["recent_activity_window_days"]:
                    score += self.WEIGHTS["recent_activity_bonus"]
                    justifications.append(f"Recent commit activity: last commit {days_since} days ago.")
            except Exception:
                pass
        # Clamp score to 0-1
        score = max(0.0, min(1.0, score))
        return {
            "name": repo_data.get("name"),
            "full_name": repo_data.get("full_name"),
            "url": repo_data.get("url"),
            "description": repo_data.get("description"),
            "score": round(score * 10, 2),
            "signals": signals,
            "justification": justifications,
            "metrics": {
                "stars": stars,
                "stars_gained_14d": stars_14d,
                "forks": forks,
                "forks_gained_14d": forks_14d,
                "commits_14d": commits_14d,
                "contributors_30d": contributors_30d,
                "avg_issue_resolution_days": avg_issue_days
            },
            "date_analyzed": now.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

    def score_repositories(self, repositories_data: List[Dict[str, Any]], historical_repo_data: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> List[Dict[str, Any]]:
        """
        Scores a list of repositories.
        Only returns repositories that meet a minimum threshold (e.g., score > 6).
        """
        # Score all repositories and return the top 5 with justifications
        scored = [self.score_repository(r, None) for r in repositories_data]
        scored = sorted(scored, key=lambda r: r["score"], reverse=True)
        return scored[:5]
