/**
 * Early Stage GitHub Signals Dashboard
 * Signal-First Dashboard for displaying promising early-stage repositories
 * Version 4.0 - Streamlined Signal-First UX
 */

document.addEventListener('DOMContentLoaded', () => {
    const moversContainer = document.getElementById('movers');
    const emptyState = document.getElementById('emptyState');
    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modal-body');
    const closeButton = document.querySelector('.close-button');
    const searchInput = document.getElementById('searchInput');
    let allRepos = [];
    let filteredRepos = [];

    async function fetchData() {
        try {
            moversContainer.innerHTML = `<div class="loading">Loading repositories...</div>`;

            const res = await fetch('api/latest.json');
            if (!res.ok) {
                throw new Error(`API responded with status: ${res.status}`);
            }

            const data = await res.json();
            allRepos = data.repositories || [];

            // Filter by momentum score >= 7 and take top 5 repos
            filteredRepos = allRepos
                .filter(repo => repo.score >= 7)
                .sort((a, b) => b.score - a.score)
                .slice(0, 5);

            renderRepos(filteredRepos);

            // Set date
            if (data.date_generated) {
                document.getElementById('report-date').textContent = new Date(data.date_generated).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
            }
            document.getElementById('current-year').textContent = new Date().getFullYear();

            // Handle empty results
            if (filteredRepos.length === 0) {
                emptyState.style.display = 'block';
            }

        } catch (e) {
            console.error("Error fetching repository data:", e);
            moversContainer.innerHTML = `
                <div class="error-state" role="alert">
                    <h3>Unable to connect</h3>
                    <p>Failed to load repository data</p>
                    <p class="error-details">Please check your connection and try again</p>
                    <button id="retryButton" class="retry-button" aria-label="Retry loading data">Retry Loading</button>
                </div>
            `;
            document.getElementById('retryButton')?.addEventListener('click', fetchData);
        }
    }

    function buildCard(r) {
        const card = document.createElement('div');
        card.className = 'project-card';
        card.dataset.repoId = r.id || r.name;

        // Add ARIA attributes for accessibility
        card.setAttribute('role', 'button');
        card.setAttribute('aria-label', `Repository ${r.name}, momentum score ${r.score}. Click for details.`);
        card.tabIndex = 0; // Make it focusable for keyboard navigation

        // Create score change indicator if available
        let scoreChangeHtml = '';
        if (r.score_change !== undefined && r.score_change !== null) {
            const changeClass = r.score_change > 0 ? 'positive-change' : (r.score_change < 0 ? 'negative-change' : 'neutral-change');
            const changeSymbol = r.score_change > 0 ? '↑' : (r.score_change < 0 ? '↓' : '');
            scoreChangeHtml = `<span class="score-change ${changeClass}" title="Score change: ${r.score_change > 0 ? '+' : ''}${r.score_change.toFixed(1)}">${changeSymbol} ${Math.abs(r.score_change).toFixed(1)}</span>`;
        }

        // Create sparkline visualization if available
        let sparklineHtml = '';
        if (r.trend && r.trend.length > 0) {
            // Add visual emphasis to the trend
            const trendArrows = r.trend.map((value, index, arr) => {
                if (index === 0) return value;
                const prev = parseFloat(arr[index - 1]);
                const current = parseFloat(value);
                if (current > prev) return `<span style="color:#15803d">↗ ${value}</span>`;
                if (current < prev) return `<span style="color:#b91c1c">↘ ${value}</span>`;
                return `<span>→ ${value}</span>`;
            }).join(' ');

            sparklineHtml = `<div class="sparkline-container">
                <div class="trend-indicator">
                    ${trendArrows}
                </div>
            </div>`;
        }

        card.innerHTML = `
      <div class="card-header">
        <h3><a href="${r.repo_url || '#'}" target="_blank" aria-label="Visit ${r.name} on GitHub">${r.name || 'N/A'}</a></h3>
        <div class="score-container">
          <span class="momentum-score" title="Momentum score: ${r.score !== undefined ? r.score.toFixed(1) : 'N/A'}">${r.score !== undefined ? r.score.toFixed(1) : '-'}</span>
          ${scoreChangeHtml}
        </div>
      </div>
      ${sparklineHtml}
      <p class="why-matters">${r.why_matters || ''}</p>
    `;

        // Add click event to show modal with detailed info
        card.addEventListener('click', (e) => {
            // Don't trigger modal if clicking on the repo link
            if (e.target.tagName === 'A') return;
            showModal(r);
        });

        return card;
    }

    function renderRepos(repos) {
        moversContainer.innerHTML = '';

        if (repos.length > 0) {
            // Add staggered animation by setting delay for each card
            repos.forEach((r, index) => {
                const card = buildCard(r);
                // Apply staggered delay for smooth card appearance
                card.style.animationDelay = `${index * 100}ms`;
                moversContainer.appendChild(card);
            });
            emptyState.style.display = 'none';
        } else {
            emptyState.style.display = 'block';
            if (searchInput.value) {
                // Show custom message for search with no results
                emptyState.innerHTML = `
                    <h3>No matching repositories found</h3>
                    <p>Try adjusting your search term or check back later for new projects.</p>
                `;
            } else {
                // Show default empty state message
                emptyState.innerHTML = `
                    <h3>📭 No breakout OSS projects this week</h3>
                    <p>Our radar updates every Monday. Check back soon for new momentum signals.</p>
                `;
            }
        }
    }

    // Search functionality
    function handleSearch() {
        const query = searchInput.value.toLowerCase().trim();

        if (!query) {
            // If search is empty, show top repos
            renderRepos(filteredRepos);
            return;
        }

        // Filter repos by name or why_matters text
        const searchResults = allRepos.filter(repo =>
            (repo.name && repo.name.toLowerCase().includes(query)) ||
            (repo.why_matters && repo.why_matters.toLowerCase().includes(query))
        );

        renderRepos(searchResults);
    }

    function showModal(repo) {
        // Build detailed view for the modal
        let trendDetails = '';
        if (repo.trend && repo.trend.length > 0) {
            // Add visual emphasis to the trend
            const trendArrows = repo.trend.map((value, index, arr) => {
                if (index === 0) return value;
                const prev = parseFloat(arr[index - 1]);
                const current = parseFloat(value);
                if (current > prev) return `<span style="color:#15803d">↗ ${value}</span>`;
                if (current < prev) return `<span style="color:#b91c1c">↘ ${value}</span>`;
                return `<span>→ ${value}</span>`;
            }).join(' ');

            trendDetails = `
                <div class="detail-section">
                    <h3>Momentum Trend</h3>
                    <div class="trend-chart" style="font-size: 1.2rem; padding: 10px 0;">${trendArrows}</div>
                </div>
            `;
        }

        // Build metrics if available
        let metricsHtml = '';
        if (repo.metrics) {
            const metrics = repo.metrics;
            metricsHtml = `
                <div class="detail-section">
                    <h3>Key Metrics</h3>
                    <div class="metrics-grid">
                        ${metrics.stars ? `<div class="metric-card" title="Total GitHub stars">
                            <div class="metric-value">⭐ ${metrics.stars}</div>
                            <div class="metric-label">Stars</div>
                        </div>` : ''}
                        
                        ${metrics.forks ? `<div class="metric-card" title="Total project forks">
                            <div class="metric-value">🍴 ${metrics.forks}</div>
                            <div class="metric-label">Forks</div>
                        </div>` : ''}
                        
                        ${metrics.commits ? `<div class="metric-card" title="Recent code commits">
                            <div class="metric-value">📝 ${metrics.commits}</div>
                            <div class="metric-label">Recent Commits</div>
                        </div>` : ''}
                        
                        ${metrics.contributors ? `<div class="metric-card" title="Total contributors">
                            <div class="metric-value">👥 ${metrics.contributors}</div>
                            <div class="metric-label">Contributors</div>
                        </div>` : ''}
                        
                        ${metrics.issues ? `<div class="metric-card" title="Open issues">
                            <div class="metric-value">🔍 ${metrics.issues}</div>
                            <div class="metric-label">Open Issues</div>
                        </div>` : ''}
                        
                        ${metrics.pr_velocity ? `<div class="metric-card" title="PR velocity">
                            <div class="metric-value">🔄 ${metrics.pr_velocity}</div>
                            <div class="metric-label">PR Velocity</div>
                        </div>` : ''}
                    </div>
                </div>
            `;
        }

        // Description section
        const descriptionHtml = repo.description ? `
            <div class="detail-section">
                <h3>About</h3>
                <p>${repo.description}</p>
            </div>
        ` : '';

        // Combine all sections
        modalBody.innerHTML = `
            <h2 id="modal-title"><a href="${repo.repo_url || '#'}" target="_blank">${repo.name || 'Repository Details'}</a></h2>
            <div class="score-container modal-score">
                <span class="momentum-score" title="Momentum score: ${repo.score !== undefined ? repo.score.toFixed(1) : 'N/A'}">${repo.score !== undefined ? repo.score.toFixed(1) : '-'}</span>
                ${repo.score_change !== undefined ? `<span class="score-change ${repo.score_change > 0 ? 'positive-change' : (repo.score_change < 0 ? 'negative-change' : 'neutral-change')}" title="Score change: ${repo.score_change > 0 ? '+' : ''}${repo.score_change.toFixed(1)}">
                    ${repo.score_change > 0 ? '↑' : (repo.score_change < 0 ? '↓' : '')} ${Math.abs(repo.score_change).toFixed(1)}
                </span>` : ''}
            </div>
            
            <div class="detail-section">
                <h3>Why It Matters</h3>
                <p>${repo.why_matters || 'No context available'}</p>
            </div>
            
            ${descriptionHtml}
            ${trendDetails}
            ${metricsHtml}
        `;

        modal.style.display = 'block';
    }

    // Close modal when clicking X button
    closeButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside of modal content
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Close modal with escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            modal.style.display = 'none';
        }
    });

    // Set up search functionality
    searchInput.addEventListener('input', handleSearch);
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            searchInput.value = '';
            handleSearch();
            searchInput.blur();
        }
    });

    // Support keyboard accessibility for cards
    moversContainer.addEventListener('keydown', (e) => {
        if ((e.key === 'Enter' || e.key === ' ') && e.target.classList.contains('project-card')) {
            e.preventDefault(); // Prevent scrolling on space press
            const repoId = e.target.dataset.repoId;
            const repo = allRepos.find(r => (r.id || r.name) === repoId);
            if (repo) showModal(repo);
        }
    });

    // Ensure modal can be closed with keyboard
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            modal.style.display = 'none';
        }
    });

    fetchData();
});
