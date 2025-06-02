"""
Insights generator for scored GitHub repositories.
"""
import re
import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from ..utils import Config, setup_logger


class InsightsGenerator:
    """
    Generates insights and explanations for GitHub repositories.
    """
    
    def __init__(self):
        """
        Initialize the insights generator with configuration.
        """
        self.config = Config()
        self.logger = setup_logger(self.__class__.__name__)
        
    def generate_insights(self, repo_data: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate insights for a repository based on its data and scores.
        
        Args:
            repo_data: Repository data from GitHubCollector
            scores: Scoring data from StartupScorer
            
        Returns:
            Dictionary with insights
        """
        insights = {}
        
        # Generate a summary of why this repository is interesting
        insights['summary'] = self._generate_summary(repo_data, scores)
        
        # Generate strengths and weaknesses
        insights['strengths'] = self._identify_strengths(repo_data, scores)
        insights['weaknesses'] = self._identify_weaknesses(repo_data, scores)
        
        # Generate potential use case or product
        insights['potential_product'] = self._identify_potential_product(repo_data)
        
        # Generate community engagement insights
        insights['community_engagement'] = self._analyze_community_engagement(repo_data, scores)
        
        # Generate team insights
        insights['team_insights'] = self._analyze_team(repo_data, scores)
        
        # Generate growth trajectory
        insights['growth_trajectory'] = self._analyze_growth(repo_data, scores)
        
        return insights
        
    def _generate_summary(self, repo_data: Dict[str, Any], scores: Dict[str, Any]) -> str:
        """
        Generate a summary explanation of why this repository is interesting.
        
        Args:
            repo_data: Repository data
            scores: Scoring data
            
        Returns:
            Summary string
        """
        total_score = scores.get('total_score', 0)
        confidence = scores.get('confidence_level', 'low')
        repo_name = repo_data.get('name', '')
        description = repo_data.get('description', 'No description available')
        language = repo_data.get('language', 'Unknown')
        stars = repo_data.get('stargazers_count', 0)
        
        # Format the creation date
        created_at = repo_data.get('created_at', '')
        creation_date_str = "recently"
        if created_at:
            try:
                created_date = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                creation_date_str = created_date.strftime('%B %Y')
            except (ValueError, TypeError):
                pass
                
        # Check if it's an organization repo
        is_org = repo_data.get('owner', {}).get('type') == 'Organization'
        org_desc = ""
        if is_org and repo_data.get('organization'):
            org = repo_data.get('organization', {})
            org_name = org.get('name') or org.get('login', 'an organization')
            team_size = org.get('team_size', 0)
            
            if team_size > 0:
                org_desc = f" developed by {org_name}, a team of {team_size} developers,"
            else:
                org_desc = f" developed by {org_name},"
        
        # Generate a summary based on confidence level
        if confidence == 'high':
            return (
                f"{repo_name} is a highly promising {language} project{org_desc} created in {creation_date_str}. "
                f"With {stars} stars, it demonstrates strong startup potential (score: {total_score:.1f}/50). "
                f"{description} "
                f"This repository shows excellent signals across repository quality, "
                f"team composition, and community engagement."
            )
        elif confidence == 'medium':
            return (
                f"{repo_name} is a noteworthy {language} project{org_desc} created in {creation_date_str}. "
                f"With {stars} stars, it shows moderate startup potential (score: {total_score:.1f}/50). "
                f"{description} "
                f"This repository has several positive signals but could improve in some areas."
            )
        else:
            return (
                f"{repo_name} is an emerging {language} project{org_desc} created in {creation_date_str}. "
                f"With {stars} stars, it shows some startup potential (score: {total_score:.1f}/50). "
                f"{description} "
                f"While this repository has potential, it needs further development to demonstrate "
                f"strong startup signals."
            )
            
    def _identify_strengths(self, repo_data: Dict[str, Any], scores: Dict[str, Any]) -> List[str]:
        """
        Identify the repository's strengths based on its scores.
        
        Args:
            repo_data: Repository data
            scores: Scoring data
            
        Returns:
            List of strength strings
        """
        strengths = []
        
        # Repository signals
        repo_scores = scores.get('repository_score', {}).get('breakdown', {})
        if repo_scores.get('recent_creation', 0) > 0:
            strengths.append("Recently created repository (less than 90 days old)")
            
        if repo_scores.get('professional_language', 0) > 0:
            strengths.append(f"Uses industry-standard language: {repo_data.get('language')}")
            
        if repo_scores.get('ci_cd_setup', 0) > 0:
            strengths.append("Professional development setup with CI/CD integration")
            
        if repo_scores.get('quality_documentation', 0) > 0:
            strengths.append("Well-documented with comprehensive README")
            
        if repo_scores.get('active_development', 0) > 0:
            commits = repo_data.get('commit_activity', {}).get('weekly_commits', 0)
            strengths.append(f"Active development with {commits} commits in the last week")
            
        if repo_scores.get('external_website', 0) > 0:
            strengths.append("Has dedicated external website")
            
        if repo_scores.get('startup_keywords', 0) > 0:
            strengths.append("Description contains startup-related terminology")
            
        if repo_scores.get('y_combinator_mentions', 0) > 0:
            strengths.append("Associated with Y Combinator")
            
        if repo_scores.get('tests_present', 0) > 0:
            strengths.append("Includes testing infrastructure")
            
        # Organization signals
        org_scores = scores.get('organization_score', {}).get('breakdown', {})
        if org_scores.get('recent_creation', 0) > 0:
            strengths.append("Recently created organization")
            
        if org_scores.get('team_size', 0) > 0:
            org_data = repo_data.get('organization', {})
            team_size = org_data.get('team_size', 0)
            strengths.append(f"Optimal team size ({team_size} members)")
            
        if org_scores.get('multiple_repos', 0) > 0:
            strengths.append("Organization has multiple repositories")
            
        if org_scores.get('professional_profile', 0) > 0:
            strengths.append("Professional organization profile")
            
        if org_scores.get('organization_website', 0) > 0:
            strengths.append("Organization has dedicated website")
            
        if org_scores.get('hiring_indicators', 0) > 0:
            strengths.append("Organization is actively hiring")
            
        # Community signals
        community_scores = scores.get('community_score', {}).get('breakdown', {})
        if community_scores.get('hacker_news_discussion', 0) > 0:
            strengths.append("Generated discussion on Hacker News")
            
        if community_scores.get('star_growth', 0) > 0:
            strengths.append("Strong star growth trajectory")
            
        if community_scores.get('external_contributors', 0) > 0:
            contributors = repo_data.get('contributors', {})
            external = contributors.get('external_count', 0)
            strengths.append(f"Attracted {external} external contributors")
            
        if community_scores.get('issue_engagement', 0) > 0:
            strengths.append("Active issue discussions")
            
        if community_scores.get('fork_activity', 0) > 0:
            strengths.append(f"Strong fork activity ({repo_data.get('forks_count', 0)} forks)")
            
        if community_scores.get('social_mentions', 0) > 0:
            strengths.append("Mentioned on social platforms")
            
        return strengths
        
    def _identify_weaknesses(self, repo_data: Dict[str, Any], scores: Dict[str, Any]) -> List[str]:
        """
        Identify the repository's weaknesses based on its scores.
        
        Args:
            repo_data: Repository data
            scores: Scoring data
            
        Returns:
            List of weakness strings
        """
        weaknesses = []
        
        # Repository signals
        repo_scores = scores.get('repository_score', {}).get('breakdown', {})
        if repo_scores.get('recent_creation', 0) == 0:
            weaknesses.append("Repository is more than 90 days old")
            
        if repo_scores.get('professional_language', 0) == 0:
            weaknesses.append(f"Uses less common language: {repo_data.get('language') or 'Unknown'}")
            
        if repo_scores.get('ci_cd_setup', 0) == 0:
            weaknesses.append("Lacks CI/CD integration")
            
        if repo_scores.get('quality_documentation', 0) == 0:
            weaknesses.append("Documentation needs improvement")
            
        if repo_scores.get('active_development', 0) == 0:
            weaknesses.append("Limited recent development activity")
            
        if repo_scores.get('external_website', 0) == 0:
            weaknesses.append("No external website")
            
        if repo_scores.get('startup_keywords', 0) == 0:
            weaknesses.append("Description lacks startup-related terminology")
            
        if repo_scores.get('tests_present', 0) == 0:
            weaknesses.append("Missing testing infrastructure")
            
        # Organization signals
        if repo_data.get('owner', {}).get('type') != 'Organization':
            weaknesses.append("Individual repository (not organization-backed)")
        else:
            org_scores = scores.get('organization_score', {}).get('breakdown', {})
            
            if org_scores.get('recent_creation', 0) == 0:
                weaknesses.append("Organization is not recently created")
                
            if org_scores.get('team_size', 0) == 0:
                org_data = repo_data.get('organization', {})
                team_size = org_data.get('team_size', 0)
                if team_size == 0:
                    weaknesses.append("Team size information unavailable")
                elif team_size == 1:
                    weaknesses.append("Single-member organization")
                else:
                    weaknesses.append(f"Large team size ({team_size} members)")
                    
            if org_scores.get('multiple_repos', 0) == 0:
                weaknesses.append("Organization has only one repository")
                
            if org_scores.get('professional_profile', 0) == 0:
                weaknesses.append("Incomplete organization profile")
                
            if org_scores.get('organization_website', 0) == 0:
                weaknesses.append("No organization website")
                
            if org_scores.get('hiring_indicators', 0) == 0:
                weaknesses.append("No hiring indicators")
                
        # Community signals
        community_scores = scores.get('community_score', {}).get('breakdown', {})
        
        if community_scores.get('hacker_news_discussion', 0) == 0:
            weaknesses.append("No Hacker News discussion")
            
        if community_scores.get('star_growth', 0) == 0:
            weaknesses.append("Limited star growth")
            
        if community_scores.get('external_contributors', 0) == 0:
            weaknesses.append("No external contributors")
            
        if community_scores.get('issue_engagement', 0) == 0:
            if repo_data.get('open_issues_count', 0) == 0:
                weaknesses.append("No open issues")
            else:
                weaknesses.append("Limited issue engagement")
                
        if community_scores.get('fork_activity', 0) == 0:
            weaknesses.append("Few or no forks")
            
        return weaknesses[:5]  # Limit to top 5 weaknesses
        
    def _identify_potential_product(self, repo_data: Dict[str, Any]) -> str:
        """
        Identify the potential product or service based on repository data.
        
        Args:
            repo_data: Repository data
            
        Returns:
            String describing potential product
        """
        description = repo_data.get('description', '')
        name = repo_data.get('name', '')
        topics = repo_data.get('topics', [])
        
        # Product-related keywords to look for
        product_keywords = {
            'api': 'API or backend service',
            'sdk': 'Software Development Kit',
            'library': 'Developer library or framework',
            'framework': 'Development framework',
            'app': 'Application',
            'mobile': 'Mobile application',
            'web': 'Web application',
            'saas': 'Software-as-a-Service',
            'platform': 'Platform',
            'tool': 'Developer tool',
            'analytics': 'Analytics solution',
            'ai': 'AI-powered solution',
            'ml': 'Machine learning solution',
            'bot': 'Automation or bot service',
            'chat': 'Messaging or chat application',
            'database': 'Database or data storage solution',
            'dashboard': 'Analytics dashboard',
            'monitoring': 'Monitoring tool',
            'payment': 'Payment processing solution',
            'ecommerce': 'E-commerce solution',
            'blockchain': 'Blockchain application',
            'crypto': 'Cryptocurrency solution',
            'auth': 'Authentication service',
            'security': 'Security tool',
            'devops': 'DevOps tool',
            'ci/cd': 'CI/CD solution',
            'cloud': 'Cloud infrastructure tool',
            'serverless': 'Serverless application',
            'iot': 'IoT platform',
            'data': 'Data processing tool',
            'visualization': 'Data visualization tool',
            'reporting': 'Reporting tool',
            'game': 'Game or gaming platform',
            'editor': 'Content editor',
            'cms': 'Content management system',
            'productivity': 'Productivity tool',
            'collaboration': 'Collaboration tool',
            'health': 'Healthcare solution',
            'fintech': 'Financial technology solution',
            'edtech': 'Educational technology',
            'hr': 'HR or recruitment tool'
        }
        
        # Check repository name and description for product keywords
        matched_keywords = []
        for keyword, product_type in product_keywords.items():
            if (
                keyword.lower() in name.lower() or 
                keyword.lower() in description.lower() or
                any(keyword.lower() in topic.lower() for topic in topics)
            ):
                matched_keywords.append(product_type)
                
        # If we have matches, use them to describe the potential product
        if matched_keywords:
            # Take the first 2 matches maximum
            primary_matches = matched_keywords[:2]
            return (
                f"Potential product: {' and '.join(primary_matches)}. "
                f"Based on repository description and topics."
            )
            
        # If no specific keywords matched, make a general assessment based on language
        language = repo_data.get('language', '')
        
        language_product_map = {
            'JavaScript': 'Web-based application or service',
            'TypeScript': 'Enterprise-ready web application',
            'Python': 'Data science, AI, or backend service',
            'Go': 'High-performance backend service or DevOps tool',
            'Rust': 'Systems-level application with high performance requirements',
            'Java': 'Enterprise application or Android mobile app',
            'Kotlin': 'Android application or backend service',
            'Swift': 'iOS application',
            'Ruby': 'Web application or developer tool',
            'PHP': 'Web application or content management system',
            'C#': '.NET application or Unity game',
            'C++': 'Desktop application or high-performance system'
        }
        
        if language in language_product_map:
            return (
                f"Potential product: {language_product_map[language]}. "
                f"Based on programming language ({language})."
            )
            
        # Fallback if no specific indicators
        if description:
            return f"Potential product: Solution addressing \"{description}\""
        else:
            return "Potential product: Unclear from available repository information"
            
    def _analyze_community_engagement(self, repo_data: Dict[str, Any], scores: Dict[str, Any]) -> str:
        """
        Analyze community engagement patterns.
        
        Args:
            repo_data: Repository data
            scores: Scoring data
            
        Returns:
            String describing community engagement
        """
        stars = repo_data.get('stargazers_count', 0)
        forks = repo_data.get('forks_count', 0)
        issues = repo_data.get('open_issues_count', 0)
        contributors = repo_data.get('contributors', {}).get('total_count', 0)
        external_contributors = repo_data.get('contributors', {}).get('external_count', 0)
        
        # Calculate fork to star ratio
        fork_ratio = (forks / stars) if stars > 0 else 0
        
        # Calculate contributor to star ratio
        contributor_ratio = (contributors / stars) if stars > 0 else 0
        
        # Interpret the engagement pattern
        if stars == 0:
            return "No community engagement detected yet."
            
        if fork_ratio >= 0.3:
            engagement = "High developer engagement: Many forks relative to stars indicates developers are actively building with this project."
        elif fork_ratio >= 0.1:
            engagement = "Moderate developer engagement: Good balance of forks to stars suggests practical developer interest."
        else:
            engagement = "Observer engagement: More stars than forks suggests people are watching but not yet building with this project."
            
        if contributor_ratio >= 0.05:
            contribution = "Strong open-source collaboration with multiple contributors relative to audience size."
        elif external_contributors >= 1:
            contribution = f"Growing external interest with {external_contributors} external contributors."
        else:
            contribution = "Primarily maintained by original creator(s) without external contributions yet."
            
        if issues >= 10:
            issues_insight = f"Active discussions with {issues} open issues showing community participation."
        elif issues > 0:
            issues_insight = f"Some community feedback with {issues} open issues."
        else:
            issues_insight = "No open issues, suggesting either perfect code or limited community feedback."
            
        return f"{engagement} {contribution} {issues_insight}"
        
    def _analyze_team(self, repo_data: Dict[str, Any], scores: Dict[str, Any]) -> str:
        """
        Analyze team composition and characteristics.
        
        Args:
            repo_data: Repository data
            scores: Scoring data
            
        Returns:
            String describing team insights
        """
        is_org = repo_data.get('owner', {}).get('type') == 'Organization'
        
        if not is_org:
            return "Individual developer project without organizational backing."
            
        org = repo_data.get('organization', {})
        org_name = org.get('name') or org.get('login', 'Unknown')
        team_size = org.get('team_size', 0)
        has_website = org.get('blog') or org.get('has_website', False)
        hiring = org.get('hiring_indicators', False)
        public_repos = org.get('public_repos', 1)
        created_at = org.get('created_at')
        
        # Calculate organization age
        org_age = "unknown age"
        if created_at:
            try:
                created_date = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_old = (datetime.datetime.now().replace(tzinfo=None) - 
                          created_date.replace(tzinfo=None)).days
                
                if days_old <= 90:
                    org_age = "very new (under 3 months old)"
                elif days_old <= 365:
                    org_age = "less than a year old"
                elif days_old <= 730:
                    org_age = "1-2 years old"
                else:
                    org_age = f"established ({days_old // 365} years old)"
            except (ValueError, TypeError):
                pass
                
        # Team size insight
        if team_size == 0:
            team_insight = "unknown team size"
        elif team_size == 1:
            team_insight = "solo founder"
        elif team_size <= 5:
            team_insight = f"small founding team of {team_size} members"
        elif team_size <= 15:
            team_insight = f"mid-sized team of {team_size} members"
        else:
            team_insight = f"larger team of {team_size} members"
            
        # Organization profile completeness
        profile_elements = [
            org.get('name') is not None,
            org.get('bio') is not None,
            org.get('email') is not None,
            org.get('location') is not None,
            has_website
        ]
        profile_completeness = sum(profile_elements)
        
        if profile_completeness >= 4:
            profile_insight = "complete professional profile"
        elif profile_completeness >= 2:
            profile_insight = "partially complete profile"
        else:
            profile_insight = "minimal profile information"
            
        # Additional insights
        insights = []
        if hiring:
            insights.append("actively hiring")
            
        if public_repos > 5:
            insights.append(f"maintaining {public_repos} public repositories")
        elif public_repos > 1:
            insights.append(f"has {public_repos} public repositories")
            
        if has_website:
            insights.append("maintains a dedicated website")
            
        insights_str = ""
        if insights:
            insights_str = f" The team is {', '.join(insights)}."
            
        return f"{org_name} is a {org_age} organization with a {team_insight} and {profile_insight}.{insights_str}"
        
    def _analyze_growth(self, repo_data: Dict[str, Any], scores: Dict[str, Any]) -> str:
        """
        Analyze growth trajectory and potential.
        
        Args:
            repo_data: Repository data
            scores: Scoring data
            
        Returns:
            String describing growth trajectory
        """
        stars = repo_data.get('stargazers_count', 0)
        forks = repo_data.get('forks_count', 0)
        
        # Calculate repository age in days
        created_at = repo_data.get('created_at')
        age_days = 0
        if created_at:
            try:
                created_date = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                age_days = (datetime.datetime.now().replace(tzinfo=None) - 
                           created_date.replace(tzinfo=None)).days
            except (ValueError, TypeError):
                age_days = 30  # Default assumption
        else:
            age_days = 30  # Default assumption
            
        # Calculate growth metrics
        stars_per_day = stars / max(1, age_days)
        forks_per_day = forks / max(1, age_days)
        
        # Commit activity as a growth signal
        weekly_commits = repo_data.get('commit_activity', {}).get('weekly_commits', 0)
        unique_authors = repo_data.get('commit_activity', {}).get('unique_authors', 0)
        
        # Interpret growth trajectory
        if stars_per_day >= 5:
            star_growth = "Exceptional star growth"
            trajectory = "rapidly gaining visibility"
        elif stars_per_day >= 1:
            star_growth = "Strong star growth"
            trajectory = "steadily gaining visibility"
        elif stars_per_day >= 0.2:
            star_growth = "Moderate star growth"
            trajectory = "gradually building an audience"
        else:
            star_growth = "Early-stage visibility"
            trajectory = "in early discovery phase"
            
        # Development momentum
        if weekly_commits >= 20:
            dev_momentum = "very rapid development pace"
        elif weekly_commits >= 10:
            dev_momentum = "active development pace"
        elif weekly_commits >= 5:
            dev_momentum = "steady development pace"
        elif weekly_commits > 0:
            dev_momentum = "moderate development activity"
        else:
            dev_momentum = "currently inactive development"
            
        # Calculate projected growth
        if stars_per_day > 0:
            projected_30d = int(stars + (stars_per_day * 30))
            projected_90d = int(stars + (stars_per_day * 90))
            projection = f"Projected growth: {projected_30d} stars in 30 days, {projected_90d} stars in 90 days based on current trajectory."
        else:
            projection = "Insufficient data to project future growth."
            
        # Combine insights
        author_insight = ""
        if unique_authors > 1:
            author_insight = f" with {unique_authors} active contributors"
            
        growth_insight = (
            f"{star_growth} ({stars_per_day:.2f} stars/day) shows this project is {trajectory}. "
            f"The repository shows a {dev_momentum}{author_insight}. {projection}"
        )
        
        return growth_insight
