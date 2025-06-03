/**
 * Early Stage GitHub Signals Platform - Dashboard JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM elements
  const reposContainer = document.getElementById('repos-container');
  const filterLanguage = document.getElementById('filter-language');
  const filterCategory = document.getElementById('filter-category');
  const filterSort = document.getElementById('filter-sort');
  const searchInput = document.getElementById('search-input');
  const resetBtn = document.getElementById('reset-filters');
  
  // State
  let repositories = [];
  let filteredRepos = [];
  let filters = {
    language: 'all',
    category: 'all',
    sort: 'score',
    search: ''
  };
  
  // Fetch the data
  async function loadData() {
    try {
      const response = await fetch('./api/latest.json');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        repositories = await response.json();
        console.log('Fetched data:', repositories); // Debug log
        filteredRepos = [...repositories];
        
        // Populate language filter options
        const languages = ['all', ...new Set(repositories.map(repo => repo.language).filter(Boolean))];
        languages.forEach(lang => {
          const option = document.createElement('option');
          option.value = lang;
          option.textContent = lang === 'all' ? 'All Languages' : lang;
          filterLanguage.appendChild(option);
        });
        
        // Render repositories
        renderRepositories(filteredRepos);
        
        // Render charts for trends
        renderCharts(repositories.trends);
        
        // Render insights
        renderInsights(repositories.insights);
        
        // Remove loading state
        document.querySelector('.loading').style.display = 'none';
      } else {
        throw new Error("Response is not JSON");
      }
    } catch (error) {
      console.error('Error loading data:', error);
      reposContainer.innerHTML = `<div class="error">Failed to load repositories data. Please try again later.</div>`;
      document.querySelector('.loading').style.display = 'none';
    }
  }
  
  loadData();
  
  // Event listeners for filters
  if (filterLanguage) {
    filterLanguage.addEventListener('change', updateFilters);
  }

  if (filterCategory) {
    filterCategory.addEventListener('change', updateFilters);
  }

  if (filterSort) {
    filterSort.addEventListener('change', updateFilters);
  }

  if (searchInput) {
    searchInput.addEventListener('input', updateFilters);
  }

  if (resetBtn) {
    resetBtn.addEventListener('click', resetFilters);
  }
  
  /**
   * Update filters and re-render repositories
   */
  function updateFilters() {
    filters = {
      language: filterLanguage.value,
      category: filterCategory.value,
      sort: filterSort.value,
      search: searchInput.value.toLowerCase()
    };
    
    filterRepositories();
    renderRepositories(filteredRepos);
  }
  
  /**
   * Reset all filters to default
   */
  function resetFilters() {
    filterLanguage.value = 'all';
    filterCategory.value = 'all';
    filterSort.value = 'score';
    searchInput.value = '';
    
    filters = {
      language: 'all',
      category: 'all',
      sort: 'score',
      search: ''
    };
    
    filteredRepos = [...repositories];
    renderRepositories(filteredRepos);
  }
  
  /**
   * Filter repositories based on current filters
   */
  function filterRepositories() {
    filteredRepos = repositories.filter(repo => {
      // Language filter
      if (filters.language !== 'all' && repo.language !== filters.language) {
        return false;
      }
      
      // Category filter
      if (filters.category !== 'all') {
        switch (filters.category) {
          case 'high-score':
            if (repo.total_score < 35) return false;
            break;
          case 'new-creation':
            if (repo.days_since_creation > 60) return false;
            break;
          case 'fast-growing':
            if (repo.star_growth_rate < 1.5) return false;
            break;
          case 'hn-discussion':
            if (!repo.hackernews_discussions || repo.hackernews_discussions.length === 0) return false;
            break;
        }
      }
      
      // Search filter
      if (filters.search) {
        const searchFields = [
          repo.name,
          repo.description,
          repo.organization.name,
          repo.language
        ].filter(Boolean).join(' ').toLowerCase();
        
        if (!searchFields.includes(filters.search)) {
          return false;
        }
      }
      
      return true;
    });
    
    // Sort repositories
    switch (filters.sort) {
      case 'score':
        filteredRepos.sort((a, b) => b.total_score - a.total_score);
        break;
      case 'stars':
        filteredRepos.sort((a, b) => b.stars - a.stars);
        break;
      case 'newest':
        filteredRepos.sort((a, b) => a.days_since_creation - b.days_since_creation);
        break;
      case 'growth':
        filteredRepos.sort((a, b) => b.star_growth_rate - a.star_growth_rate);
        break;
    }
  }
  
  /**
   * Render repository cards
   * @param {Array} repos - Repositories to render
   */
  function renderRepositories(repos) {
    if (!reposContainer) return;
    
    if (repos.length === 0) {
      reposContainer.innerHTML = '<div class="no-results">No repositories match the selected filters</div>';
      return;
    }
    
    reposContainer.innerHTML = repos.map(repo => {
      // Score bars (out of 10)
      const repoScore = Math.round(repo.scores.repository * 10 / 20); // Repository max score is 20
      const orgScore = Math.round(repo.scores.organization * 10 / 15); // Organization max score is 15
      const communityScore = Math.round(repo.scores.community * 10 / 15); // Community max score is 15
      
      // Create score bars HTML
      const createScoreBars = (score) => {
        let bars = '';
        for (let i = 0; i < 10; i++) {
          bars += `<div class="score-bar ${i < score ? 'filled' : 'empty'}"></div>`;
        }
        return bars;
      };
      
      // Tags
      const tags = [];
      if (repo.days_since_creation < 60) tags.push('New');
      if (repo.star_growth_rate > 1.5) tags.push('Fast-growing');
      if (repo.hackernews_discussions && repo.hackernews_discussions.length > 0) tags.push('HN Discussion');
      if (repo.total_score >= 35) tags.push('High Potential');
      
      return `
        <div class="repo-card">
          <div class="repo-header">
            <span class="rank-badge">#${repo.rank}</span>
            <h3 class="repo-name"><a href="${repo.html_url}" target="_blank">${repo.name}</a></h3>
          </div>
          
          <div class="repo-meta">
            <span>
              <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
              </svg>
              ${repo.stars} stars
            </span>
            <span>
              <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                <path fill-rule="evenodd" d="M1.643 3.143L.427 1.927A.25.25 0 000 2.104V5.75c0 .138.112.25.25.25h3.646a.25.25 0 00.177-.427L2.715 4.215a6.5 6.5 0 11-1.18 4.458.75.75 0 10-1.493.154 8.001 8.001 0 101.6-5.684zM7.75 4a.75.75 0 01.75.75v2.992l2.028.812a.75.75 0 01-.557 1.392l-2.5-1A.75.75 0 017 8.25v-3.5A.75.75 0 017.75 4z"></path>
              </svg>
              ${repo.days_since_creation} days
            </span>
            <span>
              <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                <path fill-rule="evenodd" d="M8 1.5c-2.363 0-4 1.69-4 3.75 0 .984.424 1.625.984 2.304l.214.253c.223.264.47.556.673.848.284.411.537.896.621 1.49a.75.75 0 01-1.484.211c-.04-.282-.163-.547-.37-.847a8.695 8.695 0 00-.542-.68c-.084-.1-.173-.205-.268-.32C3.201 7.75 2.5 6.766 2.5 5.25 2.5 2.31 4.863 0 8 0s5.5 2.31 5.5 5.25c0 1.516-.701 2.5-1.328 3.259-.095.115-.184.22-.268.319-.207.245-.383.453-.541.681-.208.3-.33.565-.37.847a.75.75 0 01-1.485-.212c.084-.593.337-1.078.621-1.489.203-.292.45-.584.673-.848.075-.088.147-.173.213-.253.561-.679.985-1.32.985-2.304 0-2.06-1.637-3.75-4-3.75zM6 15.25a.75.75 0 01.75-.75h2.5a.75.75 0 010 1.5h-2.5a.75.75 0 01-.75-.75zM5.75 12a.75.75 0 000 1.5h4.5a.75.75 0 000-1.5h-4.5z"></path>
              </svg>
              ${repo.language || 'Unknown'}
            </span>
          </div>
          
          <div class="repo-tags">
            ${tags.map(tag => `<span class="repo-tag">${tag}</span>`).join('')}
          </div>
          
          <p class="repo-description">${repo.description || 'No description provided.'}</p>
          
          <div class="score-section">
            <div class="score-label">Repository Score</div>
            <div class="score-bars">${createScoreBars(repoScore)}</div>
            
            <div class="score-label">Organization Score</div>
            <div class="score-bars">${createScoreBars(orgScore)}</div>
            
            <div class="score-label">Community Score</div>
            <div class="score-bars">${createScoreBars(communityScore)}</div>
            
            <div class="score-breakdown">
              <div class="score-category">
                <div class="score-category-name">Repository</div>
                <div class="score-category-value">${repo.scores.repository}</div>
              </div>
              <div class="score-category">
                <div class="score-category-name">Organization</div>
                <div class="score-category-value">${repo.scores.organization}</div>
              </div>
              <div class="score-category">
                <div class="score-category-name">Community</div>
                <div class="score-category-value">${repo.scores.community}</div>
              </div>
            </div>
            
            <div class="total-score">Total Score: ${repo.total_score}/50</div>
          </div>
        </div>
      `;
    }).join('');
  }
  
  /**
   * Render charts for trends
   * @param {Array} trends - Trend data
   */
  function renderCharts(trends) {
    if (!trends || !trends.length) return;
    
    const trendsContainer = document.getElementById('trends-container');
    if (!trendsContainer) return;
    
    trends.forEach((trend, index) => {
      const trendElement = document.createElement('div');
      trendElement.className = 'trend-item';
      trendElement.innerHTML = `
        <h3 class="trend-title">${trend.title}</h3>
        <p>${trend.description}</p>
        <div id="chart-${index}" class="trend-chart"></div>
      `;
      trendsContainer.appendChild(trendElement);
      
      // For a real implementation, you would use a charting library like Chart.js
      // Here we're just creating a placeholder
      const chartElement = document.getElementById(`chart-${index}`);
      if (chartElement && typeof Chart !== 'undefined') {
        // If Chart.js is loaded, create a chart
        // This is a placeholder - you would need to include Chart.js and set up actual charts
      } else if (chartElement) {
        // Fallback if Chart.js is not available
        chartElement.innerHTML = `<div style="padding: 20px; text-align: center;">Chart visualization would appear here</div>`;
      }
    });
  }
  
  /**
   * Render insights
   * @param {Array} insights - Insight data
   */
  function renderInsights(insights) {
    if (!insights || !insights.length) return;
    
    const insightsContainer = document.getElementById('insights-container');
    if (!insightsContainer) return;
    
    insights.forEach(insight => {
      const insightElement = document.createElement('div');
      insightElement.className = 'insight-item';
      insightElement.innerHTML = `
        <h3 class="insight-title">${insight.title}</h3>
        <p>${insight.description}</p>
        ${insight.repositories ? `
          <div>Related repositories: 
            ${insight.repositories.map(repo => 
              `<a href="#" data-repo="${repo}" class="repo-link">${repo}</a>`
            ).join(', ')}
          </div>
        ` : ''}
      `;
      insightsContainer.appendChild(insightElement);
    });
    
    // Add click handlers for repository links
    document.querySelectorAll('.repo-link').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const repoName = e.target.dataset.repo;
        
        // Filter to show only this repository
        searchInput.value = repoName;
        updateFilters();
        
        // Scroll to repos section
        document.getElementById('repositories').scrollIntoView({ behavior: 'smooth' });
      });
    });
  }
});
