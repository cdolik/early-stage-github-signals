/**
 * Early Stage GitHub Signals Dashboard
 * Modern dashboard for displaying promising early-stage repositories
 */

document.addEventListener('DOMContentLoaded', () => {
    const dashboard = {
        data: null,
        filters: {
            ecosystem: 'all',
            sort: 'score'
        },
        history: null,

        async init() {
            try {
                // Initialize history if available
                if (window.SignalsHistory) {
                    this.history = new SignalsHistory();
                    await this.history.init();
                }

                await this.loadData();
                this.setupEventListeners();
                this.renderRepositories();
                this.updateLastUpdated();
                document.getElementById('loadingIndicator').classList.add('hidden');
            } catch (error) {
                console.error('Error initializing dashboard:', error);
                this.showError('Failed to load repository data');
            }
        },

        async loadData() {
            try {
                const basePath = location.hostname === 'localhost' ? '.' : '/early-stage-github-signals';
                const response = await fetch(`${basePath}/api/latest.json`);
                if (!response.ok) throw new Error('Failed to fetch data');
                this.data = await response.json();
                console.log('Loaded data:', this.data);
            } catch (error) {
                console.error('Error loading data:', error);
                throw error;
            }
        },

        setupEventListeners() {
            // Ecosystem filter buttons
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    // Update active button
                    document.querySelectorAll('.filter-btn').forEach(b =>
                        b.classList.remove('active'));
                    e.target.classList.add('active');

                    // Apply filter
                    this.filters.ecosystem = e.target.dataset.filter;
                    this.renderRepositories();
                });
            });

            // Sort dropdown
            document.getElementById('sortSelect').addEventListener('change', (e) => {
                this.filters.sort = e.target.value;
                this.renderRepositories();
            });
        },

        updateLastUpdated() {
            const dateElement = document.getElementById('lastUpdated');
            if (dateElement && this.data && this.data.date) {
                const date = new Date(this.data.date);
                dateElement.textContent = date.toLocaleDateString();
            } else if (dateElement) {
                const date = new Date();
                dateElement.textContent = date.toLocaleDateString();
            }
        },

        renderRepositories() {
            const container = document.getElementById('repositoriesGrid');
            if (!container || !this.data || !this.data.repositories) return;

            // Filter repositories
            let repos = [...this.data.repositories];

            if (this.filters.ecosystem !== 'all') {
                repos = repos.filter(repo => repo.ecosystem === this.filters.ecosystem);
            }

            // Sort repositories
            switch (this.filters.sort) {
                case 'score':
                    repos.sort((a, b) => b.score - a.score);
                    break;
                case 'stars':
                    repos.sort((a, b) => b.stars - a.stars);
                    break;
                case 'newest':
                    repos.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
                    break;
            }

            // Limit to top 5
            const topRepos = repos.slice(0, 5);

            // Clear container
            container.innerHTML = '';

            // Show "no results" if needed
            if (topRepos.length === 0) {
                document.getElementById('noResults').classList.remove('hidden');
                return;
            }

            document.getElementById('noResults').classList.add('hidden');

            // Render repositories
            topRepos.forEach(repo => {
                const card = this.createRepositoryCard(repo);
                container.appendChild(card);
            });
        },

        createRepositoryCard(repo) {
            const card = document.createElement('div');
            card.className = 'repo-card';

            // Determine score color
            let scoreClass = 'score-normal';
            if (repo.score >= 8) scoreClass = 'score-high';
            else if (repo.score >= 7) scoreClass = 'score-medium';

            // Extract key signals
            const signals = [];
            for (const [key, value] of Object.entries(repo.signals)) {
                if (value && value > 0) {
                    signals.push(this.formatSignal(key, value));
                }
            }

            // Create signals HTML
            const signalsHTML = signals.length > 0 ?
                `<div class="repo-signals">
                    ${signals.map(s => `<span class="signal">${s}</span>`).join('')}
                </div>` : '';

            // Create optional ecosystem badge
            const ecosystemBadge = repo.ecosystem ?
                `<span class="ecosystem-badge">${repo.ecosystem}</span>` : '';

            // Create sparkline if trend data exists
            const sparkline = repo.trend ? this.createSparkline(repo.trend, repo.full_name) :
                (this.history ? this.createSparkline(null, repo.full_name) : '');

            card.innerHTML = `
                <div class="repo-header">
                    <h3 class="repo-name">
                        <a href="${repo.repo_url}" target="_blank">${repo.name}</a>
                    </h3>
                    <div class="score-badge ${scoreClass}">${repo.score}</div>
                </div>
                <p class="repo-description">${repo.description || ''}</p>
                ${signalsHTML}
                <div class="repo-footer">
                    <div class="repo-stats">
                        <span class="stat"><i class="fas fa-star"></i> ${repo.stars || 0}</span>
                        ${ecosystemBadge}
                    </div>
                    ${sparkline}
                    <div class="repo-why">${repo.why_matters || ''}</div>
                </div>
            `;

            return card;
        },

        formatSignal(key, value) {
            switch (key) {
                case 'commit_surge':
                    return `<i class="fas fa-code-commit" title="Commit surge: ${value}"></i>`;
                case 'star_velocity':
                    return `<i class="fas fa-star" title="Star velocity: ${value}"></i>`;
                case 'team_traction':
                    return `<i class="fas fa-users" title="Team traction: ${value}"></i>`;
                case 'dev_ecosystem_fit':
                    return `<i class="fas fa-puzzle-piece" title="Ecosystem fit: ${value}"></i>`;
                default:
                    return `<i class="fas fa-chart-line" title="${key}: ${value}"></i>`;
            }
        },

        createSparkline(trend, repoFullName) {
            if (!trend || trend.length < 2) return '';

            // If trend wasn't passed but we have history, try to get it
            if ((!trend || trend.length === 0) && this.history && repoFullName) {
                trend = this.history.getTrend(repoFullName);

                // Still no trend? Return empty
                if (!trend || trend.length < 2) return '';
            }

            // Simple SVG sparkline
            const width = 50;
            const height = 20;
            const values = trend.map(t => parseFloat(t));
            const max = Math.max(...values);
            const min = Math.min(...values) || 0;

            // Create points
            const points = values.map((value, index) => {
                const x = (index / (values.length - 1)) * width;
                const y = height - ((value - min) / (max - min || 1)) * height;
                return `${x},${y}`;
            }).join(' ');

            // Add final point with label
            const direction = values[values.length - 1] > values[values.length - 2] ? 'up' : 'down';
            const trendIcon = direction === 'up' ? '↑' : '↓';

            return `
                <div class="sparkline" title="Score trend">
                    <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
                        <polyline fill="none" stroke="var(--accent-color)" stroke-width="1" points="${points}" />
                    </svg>
                    <span class="trend-${direction}">${trendIcon}</span>
                </div>
            `;
        },

        showError(message) {
            document.getElementById('loadingIndicator').classList.add('hidden');
            const container = document.getElementById('repositoriesGrid');
            if (container) {
                container.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>${message}</p>
                        <button onclick="location.reload()">Try Again</button>
                    </div>
                `;
            }
        }
    };

    dashboard.init();
});
