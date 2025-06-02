"""
HTML dashboard generator for GitHub repository analysis.
"""
import os
import datetime
import json
import shutil
from typing import Any, Dict, List, Optional, Tuple

import jinja2

from ..utils import Config, setup_logger, sanitize_filename


class HtmlGenerator:
    """
    Generates HTML dashboard for GitHub repository analysis.
    """
    
    def __init__(self):
        """
        Initialize the HTML generator with configuration.
        """
        self.config = Config()
        self.logger = setup_logger(self.__class__.__name__)
        
        # Set up Jinja2 template environment
        self.template_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "templates",
            "html"
        )
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Set up output directory
        self.docs_dir = self.config.get(
            'output.docs_directory',
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                       "docs")
        )
        
    def generate_dashboard(
        self,
        repositories: List[Dict[str, Any]],
        trends: Dict[str, Any],
        report_date: Optional[datetime.datetime] = None
    ) -> str:
        """
        Generate an HTML dashboard for the analyzed repositories.
        
        Args:
            repositories: List of repositories with scores and insights
            trends: Trend analysis results
            report_date: Date for the report (defaults to today)
            
        Returns:
            Path to the generated dashboard
        """
        if report_date is None:
            report_date = datetime.datetime.now()
            
        date_str = report_date.strftime('%Y-%m-%d')
        
        self.logger.info(f"Generating HTML dashboard for {date_str}")
        
        # Prepare dashboard data
        dashboard_data = self._prepare_dashboard_data(repositories, trends, report_date)
        
        # Serialize data for JavaScript
        dashboard_data['json_data'] = json.dumps({
            'repositories': dashboard_data['repositories'],
            'trends': dashboard_data['trends']
        })
        
        # Load and render the template
        try:
            template = self.env.get_template("dashboard.html")
            dashboard_content = template.render(**dashboard_data)
        except jinja2.exceptions.TemplateNotFound:
            self.logger.warning("Template not found. Creating default dashboard template.")
            self._create_default_template()
            try:
                template = self.env.get_template("dashboard.html")
                dashboard_content = template.render(**dashboard_data)
            except Exception as e:
                self.logger.error(f"Error rendering template after creation: {e}")
                return ""
        except Exception as e:
            self.logger.error(f"Error rendering template: {e}")
            return ""
            
        # Write the dashboard to file
        index_path = os.path.join(self.docs_dir, "index.html")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)
            
        # Create CSS and JS files if they don't exist
        self._ensure_assets_exist()
        
        self.logger.info(f"Dashboard saved to {index_path}")
        return index_path
        
    def _prepare_dashboard_data(
        self,
        repositories: List[Dict[str, Any]],
        trends: Dict[str, Any],
        report_date: datetime.datetime
    ) -> Dict[str, Any]:
        """
        Prepare data for the dashboard template.
        
        Args:
            repositories: List of repositories with scores and insights
            trends: Trend analysis results
            report_date: Date for the report
            
        Returns:
            Dictionary of data for the template
        """
        # Sort repositories by total score
        sorted_repos = sorted(repositories, key=lambda r: r.get('total_score', 0), reverse=True)
        
        # Format repositories for the dashboard
        dashboard_repos = []
        for repo in sorted_repos:
            # Extract repo data
            repo_data = repo.copy()
            
            # Basic repository info
            repo_info = {
                'full_name': repo.get('repository', repo.get('full_name', 'Unknown')),
                'name': repo.get('full_name', 'Unknown').split('/')[-1] if repo.get('full_name') else 'Unknown',
                'owner': repo.get('full_name', '/').split('/')[0] if repo.get('full_name') else 'Unknown',
                'url': repo.get('html_url', f"https://github.com/{repo.get('full_name', '')}"),
                'description': repo.get('description', 'No description available'),
                'language': repo.get('language', 'Unknown'),
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'issues': repo.get('open_issues_count', 0),
                'created_at': repo.get('created_at', ''),
                'updated_at': repo.get('updated_at', ''),
            }
            
            # Calculate repository age
            if repo_info['created_at']:
                try:
                    created_date = datetime.datetime.fromisoformat(repo_info['created_at'].replace('Z', '+00:00'))
                    age_days = (datetime.datetime.now().replace(tzinfo=None) - 
                              created_date.replace(tzinfo=None)).days
                    repo_info['age_days'] = age_days
                except (ValueError, TypeError):
                    repo_info['age_days'] = None
            else:
                repo_info['age_days'] = None
                
            # Score information
            score_info = {
                'total_score': repo.get('total_score', 0),
                'repo_score': repo.get('repository_score', {}).get('total', 0),
                'org_score': repo.get('organization_score', {}).get('total', 0),
                'community_score': repo.get('community_score', {}).get('total', 0),
                'confidence': repo.get('confidence_level', 'low'),
                'score_breakdown': {
                    'repository': repo.get('repository_score', {}).get('breakdown', {}),
                    'organization': repo.get('organization_score', {}).get('breakdown', {}),
                    'community': repo.get('community_score', {}).get('breakdown', {}),
                }
            }
            
            # Insights
            insights = repo.get('insights', {})
            insights_info = {
                'summary': insights.get('summary', ''),
                'strengths': insights.get('strengths', []),
                'weaknesses': insights.get('weaknesses', []),
                'product': insights.get('potential_product', ''),
                'community': insights.get('community_engagement', ''),
                'team': insights.get('team_insights', ''),
                'growth': insights.get('growth_trajectory', ''),
            }
            
            # Combine all data
            dashboard_repo = {**repo_info, **score_info, **{'insights': insights_info}}
            dashboard_repos.append(dashboard_repo)
            
        # Prepare the full dashboard data
        return {
            'title': "GitHub Early-Stage Startup Signals Dashboard",
            'date': report_date.strftime('%Y-%m-%d'),
            'repositories': dashboard_repos,
            'repository_count': len(repositories),
            'trends': trends,
            'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'api_url': f'api/{report_date.strftime("%Y-%m-%d")}.json',
            'latest_api_url': 'api/latest.json',
        }
        
    def _ensure_assets_exist(self):
        """
        Ensure CSS and JS assets exist in the docs directory.
        """
        # CSS directory
        css_dir = os.path.join(self.docs_dir, "assets", "css")
        os.makedirs(css_dir, exist_ok=True)
        
        # JS directory
        js_dir = os.path.join(self.docs_dir, "assets", "js")
        os.makedirs(js_dir, exist_ok=True)
        
        # Create CSS file if it doesn't exist
        css_file = os.path.join(css_dir, "style.css")
        if not os.path.exists(css_file):
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(self._get_default_css())
                
        # Create JS file if it doesn't exist
        js_file = os.path.join(js_dir, "dashboard.js")
        if not os.path.exists(js_file):
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(self._get_default_js())
                
    def _create_default_template(self):
        """
        Create a default HTML template if none exists.
        """
        # Ensure template directory exists
        os.makedirs(self.template_dir, exist_ok=True)
        
        # Create the default template
        template_path = os.path.join(self.template_dir, "dashboard.html")
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(self._get_default_html_template())
            
        self.logger.info(f"Created default dashboard template at {template_path}")
        
    def _get_default_html_template(self) -> str:
        """
        Get the default HTML template content.
        
        Returns:
            String containing the HTML template
        """
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <header>
        <div class="container">
            <h1><i class="fab fa-github"></i> {{ title }}</h1>
            <p class="subtitle">Discovering tomorrow's startups today</p>
            <div class="report-meta">
                <span class="date">Report Date: {{ date }}</span>
                <span class="repo-count">{{ repository_count }} repositories analyzed</span>
            </div>
        </div>
    </header>
    
    <div class="container">
        <div class="dashboard-controls">
            <div class="search-filter">
                <input type="text" id="repo-search" placeholder="Search repositories...">
                <select id="language-filter">
                    <option value="">All Languages</option>
                </select>
                <select id="confidence-filter">
                    <option value="">All Confidence Levels</option>
                    <option value="high">High Confidence</option>
                    <option value="medium">Medium Confidence</option>
                    <option value="low">Low Confidence</option>
                </select>
                <button id="reset-filters" class="btn">Reset Filters</button>
            </div>
        </div>
        
        <div class="dashboard-overview">
            <div class="overview-card">
                <h3>Repository Score Distribution</h3>
                <canvas id="score-distribution-chart"></canvas>
            </div>
            <div class="overview-card">
                <h3>Language Distribution</h3>
                <canvas id="language-chart"></canvas>
            </div>
            <div class="overview-card">
                <h3>Confidence Levels</h3>
                <canvas id="confidence-chart"></canvas>
            </div>
        </div>
        
        <div class="dashboard-main">
            <h2>Top Startup Repositories</h2>
            <table id="repositories-table">
                <thead>
                    <tr>
                        <th data-sort="name">Repository <i class="fas fa-sort"></i></th>
                        <th data-sort="total_score">Score <i class="fas fa-sort"></i></th>
                        <th data-sort="confidence">Confidence <i class="fas fa-sort"></i></th>
                        <th data-sort="language">Language <i class="fas fa-sort"></i></th>
                        <th data-sort="stars">Stars <i class="fas fa-sort"></i></th>
                        <th data-sort="age_days">Age (Days) <i class="fas fa-sort"></i></th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody id="repo-table-body">
                    <!-- Repository rows will be inserted here by JavaScript -->
                </tbody>
            </table>
        </div>
        
        <!-- Repository details modal -->
        <div id="repo-modal" class="modal">
            <div class="modal-content">
                <span class="close">&times;</span>
                <div id="repo-details-content"></div>
            </div>
        </div>
    </div>
    
    <footer>
        <div class="container">
            <p>Generated at {{ generated_at }} | <a href="{{ api_url }}">API</a> | GitHub Signals Platform</p>
        </div>
    </footer>
    
    <script>
        // Pass data to JavaScript
        const dashboardData = {{ json_data|safe }};
    </script>
    <script src="assets/js/dashboard.js"></script>
</body>
</html>
'''

    def _get_default_css(self) -> str:
        """
        Get the default CSS content.
        
        Returns:
            String containing the CSS
        """
        return '''/* Global styles */
:root {
    --primary-color: #0366d6;
    --secondary-color: #2ea44f;
    --text-color: #24292e;
    --light-bg: #f6f8fa;
    --border-color: #e1e4e8;
    --header-bg: #24292e;
    --header-text: white;
    --high-confidence: #2ea44f;
    --medium-confidence: #f6a821;
    --low-confidence: #dc3545;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: #ffffff;
}

.container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
}

/* Header */
header {
    background-color: var(--header-bg);
    color: var(--header-text);
    padding: 2rem 0;
    margin-bottom: 2rem;
}

header h1 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

header .subtitle {
    font-size: 1.2rem;
    opacity: 0.8;
    margin-bottom: 1rem;
}

.report-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    font-size: 0.9rem;
}

/* Dashboard controls */
.dashboard-controls {
    margin-bottom: 2rem;
    padding: 1rem;
    background-color: var(--light-bg);
    border-radius: 6px;
    border: 1px solid var(--border-color);
}

.search-filter {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
}

.search-filter input,
.search-filter select {
    padding: 8px 12px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-size: 0.9rem;
}

.search-filter input {
    flex-grow: 1;
    min-width: 200px;
}

.btn {
    padding: 8px 16px;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
}

.btn:hover {
    opacity: 0.9;
}

/* Dashboard overview cards */
.dashboard-overview {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 2rem;
}

.overview-card {
    background-color: white;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.overview-card h3 {
    margin-bottom: 1rem;
    font-size: 1.1rem;
    color: var(--text-color);
}

/* Repositories table */
.dashboard-main {
    margin-bottom: 3rem;
}

.dashboard-main h2 {
    margin-bottom: 1rem;
    font-size: 1.5rem;
}

#repositories-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}

#repositories-table th,
#repositories-table td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}

#repositories-table th {
    background-color: var(--light-bg);
    position: sticky;
    top: 0;
    cursor: pointer;
}

#repositories-table th:hover {
    background-color: #e1e4e8;
}

#repositories-table tbody tr:hover {
    background-color: var(--light-bg);
}

.score-cell {
    font-weight: 600;
}

.confidence-badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
    color: white;
}

.confidence-high {
    background-color: var(--high-confidence);
}

.confidence-medium {
    background-color: var(--medium-confidence);
}

.confidence-low {
    background-color: var(--low-confidence);
}

.details-btn {
    padding: 5px 10px;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
}

.details-btn:hover {
    opacity: 0.9;
}

/* Modal */
.modal {
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
    background-color: white;
    margin: 5% auto;
    padding: 20px;
    border-radius: 6px;
    width: 80%;
    max-width: 900px;
    max-height: 85vh;
    overflow-y: auto;
    position: relative;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.close {
    position: absolute;
    top: 15px;
    right: 20px;
    font-size: 28px;
    font-weight: bold;
    cursor: pointer;
}

.repo-details-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-color);
}

.repo-details-header h2 {
    margin-bottom: 0.5rem;
}

.repo-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 1rem;
}

.repo-meta-item {
    display: flex;
    align-items: center;
    gap: 5px;
}

.repo-score-section {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 1.5rem;
}

.score-card {
    flex: 1;
    min-width: 150px;
    padding: 1rem;
    background-color: var(--light-bg);
    border-radius: 6px;
}

.score-value {
    font-size: 1.8rem;
    font-weight: 600;
    margin-bottom: 5px;
}

.insights-section {
    margin-bottom: 1.5rem;
}

.insights-section h3 {
    margin-bottom: 0.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-color);
}

.insights-lists {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin: 1rem 0;
}

@media (max-width: 768px) {
    .insights-lists {
        grid-template-columns: 1fr;
    }
    
    .repo-score-section {
        flex-direction: column;
    }
    
    .search-filter {
        flex-direction: column;
        align-items: stretch;
    }
    
    .search-filter input,
    .search-filter select,
    .search-filter button {
        width: 100%;
    }
}

/* Footer */
footer {
    background-color: var(--light-bg);
    padding: 1rem 0;
    border-top: 1px solid var(--border-color);
    font-size: 0.9rem;
    text-align: center;
}

footer a {
    color: var(--primary-color);
    text-decoration: none;
}

footer a:hover {
    text-decoration: underline;
}
'''

    def _get_default_js(self) -> str:
        """
        Get the default JavaScript content.
        
        Returns:
            String containing the JavaScript
        """
        return '''// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Extract repositories data
    const repositories = dashboardData.repositories;
    const trends = dashboardData.trends;
    
    // Initialize filters
    initializeFilters(repositories);
    
    // Initialize charts
    initializeCharts(repositories, trends);
    
    // Populate the repositories table
    populateRepositoriesTable(repositories);
    
    // Set up sorting functionality
    setupTableSorting();
    
    // Set up modal functionality
    setupModal();
    
    // Set up filter functionality
    setupFilters();
});

// Initialize filter dropdowns
function initializeFilters(repositories) {
    // Populate language filter
    const languages = new Set();
    repositories.forEach(repo => {
        if (repo.language) {
            languages.add(repo.language);
        }
    });
    
    const languageFilter = document.getElementById('language-filter');
    [...languages].sort().forEach(language => {
        const option = document.createElement('option');
        option.value = language;
        option.textContent = language;
        languageFilter.appendChild(option);
    });
}

// Initialize charts with Chart.js
function initializeCharts(repositories, trends) {
    // Score distribution chart
    const scoreData = calculateScoreDistribution(repositories);
    new Chart(document.getElementById('score-distribution-chart').getContext('2d'), {
        type: 'bar',
        data: {
            labels: scoreData.labels,
            datasets: [{
                label: 'Repositories',
                data: scoreData.data,
                backgroundColor: 'rgba(3, 102, 214, 0.7)',
                borderColor: 'rgba(3, 102, 214, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Repositories'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Score Range'
                    }
                }
            }
        }
    });
    
    // Language chart
    const languageData = calculateLanguageDistribution(repositories);
    new Chart(document.getElementById('language-chart').getContext('2d'), {
        type: 'pie',
        data: {
            labels: languageData.labels,
            datasets: [{
                data: languageData.data,
                backgroundColor: [
                    '#0366d6', '#2ea44f', '#6f42c1', '#e36209', '#d73a49',
                    '#b08800', '#005cc5', '#22863a', '#5a32a3', '#cb2431'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                }
            }
        }
    });
    
    // Confidence level chart
    const confidenceData = calculateConfidenceLevels(repositories);
    new Chart(document.getElementById('confidence-chart').getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: confidenceData.labels,
            datasets: [{
                data: confidenceData.data,
                backgroundColor: [
                    '#2ea44f', // high
                    '#f6a821', // medium
                    '#dc3545'  // low
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                }
            }
        }
    });
}

// Calculate score distribution for chart
function calculateScoreDistribution(repositories) {
    const scoreRanges = {
        '0-10': 0,
        '11-20': 0,
        '21-30': 0,
        '31-40': 0,
        '41-50': 0
    };
    
    repositories.forEach(repo => {
        const score = repo.total_score;
        if (score <= 10) scoreRanges['0-10']++;
        else if (score <= 20) scoreRanges['11-20']++;
        else if (score <= 30) scoreRanges['21-30']++;
        else if (score <= 40) scoreRanges['31-40']++;
        else scoreRanges['41-50']++;
    });
    
    return {
        labels: Object.keys(scoreRanges),
        data: Object.values(scoreRanges)
    };
}

// Calculate language distribution for chart
function calculateLanguageDistribution(repositories) {
    const languages = {};
    const otherThreshold = repositories.length * 0.03; // 3% threshold for "Other"
    
    repositories.forEach(repo => {
        const lang = repo.language || 'Unknown';
        languages[lang] = (languages[lang] || 0) + 1;
    });
    
    // Convert to arrays and sort by count
    let sortedLangs = Object.entries(languages)
        .sort((a, b) => b[1] - a[1]);
        
    // Separate top languages and group small ones as "Other"
    const topLangs = [];
    let otherCount = 0;
    
    sortedLangs.forEach(([lang, count]) => {
        if (count >= otherThreshold && topLangs.length < 9) {
            topLangs.push([lang, count]);
        } else {
            otherCount += count;
        }
    });
    
    // Add "Other" if needed
    if (otherCount > 0) {
        topLangs.push(['Other', otherCount]);
    }
    
    return {
        labels: topLangs.map(l => l[0]),
        data: topLangs.map(l => l[1])
    };
}

// Calculate confidence level distribution
function calculateConfidenceLevels(repositories) {
    const levels = {
        'High': 0,
        'Medium': 0,
        'Low': 0
    };
    
    repositories.forEach(repo => {
        const confidence = repo.confidence.charAt(0).toUpperCase() + repo.confidence.slice(1);
        levels[confidence]++;
    });
    
    return {
        labels: Object.keys(levels),
        data: Object.values(levels)
    };
}

// Populate the repositories table
function populateRepositoriesTable(repositories) {
    const tableBody = document.getElementById('repo-table-body');
    tableBody.innerHTML = '';
    
    repositories.forEach(repo => {
        const row = document.createElement('tr');
        row.dataset.repo = repo.full_name;
        
        // Repository name with link
        row.innerHTML = `
            <td><a href="${repo.url}" target="_blank">${repo.full_name}</a></td>
            <td class="score-cell">${repo.total_score.toFixed(1)}</td>
            <td><span class="confidence-badge confidence-${repo.confidence}">${repo.confidence.charAt(0).toUpperCase() + repo.confidence.slice(1)}</span></td>
            <td>${repo.language || 'Unknown'}</td>
            <td>${repo.stars}</td>
            <td>${repo.age_days !== null ? repo.age_days : 'Unknown'}</td>
            <td><button class="details-btn" data-repo="${repo.full_name}">Details</button></td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Set up table sorting functionality
function setupTableSorting() {
    const table = document.getElementById('repositories-table');
    const headers = table.querySelectorAll('th[data-sort]');
    let currentSortColumn = 'total_score';
    let currentSortDirection = 'desc';
    
    headers.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.sort;
            
            // Toggle direction if clicking the same column
            if (column === currentSortColumn) {
                currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                currentSortColumn = column;
                currentSortDirection = 'desc'; // Default to descending on new column
            }
            
            // Update UI to show sort direction
            headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
            header.classList.add(`sort-${currentSortDirection}`);
            
            // Sort the table
            sortTable(column, currentSortDirection);
        });
    });
    
    // Initial sort by score
    sortTable('total_score', 'desc');
}

// Sort the repositories table
function sortTable(column, direction) {
    const tableBody = document.getElementById('repo-table-body');
    const rows = Array.from(tableBody.querySelectorAll('tr'));
    
    const sortedRows = rows.sort((a, b) => {
        let aValue, bValue;
        
        // Get values based on column
        if (column === 'name') {
            aValue = a.dataset.repo.toLowerCase();
            bValue = b.dataset.repo.toLowerCase();
        } else if (column === 'confidence') {
            // Convert confidence to numeric value for sorting
            const confidenceValues = { 'high': 3, 'medium': 2, 'low': 1 };
            aValue = confidenceValues[a.querySelector('.confidence-badge').textContent.toLowerCase()];
            bValue = confidenceValues[b.querySelector('.confidence-badge').textContent.toLowerCase()];
        } else {
            // For numeric columns
            aValue = parseFloat(a.cells[getColumnIndex(column)].textContent) || 0;
            bValue = parseFloat(b.cells[getColumnIndex(column)].textContent) || 0;
        }
        
        // Compare based on direction
        if (direction === 'asc') {
            return aValue > bValue ? 1 : -1;
        } else {
            return aValue < bValue ? 1 : -1;
        }
    });
    
    // Update the table
    sortedRows.forEach(row => tableBody.appendChild(row));
}

// Get column index by data attribute
function getColumnIndex(column) {
    const columns = {
        'name': 0,
        'total_score': 1,
        'confidence': 2,
        'language': 3,
        'stars': 4,
        'age_days': 5
    };
    
    return columns[column] || 0;
}

// Set up modal functionality
function setupModal() {
    const modal = document.getElementById('repo-modal');
    const closeBtn = modal.querySelector('.close');
    
    // Close modal when clicking X
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Show modal when clicking details button
    document.addEventListener('click', (event) => {
        if (event.target.classList.contains('details-btn')) {
            const repoName = event.target.dataset.repo;
            showRepoDetails(repoName);
        }
    });
}

// Show repository details in modal
function showRepoDetails(repoName) {
    const repo = dashboardData.repositories.find(r => r.full_name === repoName);
    if (!repo) return;
    
    const modal = document.getElementById('repo-modal');
    const content = document.getElementById('repo-details-content');
    
    // Create modal content
    content.innerHTML = `
        <div class="repo-details-header">
            <div>
                <h2><a href="${repo.url}" target="_blank">${repo.full_name}</a></h2>
                <p>${repo.description || 'No description available'}</p>
            </div>
            <div>
                <span class="confidence-badge confidence-${repo.confidence}">${repo.confidence.charAt(0).toUpperCase() + repo.confidence.slice(1)} Confidence</span>
            </div>
        </div>
        
        <div class="repo-meta">
            <div class="repo-meta-item">
                <i class="fas fa-code"></i> ${repo.language || 'Unknown'}
            </div>
            <div class="repo-meta-item">
                <i class="fas fa-star"></i> ${repo.stars} stars
            </div>
            <div class="repo-meta-item">
                <i class="fas fa-code-branch"></i> ${repo.forks} forks
            </div>
            <div class="repo-meta-item">
                <i class="fas fa-exclamation-circle"></i> ${repo.issues} issues
            </div>
            <div class="repo-meta-item">
                <i class="fas fa-calendar"></i> Created: ${formatDate(repo.created_at)}
            </div>
            ${repo.age_days !== null ? `
            <div class="repo-meta-item">
                <i class="fas fa-clock"></i> ${repo.age_days} days old
            </div>` : ''}
        </div>
        
        <div class="repo-score-section">
            <div class="score-card">
                <h3>Total Score</h3>
                <div class="score-value">${repo.total_score.toFixed(1)}/50</div>
            </div>
            <div class="score-card">
                <h3>Repository</h3>
                <div class="score-value">${repo.repo_score.toFixed(1)}/20</div>
            </div>
            <div class="score-card">
                <h3>Organization</h3>
                <div class="score-value">${repo.org_score.toFixed(1)}/15</div>
            </div>
            <div class="score-card">
                <h3>Community</h3>
                <div class="score-value">${repo.community_score.toFixed(1)}/15</div>
            </div>
        </div>
        
        <div class="insights-section">
            <h3>Summary</h3>
            <p>${repo.insights.summary}</p>
            
            <h3>Potential Product</h3>
            <p>${repo.insights.product}</p>
            
            <div class="insights-lists">
                <div>
                    <h4>Strengths</h4>
                    <ul>
                        ${repo.insights.strengths.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                </div>
                <div>
                    <h4>Areas for Improvement</h4>
                    <ul>
                        ${repo.insights.weaknesses.map(w => `<li>${w}</li>`).join('')}
                    </ul>
                </div>
            </div>
            
            <h3>Team Insights</h3>
            <p>${repo.insights.team}</p>
            
            <h3>Community Engagement</h3>
            <p>${repo.insights.community}</p>
            
            <h3>Growth Trajectory</h3>
            <p>${repo.insights.growth}</p>
        </div>
    `;
    
    // Show the modal
    modal.style.display = 'block';
}

// Format ISO date to readable format
function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    
    try {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        }).format(date);
    } catch (e) {
        return dateString;
    }
}

// Set up filter functionality
function setupFilters() {
    const searchInput = document.getElementById('repo-search');
    const languageFilter = document.getElementById('language-filter');
    const confidenceFilter = document.getElementById('confidence-filter');
    const resetBtn = document.getElementById('reset-filters');
    
    // Function to apply filters
    function applyFilters() {
        const searchTerm = searchInput.value.toLowerCase();
        const language = languageFilter.value.toLowerCase();
        const confidence = confidenceFilter.value.toLowerCase();
        
        const allRepos = dashboardData.repositories;
        const filteredRepos = allRepos.filter(repo => {
            // Search term filter
            const matchesSearch = !searchTerm || 
                repo.full_name.toLowerCase().includes(searchTerm) ||
                (repo.description && repo.description.toLowerCase().includes(searchTerm));
            
            // Language filter
            const matchesLanguage = !language || 
                (repo.language && repo.language.toLowerCase() === language);
            
            // Confidence filter
            const matchesConfidence = !confidence || 
                repo.confidence.toLowerCase() === confidence;
            
            return matchesSearch && matchesLanguage && matchesConfidence;
        });
        
        // Update table with filtered repositories
        populateRepositoriesTable(filteredRepos);
    }
    
    // Add event listeners
    searchInput.addEventListener('input', applyFilters);
    languageFilter.addEventListener('change', applyFilters);
    confidenceFilter.addEventListener('change', applyFilters);
    
    // Reset filters
    resetBtn.addEventListener('click', () => {
        searchInput.value = '';
        languageFilter.value = '';
        confidenceFilter.value = '';
        populateRepositoriesTable(dashboardData.repositories);
    });
}
'''
