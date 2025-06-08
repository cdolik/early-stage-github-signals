/**
 * Early Stage GitHub Signals Dashboard
 * Investor-Grade Dashboard for displaying promising early-stage repositories
 * Version 2.0
 */

document.addEventListener('DOMContentLoaded', () => {
    const dashboard = {
        data: null,
        filters: {
            ecosystem: 'all',
            sort: 'score',
            minScore: 7,
            newThisWeek: false
        },
        viewMode: 'table', // 'table' or 'card'
        vcMode: false,
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
                this.renderTopMovers();
                this.renderRepositories();
                this.updateLastUpdated();
                this.updateMetricsPanel();
                this.showAlertBanner();
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

                // Calculate score changes if not already present
                this.calculateScoreChanges();
            } catch (error) {
                console.error('Error loading data:', error);
                throw error;
            }
        },

        calculateScoreChanges() {
            if (!this.data || !this.data.repositories) return;

            // For each repo, calculate score change if not present
            this.data.repositories.forEach(repo => {
                if (repo.score_change === null && repo.trend && repo.trend.length >= 2) {
                    const currentScore = repo.trend[repo.trend.length - 1];
                    const previousScore = repo.trend[repo.trend.length - 2];
                    repo.score_change = currentScore - previousScore;
                }
            });
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

            // Score slider
            const scoreSlider = document.getElementById('scoreSlider');
            const scoreValue = document.getElementById('scoreValue');
            if (scoreSlider && scoreValue) {
                scoreSlider.addEventListener('input', (e) => {
                    const value = e.target.value;
                    scoreValue.textContent = value;
                    this.filters.minScore = parseFloat(value);
                    this.renderRepositories();
                });
            }

            // New this week toggle
            const newThisWeek = document.getElementById('newThisWeek');
            if (newThisWeek) {
                newThisWeek.addEventListener('change', (e) => {
                    this.filters.newThisWeek = e.target.checked;
                    this.renderRepositories();
                });
            }

            // VC Mode toggle
            const vcModeToggle = document.getElementById('vcModeToggle');
            if (vcModeToggle) {
                vcModeToggle.addEventListener('click', () => {
                    this.vcMode = !this.vcMode;
                    vcModeToggle.classList.toggle('active', this.vcMode);
                    this.filters.minScore = this.vcMode ? 8 : 7;

                    // Update UI for VC mode
                    if (scoreSlider && scoreValue) {
                        scoreSlider.value = this.filters.minScore;
                        scoreValue.textContent = this.filters.minScore;
                    }

                    this.renderRepositories();
                });
            }

            // View toggle
            const tableViewBtn = document.getElementById('tableViewBtn');
            const cardViewBtn = document.getElementById('cardViewBtn');
            const reposTable = document.getElementById('repositoriesTable');
            const reposGrid = document.getElementById('repositoriesGrid');

            if (tableViewBtn && cardViewBtn) {
                tableViewBtn.addEventListener('click', () => {
                    this.viewMode = 'table';
                    tableViewBtn.classList.add('active');
                    cardViewBtn.classList.remove('active');

                    if (reposTable && reposGrid) {
                        reposTable.closest('.table-container').classList.remove('hidden');
                        reposGrid.classList.add('hidden');
                    }
                });

                cardViewBtn.addEventListener('click', () => {
                    this.viewMode = 'card';
                    cardViewBtn.classList.add('active');
                    tableViewBtn.classList.remove('active');

                    if (reposTable && reposGrid) {
                        reposTable.closest('.table-container').classList.add('hidden');
                        reposGrid.classList.remove('hidden');
                    }
                });
            }

            // Modal close
            const modal = document.getElementById('repoModal');
            const modalClose = document.querySelector('.modal-close');
            if (modal && modalClose) {
                modalClose.addEventListener('click', () => {
                    modal.style.display = 'none';
                });

                window.addEventListener('click', (e) => {
                    if (e.target === modal) {
                        modal.style.display = 'none';
                    }
                });
            }

            // GitHub CTA links already use standard <a> tags, no extra JS needed
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

        updateMetricsPanel() {
            if (!this.data || !this.data.repositories) return;

            // Calculate metrics
            const qualifiedRepos = this.data.repositories.filter(repo => repo.score >= 7).length;

            // Calculate median score
            const scores = [...this.data.repositories.map(repo => repo.score)].sort((a, b) => a - b);
            let median;
            if (scores.length % 2 === 0) {
                median = (scores[scores.length / 2 - 1] + scores[scores.length / 2]) / 2;
            } else {
                median = scores[Math.floor(scores.length / 2)];
            }

            // Find highest delta
            let highestDelta = 0;
            let highestDeltaRepo = '';
            this.data.repositories.forEach(repo => {
                if (repo.score_change && repo.score_change > highestDelta) {
                    highestDelta = repo.score_change;
                    highestDeltaRepo = repo.name;
                }
            });

            // Update DOM
            document.getElementById('qualifiedRepos').textContent = qualifiedRepos;
            document.getElementById('medianScore').textContent = median.toFixed(1);
            document.getElementById('highestDelta').textContent =
                highestDelta > 0 ? `+${highestDelta.toFixed(1)} (${highestDeltaRepo})` : '-';
        },

        // Empty function as we've removed the alert banner
        showAlertBanner() {
            // GitHub CTA is always visible now, no need to show/hide
        },

        renderTopMovers() {
            const container = document.getElementById('topMoversGrid');
            if (!container || !this.data || !this.data.repositories) return;

            // Get repositories with highest score change
            const repos = [...this.data.repositories]
                .filter(repo => repo.score_change && repo.score_change > 0)
                .sort((a, b) => b.score_change - a.score_change)
                .slice(0, 3);

            // Clear container
            container.innerHTML = '';

            if (repos.length === 0) {
                container.innerHTML = `
                <div class="empty-state">
                    <h3>No standout movers this week</h3>
                    <p>We track early momentum changes—but only highlight repositories that show significant positive movement.</p>
                </div>`;
                return;
            }

            // Render top movers
            repos.forEach(repo => {
                const card = this.createTopMoverCard(repo);
                container.appendChild(card);
            });
        },

        createTopMoverCard(repo) {
            const card = document.createElement('div');
            card.className = 'top-mover-card';

            // Determine score color
            let scoreClass = 'score-normal';
            if (repo.score >= 8) scoreClass = 'score-high';
            else if (repo.score >= 7) scoreClass = 'score-medium';

            // Create sparkline
            const sparkline = this.createSparkline(repo.trend, repo.full_name, true);

            // Format score change
            const scoreChange = repo.score_change ?
                `<span class="score-change-positive">+${repo.score_change.toFixed(1)}</span>` : '';

            card.innerHTML = `
                <div class="top-mover-header">
                    <h3 class="top-mover-name">
                        <a href="${repo.repo_url}" target="_blank">${repo.name}</a>
                    </h3>
                    <div class="score-badge ${scoreClass}">
                        ${repo.score} ${scoreChange}
                    </div>
                </div>
                <div class="top-mover-stats">
                    <span class="stat"><i class="fas fa-star"></i> ${repo.stars || 0}</span>
                    ${repo.ecosystem ? `<span class="ecosystem-badge">${repo.ecosystem}</span>` : ''}
                </div>
                <div class="top-mover-sparkline">
                    ${sparkline}
                </div>
                <div class="top-mover-why">${repo.why_matters || ''}</div>
            `;

            card.addEventListener('click', () => this.openRepoModal(repo));

            return card;
        },

        renderRepositories() {
            // Check if we're rendering to table or grid
            const table = document.getElementById('repositoriesTable');
            const grid = document.getElementById('repositoriesGrid');
            const noResults = document.getElementById('noResults');

            if (!this.data || !this.data.repositories) return;

            // Filter repositories
            let repos = [...this.data.repositories];

            if (this.filters.ecosystem !== 'all') {
                repos = repos.filter(repo => repo.ecosystem === this.filters.ecosystem);
            }

            // Apply score filter
            repos = repos.filter(repo => repo.score >= this.filters.minScore);

            // Apply new this week filter if checked
            if (this.filters.newThisWeek) {
                const oneWeekAgo = new Date();
                oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
                repos = repos.filter(repo => {
                    if (!repo.created_at) return false;
                    const createdDate = new Date(repo.created_at);
                    return createdDate >= oneWeekAgo;
                });
            }

            // Sort repositories
            switch (this.filters.sort) {
                case 'score':
                    repos.sort((a, b) => b.score - a.score);
                    break;
                case 'score_change':
                    repos.sort((a, b) => {
                        const changeA = a.score_change || 0;
                        const changeB = b.score_change || 0;
                        return changeB - changeA;
                    });
                    break;
                case 'stars':
                    repos.sort((a, b) => b.stars - a.stars);
                    break;
                case 'newest':
                    repos.sort((a, b) => {
                        const dateA = a.created_at ? new Date(a.created_at) : new Date(0);
                        const dateB = b.created_at ? new Date(b.created_at) : new Date(0);
                        return dateB - dateA;
                    });
                    break;
            }

            // Show "no results" if needed
            if (repos.length === 0) {
                noResults.classList.remove('hidden');
                return;
            }

            noResults.classList.add('hidden');

            // Render based on view mode
            if (this.viewMode === 'table' && table) {
                this.renderRepositoriesTable(repos, table);
            } else if (grid) {
                this.renderRepositoriesGrid(repos, grid);
            }
        },

        renderRepositoriesTable(repos, table) {
            const tbody = table.querySelector('tbody');
            if (!tbody) return;

            // Clear container
            tbody.innerHTML = '';

            // Render repositories
            repos.forEach(repo => {
                const row = this.createRepositoryRow(repo);
                tbody.appendChild(row);
            });
        },

        renderRepositoriesGrid(repos, grid) {
            // Clear container
            grid.innerHTML = '';

            // Render repositories
            repos.forEach(repo => {
                const card = this.createRepositoryCard(repo);
                grid.appendChild(card);
            });
        },

        createRepositoryRow(repo) {
            const row = document.createElement('tr');

            // Determine score color
            let scoreClass = 'score-normal';
            if (repo.score >= 8) scoreClass = 'score-high';
            else if (repo.score >= 7) scoreClass = 'score-medium';

            // Format score change
            let scoreChangeHtml = '-';
            if (repo.score_change !== null && repo.score_change !== undefined) {
                const changeClass = repo.score_change >= 0 ? 'score-change-positive' : 'score-change-negative';
                const sign = repo.score_change >= 0 ? '+' : '';
                scoreChangeHtml = `<span class="${changeClass}">${sign}${repo.score_change.toFixed(1)}</span>`;
            }

            // Create sparkline
            const sparkline = this.createSparkline(repo.trend, repo.full_name);

            row.innerHTML = `
                <td>
                    <div class="repo-name-cell">
                        <span class="repo-icon"><i class="fas fa-code-branch"></i></span>
                        <div class="repo-info">
                            <a href="${repo.repo_url}" target="_blank" class="repo-link">${repo.name}</a>
                            <span class="repo-desc">${repo.description || ''}</span>
                            ${repo.ecosystem ? `<span class="ecosystem-tag">${repo.ecosystem}</span>` : ''}
                        </div>
                    </div>
                </td>
                <td class="score-cell">${repo.score}</td>
                <td class="score-change-cell">${scoreChangeHtml}</td>
                <td>${repo.stars || 0}</td>
                <td>${repo.contributors_30d || '-'}</td>
                <td>${sparkline}</td>
                <td>${repo.why_matters || ''}</td>
            `;

            // Add click handler to open modal
            row.style.cursor = 'pointer';
            row.addEventListener('click', () => this.openRepoModal(repo));

            return row;
        },

        createRepositoryCard(repo) {
            const card = document.createElement('div');
            card.className = 'repo-card';

            // Determine score color
            let scoreClass = 'score-normal';
            if (repo.score >= 8) scoreClass = 'score-high';
            else if (repo.score >= 7) scoreClass = 'score-medium';

            // Format score change
            const scoreChange = repo.score_change ?
                `<span class="score-change-positive">+${repo.score_change.toFixed(1)}</span>` : '';

            // Extract key signals
            const signals = [];
            for (const [key, value] of Object.entries(repo.signals || {})) {
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
                    <div class="score-badge ${scoreClass}">
                        ${repo.score} ${scoreChange}
                    </div>
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

            // Add click handler
            card.addEventListener('click', () => this.openRepoModal(repo));

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

        createSparkline(trend, repoFullName, larger = false) {
            if (!trend || trend.length < 2) return '';

            // If trend wasn't passed but we have history, try to get it
            if ((!trend || trend.length === 0) && this.history && repoFullName) {
                trend = this.history.getTrend(repoFullName);

                // Still no trend? Return empty
                if (!trend || trend.length < 2) return '';
            }

            // Set SVG dimensions
            const width = larger ? 100 : 50;
            const height = larger ? 30 : 20;
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

            // Create dots for data points
            const dots = values.map((value, index) => {
                const x = (index / (values.length - 1)) * width;
                const y = height - ((value - min) / (max - min || 1)) * height;
                return `<circle cx="${x}" cy="${y}" r="${larger ? 2 : 1.5}" fill="var(--accent-primary)" />`;
            }).join('');

            // Add annotations if available
            let annotations = '';
            if (larger && trend.annotations) {
                annotations = trend.annotations.map(anno => {
                    const index = anno.index || trend.length - 1;
                    const x = (index / (trend.length - 1)) * width;
                    const y = height - ((values[index] - min) / (max - min || 1)) * height;
                    return `
                        <g class="annotation" title="${anno.text}">
                            <circle cx="${x}" cy="${y}" r="3" fill="var(--accent-secondary)" />
                            <text x="${x}" y="${y - 5}" text-anchor="middle" font-size="8">${anno.label || '!'}</text>
                        </g>
                    `;
                }).join('');
            }

            return `
                <div class="sparkline ${larger ? 'sparkline-lg' : ''}" title="Score trend over time">
                    <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
                        <polyline fill="none" stroke="var(--accent-primary)" stroke-width="${larger ? 2 : 1}" points="${points}" />
                        ${dots}
                        ${annotations}
                    </svg>
                    <span class="sparkline-trend-${direction}">${trendIcon}</span>
                </div>
            `;
        },

        openRepoModal(repo) {
            const modal = document.getElementById('repoModal');
            const modalName = document.getElementById('modalRepoName');
            const modalBody = document.getElementById('modalBody');

            if (!modal || !modalName || !modalBody) return;

            // Set repository name
            modalName.textContent = repo.name;

            // Create detailed content
            const sparkline = this.createSparkline(repo.trend, repo.full_name, true);

            // Create signals details
            let signalsHtml = '<div class="modal-signals">';
            if (repo.signals) {
                for (const [key, value] of Object.entries(repo.signals)) {
                    if (value && value > 0) {
                        signalsHtml += `
                            <div class="modal-signal">
                                <div class="signal-name">${this.formatSignalName(key)}</div>
                                <div class="signal-value">${value}</div>
                            </div>
                        `;
                    }
                }
            }
            signalsHtml += '</div>';

            // Format score change
            let scoreChangeHtml = '';
            if (repo.score_change !== null && repo.score_change !== undefined) {
                const changeClass = repo.score_change >= 0 ? 'score-change-positive' : 'score-change-negative';
                const sign = repo.score_change >= 0 ? '+' : '';
                scoreChangeHtml = `<div class="modal-score-change ${changeClass}">${sign}${repo.score_change.toFixed(1)} pts this week</div>`;
            }

            // Create content
            modalBody.innerHTML = `
                <div class="modal-repo-details">
                    <div class="modal-description">${repo.description || ''}</div>
                    
                    <div class="modal-stats">
                        <div class="modal-stat-group">
                            <div class="modal-stat">
                                <div class="stat-label">Score</div>
                                <div class="stat-value">${repo.score}/10</div>
                            </div>
                            ${scoreChangeHtml}
                        </div>
                        
                        <div class="modal-stat-group">
                            <div class="modal-stat">
                                <div class="stat-label">Stars</div>
                                <div class="stat-value"><i class="fas fa-star"></i> ${repo.stars || 0}</div>
                            </div>
                            <div class="modal-stat">
                                <div class="stat-label">Ecosystem</div>
                                <div class="stat-value">${repo.ecosystem || 'Other'}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="modal-trend">
                        <h3>Momentum Trend</h3>
                        ${sparkline}
                    </div>
                    
                    <div class="modal-signals-section">
                        <h3>Signal Breakdown</h3>
                        ${signalsHtml}
                    </div>
                    
                    <div class="modal-why-section">
                        <h3>Why It Matters</h3>
                        <p>${repo.why_matters || 'No additional insights available'}</p>
                    </div>
                </div>
            `;

            // Show modal
            modal.style.display = 'block';
        },

        formatSignalName(key) {
            switch (key) {
                case 'commit_surge':
                    return 'Commit Surge';
                case 'star_velocity':
                    return 'Star Velocity';
                case 'team_traction':
                    return 'Team Traction';
                case 'dev_ecosystem_fit':
                    return 'Ecosystem Fit';
                default:
                    return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
            }
        },

        showError(message) {
            document.getElementById('loadingIndicator').classList.add('hidden');
            const container = document.getElementById('repositoriesGrid');
            const table = document.querySelector('.table-container');

            if (container) {
                container.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>${message}</p>
                        <button onclick="location.reload()">Try Again</button>
                    </div>
                `;
            }

            if (table) {
                table.classList.add('hidden');
            }

            // Show the grid view with error
            container.classList.remove('hidden');
        },

        exportRepositoryData(repo) {
            // Create a CSV or JSON representation of repo data
            if (!repo) return;

            const dataStr = JSON.stringify(repo, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const dataUrl = URL.createObjectURL(dataBlob);

            // Create download link
            const downloadLink = document.createElement('a');
            downloadLink.href = dataUrl;
            downloadLink.download = `${repo.name}-report.json`;
            downloadLink.click();
        },

        toggleDeveloperView() {
            const devGuide = document.getElementById('implementationGuide');
            if (devGuide) {
                devGuide.classList.toggle('hidden');
            }
        }
    };

    dashboard.init();

    // Enable Dev Mode with Konami Code
    let konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
    let konamiPosition = 0;

    document.addEventListener('keydown', (e) => {
        if (e.key === konamiCode[konamiPosition]) {
            konamiPosition++;
            if (konamiPosition === konamiCode.length) {
                dashboard.toggleDeveloperView();
                konamiPosition = 0;
            }
        } else {
            konamiPosition = 0;
        }
    });
});
