/**
 * Early Stage GitHub Signals Dashboard
 * Enhanced UX Dashboard for displaying promising early-stage repositories
 * Version 5.0 - Professional Grade UX
 */

document.addEventListener('DOMContentLoaded', () => {
    // Helper functions for UI and error handling
    function getProjectDescription(project) {
        return project.tagline || project.description || "No description provided.";
    }

    function showError(message) {
        const errorContainer = document.getElementById("error-message") || document.body;
        const div = document.createElement("div");
        div.textContent = `Error: ${message}`;
        div.style.color = "red";
        div.style.padding = "1em";
        errorContainer.appendChild(div);
        console.error("Dashboard error:", message);
    }

    // Initialize UI elements
    const loadingScreen = document.getElementById('loading-screen');
    const stickyNav = document.getElementById('sticky-nav');
    const mainHeader = document.getElementById('main-header');
    const moversContainer = document.getElementById('movers');
    const emptyState = document.getElementById('emptyState');
    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modal-body');
    const modalClose = document.querySelector('.modal-close');
    const modalOverlay = document.querySelector('.modal-overlay');
    const refreshBtn = document.getElementById('refresh-btn');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const viewButtons = document.querySelectorAll('.view-btn');

    // State management
    let allRepos = [];
    let filteredRepos = [];
    let currentFilter = 'all';
    let currentView = 'grid';
    let isLoading = false;

    // Initialize app
    init();

    async function init() {
        try {
            setupEventListeners();
            setupIntersectionObserver();
            setupAccessibility();
            setupScrollToTop();
            showSkeletonLoading();

            const fetchWithRetry = createRetryMechanism(fetchData);
            await fetchWithRetry();

            setupAdvancedObserver();
            prefetchResources();
            safeHideLoadingScreen();

            // Announce successful load
            setTimeout(() => {
                window.announceToScreenReader?.(`Loaded ${allRepos.length} repositories`);
            }, 500);
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
            showError('Failed to initialize dashboard');
            safeHideLoadingScreen();
        }
    }

    function setupEventListeners() {
        // Refresh button
        refreshBtn?.addEventListener('click', handleRefresh);

        // Filter buttons
        filterButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const filter = e.target.dataset.filter;
                setActiveFilter(filter);
                applyFilter(filter);
            });
        });

        // View toggle buttons
        viewButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const view = e.target.dataset.view;
                setActiveView(view);
                applyView(view);
            });
        });

        // Modal event listeners
        modalClose?.addEventListener('click', closeModal);
        modalOverlay?.addEventListener('click', closeModal);

        // Keyboard shortcuts
        document.addEventListener('keydown', handleKeyboard);

        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    function setupIntersectionObserver() {
        // Sticky nav visibility
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.target === mainHeader) {
                    stickyNav?.classList.toggle('visible', !entry.isIntersecting);
                }
            });
        }, { threshold: 0.1 });

        if (mainHeader) {
            observer.observe(mainHeader);
        }
    }

    async function fetchData() {
        if (isLoading) return; try {
            isLoading = true;
            addLoadingStates();

            // Enhanced path resolution for GitHub Pages
            const basePaths = [
                location.hostname === 'cdolik.github.io' ? '/early-stage-github-signals/' : '',
                './',
                ''
            ];

            let data = null;
            let lastError = null;

            for (const basePath of basePaths) {
                try {
                    const apiPath = `${basePath}api/latest.json`.replace(/\/+/g, '/').replace(/^\//, basePath ? '/' : '');
                    console.log(`Attempting to fetch from: ${apiPath}`);

                    const res = await fetch(apiPath, {
                        cache: 'no-cache',
                        headers: {
                            'Cache-Control': 'no-cache'
                        }
                    });
                    if (res.ok) {
                        data = await res.json();
                        console.log(`Successfully fetched data from: ${apiPath}`);
                        break;
                    } else {
                        lastError = new Error(`HTTP ${res.status}: ${res.statusText}`);
                    }
                } catch (err) {
                    lastError = err;
                    console.log(`Failed to fetch from ${basePath}: ${err.message}`);
                }
            }

            if (!data) {
                throw lastError || new Error('All fetch attempts failed');
            }

            processData(data);
            updateStats(data);
            renderRepositories();

        } catch (error) {
            console.error("Error fetching repository data:", error);
            
            // Enhanced error handling with user-friendly messages
            let userMessage = 'Unable to load repository data';
            if (error.message.includes('fetch')) {
                userMessage = 'Network error: Unable to connect to the data source';
            } else if (error.message.includes('JSON')) {
                userMessage = 'Data format error: The server returned invalid data';
            } else if (error.message.includes('HTTP')) {
                userMessage = `Server error: ${error.message}`;
            }
            
            showError(userMessage);
            
            // Rethrow the error to allow higher-level handling
            throw error;
        } finally {
            isLoading = false;
            removeLoadingStates();
        }
    }

    function processData(data) {
        // Enhanced data validation to prevent crashes from malformed data
        try {
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid data format: expected object');
            }

            if (!Array.isArray(data.repositories)) {
                console.warn('No repositories array found in data, using empty array');
                data.repositories = [];
            }

            allRepos = data.repositories.map((repo, index) => {
                // Validate individual repository data
                if (!repo || typeof repo !== 'object') {
                    console.warn(`Invalid repository data at index ${index}, skipping`);
                    return null;
                }

                return {
                    ...repo,
                    id: repo.id || repo.name || `repo-${index}`,
                    score: typeof repo.score === 'number' ? repo.score : 0,
                    name: typeof repo.name === 'string' ? repo.name : 'Unknown Repository',
                    description: typeof repo.description === 'string' ? repo.description : '',
                    why_matters: typeof repo.why_matters === 'string' ? repo.why_matters : '',
                    repo_url: typeof repo.repo_url === 'string' ? repo.repo_url : (typeof repo.url === 'string' ? repo.url : '#'),
                    trend: Array.isArray(repo.trend) ? repo.trend : [],
                    score_change: typeof repo.score_change === 'number' ? repo.score_change : undefined
                };
            }).filter(repo => repo !== null); // Remove invalid entries

            // Sort by score
            allRepos.sort((a, b) => b.score - a.score);

            // Calculate and render metrics
            const metrics = calculateMetrics(data);
            renderMetrics(metrics);

            // Set initial filter
            applyFilter(currentFilter);

            // Update date
            if (data.date_generated) {
                try {
                    const date = new Date(data.date_generated);
                    if (!isNaN(date.getTime())) {
                        const formattedDate = date.toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                        });
                        const dateElement = document.getElementById('report-date');
                        if (dateElement) {
                            dateElement.textContent = formattedDate;
                        }
                    }
                } catch (dateError) {
                    console.warn('Invalid date format in data:', data.date_generated);
                }
            }

            // Set current year in footer
            const currentYearElement = document.getElementById('current-year');
            if (currentYearElement) {
                currentYearElement.textContent = new Date().getFullYear();
            }
        } catch (error) {
            console.error('Error processing data:', error);
            showError('Data processing error: ' + error.message);
            
            // Initialize with empty data to prevent further crashes
            allRepos = [];
            const emptyMetrics = calculateMetrics({ repositories: [] });
            renderMetrics(emptyMetrics);
        }
    }

    function calculateMetrics(data) {
        if (!data || !data.repositories) {
            return {
                totalRepositories: 0,
                qualifyingRepositories: 0,
                medianScore: 0,
                highestScore: 0,
                averageScore: 0
            };
        }

        const repos = data.repositories;
        const scores = repos.map(repo => repo.score || 0).filter(score => score > 0);
        const qualifyingRepos = repos.filter(repo => (repo.score || 0) >= 7);

        // Calculate median
        const sortedScores = [...scores].sort((a, b) => a - b);
        const medianScore = sortedScores.length > 0 
            ? sortedScores.length % 2 === 0
                ? (sortedScores[sortedScores.length / 2 - 1] + sortedScores[sortedScores.length / 2]) / 2
                : sortedScores[Math.floor(sortedScores.length / 2)]
            : 0;

        return {
            totalRepositories: repos.length,
            qualifyingRepositories: qualifyingRepos.length,
            medianScore: Math.round(medianScore * 10) / 10,
            highestScore: scores.length > 0 ? Math.max(...scores) : 0,
            averageScore: scores.length > 0 ? Math.round((scores.reduce((sum, score) => sum + score, 0) / scores.length) * 10) / 10 : 0
        };
    }

    function renderMetrics(metrics) {
        // Create or update metrics container
        let metricsContainer = document.getElementById('metrics-dashboard');
        if (!metricsContainer) {
            metricsContainer = document.createElement('div');
            metricsContainer.id = 'metrics-dashboard';
            metricsContainer.className = 'metrics-container';
            
            // Insert after nav but before main content
            const nav = document.getElementById('sticky-nav');
            if (nav) {
                if (nav.nextSibling) {
                    nav.parentNode.insertBefore(metricsContainer, nav.nextSibling);
                } else {
                    nav.parentNode.appendChild(metricsContainer);
                }
            } else {
                document.body.appendChild(metricsContainer);
            }
        }

        metricsContainer.innerHTML = `
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Total Repositories</h3>
                    <span class="metric-value">${metrics.totalRepositories}</span>
                </div>
                <div class="metric-card">
                    <h3>Qualifying (≥7.0)</h3>
                    <span class="metric-value">${metrics.qualifyingRepositories}</span>
                </div>
                <div class="metric-card">
                    <h3>Median Score</h3>
                    <span class="metric-value">${metrics.medianScore}</span>
                </div>
                <div class="metric-card">
                    <h3>Highest Score</h3>
                    <span class="metric-value">${metrics.highestScore}</span>
                </div>
                <div class="metric-card">
                    <h3>Average Score</h3>
                    <span class="metric-value">${metrics.averageScore}</span>
                </div>
            </div>
        `;
    }

    function updateStats(data) {
        const repoCount = allRepos.length;
        const avgScore = repoCount > 0 ?
            (allRepos.reduce((sum, repo) => sum + repo.score, 0) / repoCount).toFixed(1) : '0';

        // Animate numbers
        animateNumber(document.getElementById('repo-count'), repoCount);
        animateNumber(document.getElementById('avg-score'), parseFloat(avgScore));
    }

    function animateNumber(element, targetValue) {
        if (!element) return;

        const startValue = 0;
        const duration = 1000;
        const startTime = performance.now();

        function updateNumber(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentValue = Math.round(startValue + (targetValue - startValue) * easeOut);

            element.textContent = currentValue;

            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        }

        requestAnimationFrame(updateNumber);
    }

    function applyFilter(filter) {
        currentFilter = filter;

        switch (filter) {
            case 'trending':
                filteredRepos = allRepos.filter(repo => repo.score_change > 0).slice(0, 10);
                break;
            case 'new':
                // Filter for repos created in the last week (this would need actual date logic)
                filteredRepos = allRepos.slice(0, 5);
                break;
            case 'all':
            default:
                filteredRepos = allRepos.slice(0, 10);
                break;
        }

        renderRepositories();
    }

    function setActiveFilter(filter) {
        filterButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });
    }

    function applyView(view) {
        currentView = view;
        const grid = document.querySelector('.projects-grid');
        if (grid) {
            grid.classList.toggle('list-view', view === 'list');
        }
    }

    function setActiveView(view) {
        viewButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });
    }

    function renderRepositories() {
        if (!moversContainer) return;

        moversContainer.innerHTML = '';

        if (filteredRepos.length === 0) {
            emptyState.style.display = 'block';
            return;
        }

        emptyState.style.display = 'none';

        filteredRepos.forEach((repo, index) => {
            const card = createProjectCard(repo, index);
            moversContainer.appendChild(card);
        });
    }

    function createProjectCard(repo, index) {
        const card = document.createElement('div');
        card.className = 'project-card';
        card.dataset.repoId = repo.id;
        card.style.animationDelay = `${index * 0.1}s`;

        // Accessibility
        card.setAttribute('role', 'button');
        card.setAttribute('aria-label', `Repository ${repo.name}, momentum score ${repo.score.toFixed(1)}. Click for details.`);
        card.tabIndex = 0;

        // Score change indicator
        const scoreChangeHtml = repo.score_change !== undefined ?
            `<div class="score-change ${getScoreChangeClass(repo.score_change)}" 
                  title="Score change: ${repo.score_change > 0 ? '+' : ''}${repo.score_change.toFixed(1)}">
                ${getScoreChangeIcon(repo.score_change)} ${Math.abs(repo.score_change).toFixed(1)}
             </div>` : '';

        // Trend visualization
        const sparklineHtml = repo.trend && repo.trend.length > 0 ?
            `<div class="sparkline-container">
                <div class="trend-indicator">
                    ${createTrendVisualization(repo.trend)}
                </div>
             </div>` : '';

        card.innerHTML = `
            <div class="card-header">
                <h3>
                    <a href="${repo.repo_url || `https://github.com/${repo.full_name}`}" target="_blank" 
                       aria-label="Visit ${repo.name} on GitHub">${repo.name}</a>
                </h3>
                <div class="score-container">
                    <div class="momentum-score ${getScoreClass(repo.score)}" title="Momentum score: ${repo.score.toFixed(1)}">
                        ${repo.score.toFixed(1)}
                    </div>
                    ${scoreChangeHtml}
                </div>
            </div>
            ${sparklineHtml}
            <p class="project-description">${getProjectDescription(repo)}</p>
            <div class="project-stats">
                ${getProjectStats(repo)}
            </div>
        `;

        // Event listeners
        card.addEventListener('click', (e) => {
            // Don't trigger modal if clicking on the repo link
            if (e.target.tagName === 'A') return;
            showModal(repo);
        });
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                showModal(repo);
            }
        });

        return card;
    }

    function getProjectStats(repo) {
        // Extract metrics from the repo object
        const metrics = repo.metrics || {};
        const stars = repo.stars || metrics.stars || 0;
        const forks = repo.forks || metrics.forks || 0;
        const starsGained = metrics.stars_gained_14d || 0;
        const commitsRecent = metrics.commits_14d || 0;
        const contributors = metrics.contributors_30d || 0;

        // Format numbers for display
        const formatNumber = (num) => {
            if (num >= 1000) {
                return (num / 1000).toFixed(1) + 'k';
            }
            return num.toString();
        };

        // Create stat items
        return `
            <div class="stat-item" title="Total stars">
                <i class="stat-icon">★</i>
                <span class="stat-value">${formatNumber(stars)}</span>
            </div>
            ${starsGained > 0 ? `
            <div class="stat-item trend-positive" title="Stars gained in last 14 days">
                <i class="stat-icon">↗</i>
                <span class="stat-value">+${formatNumber(starsGained)}</span>
            </div>
            ` : ''}
            <div class="stat-item" title="Total forks">
                <i class="stat-icon">⑂</i>
                <span class="stat-value">${formatNumber(forks)}</span>
            </div>
            ${commitsRecent > 0 ? `
            <div class="stat-item" title="Commits in last 14 days">
                <i class="stat-icon">⚡</i>
                <span class="stat-value">${formatNumber(commitsRecent)}</span>
            </div>
            ` : ''}
            ${contributors > 0 ? `
            <div class="stat-item" title="Active contributors">
                <i class="stat-icon">👥</i>
                <span class="stat-value">${formatNumber(contributors)}</span>
            </div>
            ` : ''}
        `;
    }

    function getScoreChangeClass(change) {
        if (change > 0) return 'positive-change';
        if (change < 0) return 'negative-change';
        return 'neutral-change';
    }

    function getScoreChangeIcon(change) {
        if (change > 0) return '↗';
        if (change < 0) return '↘';
        return '→';
    }

    function getScoreClass(score) {
        if (score >= 7) return 'score-excellent';
        if (score >= 5) return 'score-good';
        if (score >= 3) return 'score-moderate';
        if (score >= 1) return 'score-low';
        return 'score-minimal';
    }

    function createTrendVisualization(trend) {
        if (!trend || trend.length < 2) return '';

        // Create SVG sparkline for better visual appeal
        const values = trend.map(v => parseFloat(v) || 0);
        const max = Math.max(...values);
        const min = Math.min(...values);
        const range = max - min || 1;

        const points = values.map((value, index) => {
            const x = (index / (values.length - 1)) * 100;
            const y = 100 - ((value - min) / range) * 100;
            return `${x},${y}`;
        }).join(' ');

        // Determine overall trend
        const firstValue = values[0];
        const lastValue = values[values.length - 1];
        const trendClass = lastValue > firstValue ? 'positive' :
            lastValue < firstValue ? 'negative' : 'neutral';
        const trendIcon = lastValue > firstValue ? '↗' :
            lastValue < firstValue ? '↘' : '→';

        const uniqueId = Math.random().toString(36).substr(2, 9);

        return `
            <div class="sparkline-wrapper">
                <svg class="sparkline" viewBox="0 0 100 100" preserveAspectRatio="none" 
                     role="img" aria-label="Trend: ${firstValue} to ${lastValue}">
                    <defs>
                        <linearGradient id="sparkline-gradient-${uniqueId}" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" style="stop-color:var(--accent);stop-opacity:0.6" />
                            <stop offset="100%" style="stop-color:var(--success);stop-opacity:0.8" />
                        </linearGradient>
                    </defs>
                    <polyline points="${points}" fill="none" 
                              stroke="url(#sparkline-gradient-${uniqueId})" 
                              stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
                    <circle cx="${points.split(' ').pop().split(',')[0]}" 
                            cy="${points.split(' ').pop().split(',')[1]}" 
                            r="2" fill="var(--accent)" opacity="0.9" />
                </svg>
                <span class="trend-summary trend-${trendClass}" 
                      title="Trend: ${firstValue} → ${lastValue}">
                    ${trendIcon} ${lastValue}
                </span>
            </div>
        `;
    }

    function showModal(repo) {
        if (!modal || !modalBody) return;

        // Update modal title
        const modalTitle = document.getElementById('modal-title');
        if (modalTitle) {
            modalTitle.textContent = repo.name;
        }

        // Create modal content
        const content = createModalContent(repo);
        modalBody.innerHTML = content;

        // Show modal
        modal.classList.add('active');
        modal.style.display = 'flex';

        // Focus management
        modalClose?.focus();

        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }

    function createModalContent(repo) {
        const metrics = repo.metrics || {};
        const signals = repo.signals || {};
        const scoreDetails = repo.score_details || {};

        return `
            <div class="modal-repo-header">
                <h3><a href="${repo.repo_url || `https://github.com/${repo.full_name}`}" target="_blank">${repo.name}</a></h3>
                <div class="modal-score">
                    <span class="score-value">${repo.score.toFixed(1)}</span>
                    <span class="score-label">Momentum Score</span>
                </div>
            </div>
            
            ${repo.description ? `
            <div class="modal-section">
                <h4>Description</h4>
                <p>${repo.description}</p>
            </div>
            ` : ''}
            
            <div class="modal-section">
                <h4>What Makes This Interesting</h4>
                <p>${generateMomentumSummary(repo)}</p>
            </div>
            
            <div class="modal-section">
                <h4>Key Metrics</h4>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-header">Stars</div>
                        <div class="metric-value">${metrics.stars || repo.stars || 0}</div>
                        <div class="metric-detail">+${metrics.stars_gained_14d || 0} in 14 days</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-header">Forks</div>
                        <div class="metric-value">${metrics.forks || repo.forks || 0}</div>
                        <div class="metric-detail">+${metrics.forks_gained_14d || 0} in 14 days</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-header">Commits</div>
                        <div class="metric-value">${metrics.commits_14d || 0}</div>
                        <div class="metric-detail">in last 14 days</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-header">Contributors</div>
                        <div class="metric-value">${metrics.contributors_30d || 0}</div>
                        <div class="metric-detail">active in 30 days</div>
                    </div>
                </div>
            </div>
            
            ${scoreDetails && Object.keys(scoreDetails).length > 0 ? `
            <div class="modal-section">
                <h4>Score Breakdown</h4>
                <div class="score-breakdown">
                    ${scoreDetails.commit_surge ? `
                    <div class="score-factor">
                        <div class="factor-name">Commit Surge</div>
                        <div class="factor-value">${scoreDetails.commit_surge}/3</div>
                    </div>` : ''}
                    ${scoreDetails.star_velocity ? `
                    <div class="score-factor">
                        <div class="factor-name">Star Velocity</div>
                        <div class="factor-value">${scoreDetails.star_velocity}/3</div>
                    </div>` : ''}
                    ${scoreDetails.team_traction ? `
                    <div class="score-factor">
                        <div class="factor-name">Team Traction</div>
                        <div class="factor-value">${scoreDetails.team_traction}/2</div>
                    </div>` : ''}
                    ${scoreDetails.dev_ecosystem_fit ? `
                    <div class="score-factor">
                        <div class="factor-name">Dev Ecosystem Fit</div>
                        <div class="factor-value">${scoreDetails.dev_ecosystem_fit}/2</div>
                    </div>` : ''}
                </div>
            </div>
            ` : ''}
            
            ${Object.keys(signals).length > 0 ? `
            <div class="modal-section">
                <h4>Momentum Signals</h4>
                <div class="signals-grid">
                    ${Object.entries(signals)
                    .filter(([key, value]) => value > 0)
                    .sort(([, a], [, b]) => b - a)
                    .map(([key, value]) => `
                        <div class="signal-item">
                            <span class="signal-label">${getSignalDisplayName(key)}</span>
                            <div class="signal-bar">
                                <div class="signal-fill" style="width: ${Math.round(value * 100)}%"></div>
                                <span class="signal-value">${Math.round(value * 100)}%</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
            
            <div class="modal-actions">
                <a href="${repo.repo_url}" target="_blank" class="btn-primary">
                    View on GitHub
                </a>
            </div>
        `;
    }

    function formatMetricName(key) {
        // Convert snake_case to Title Case with spaces
        return key
            .replace(/_/g, ' ')
            .replace(/(\w)(\w*)/g, (g0, g1, g2) => g1.toUpperCase() + g2.toLowerCase());
    }

    function closeModal() {
        if (modal) {
            modal.classList.remove('active');
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }

    function handleKeyboard(e) {
        // ESC to close modal
        if (e.key === 'Escape' && modal?.classList.contains('active')) {
            closeModal();
        }

        // R to refresh (Ctrl/Cmd + R for normal refresh)
        if (e.key === 'r' && !e.ctrlKey && !e.metaKey) {
            e.preventDefault();
            handleRefresh();
        }
    }

    async function handleRefresh() {
        if (isLoading) return;

        // Add loading state to refresh button
        refreshBtn?.classList.add('loading');

        try {
            await fetchData();
        } finally {
            refreshBtn?.classList.remove('loading');
        }
    }

    function showLoadingState() {
        if (moversContainer) {
            moversContainer.innerHTML = `
                <div class="loading-state">
                    <div class="loading-spinner"></div>
                    <h3>Loading momentum signals...</h3>
                    <p>Analyzing repository data and computing scores</p>
                </div>
            `;
        }
    }

    function showSkeletonLoading() {
        if (moversContainer) {
            const skeletonCards = Array.from({ length: 6 }, (_, i) => `
                <div class="skeleton-card loading-skeleton">
                    <div class="skeleton-title loading-skeleton"></div>
                    <div class="skeleton-text loading-skeleton"></div>
                    <div class="skeleton-text loading-skeleton"></div>
                    <div class="skeleton-text loading-skeleton"></div>
                </div>
            `).join('');

            moversContainer.innerHTML = skeletonCards;
        }
    }

    function addLoadingStates() {
        // Add loading class to refresh button
        refreshBtn?.classList.add('loading');

        // Add subtle pulse to nav
        stickyNav?.classList.add('loading-pulse');
    }

    function removeLoadingStates() {
        refreshBtn?.classList.remove('loading');
        stickyNav?.classList.remove('loading-pulse');
    }

    function hideLoadingScreen() {
        // Remove element with id 'loading-indicator' if it exists
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
        
        // Also handle the existing loading-screen element for backward compatibility
        if (loadingScreen) {
            loadingScreen.classList.add('hidden');
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 300);
        }
    }

    // Safe call wrapper for hideLoadingScreen
    function safeHideLoadingScreen() {
        try {
            if (typeof hideLoadingScreen === 'function') {
                hideLoadingScreen();
            }
        } catch (error) {
            console.warn('hideLoadingScreen failed:', error);
        }
    }

    // Enhanced intersection observer for better performance
    function setupAdvancedObserver() {
        // Lazy load images and animations
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                }
            });
        }, { threshold: 0.1 });

        // Observe all images with data-src
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });

        // Add staggered animations to cards
        const cardObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.classList.add('animate-in');
                    }, index * 100);
                    cardObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });

        // Observe project cards for staggered animation
        document.querySelectorAll('.project-card').forEach(card => {
            cardObserver.observe(card);
        });
    }

    // Enhanced error handling with retry mechanism
    function createRetryMechanism(operation, maxRetries = 3, delay = 1000) {
        return async function retryWrapper(...args) {
            for (let attempt = 1; attempt <= maxRetries; attempt++) {
                try {
                    return await operation(...args);
                } catch (error) {
                    if (attempt === maxRetries) {
                        throw error;
                    }

                    console.log(`Attempt ${attempt} failed, retrying in ${delay}ms...`);
                    await new Promise(resolve => setTimeout(resolve, delay * attempt));
                }
            }
        };
    }

    // Prefetch next likely actions
    function prefetchResources() {
        // Prefetch about page
        const aboutLink = document.createElement('link');
        aboutLink.rel = 'prefetch';
        aboutLink.href = 'about.html';
        document.head.appendChild(aboutLink);

        // Prefetch GitHub links for top repositories
        const topRepos = filteredRepos.slice(0, 3);
        topRepos.forEach(repo => {
            if (repo.repo_url) {
                const link = document.createElement('link');
                link.rel = 'dns-prefetch';
                link.href = new URL(repo.repo_url).origin;
                document.head.appendChild(link);
            }
        });
    }

    // Enhanced accessibility
    function setupAccessibility() {
        // Announce dynamic content changes
        const announcer = document.createElement('div');
        announcer.setAttribute('aria-live', 'polite');
        announcer.setAttribute('aria-atomic', 'true');
        announcer.className = 'sr-only';
        document.body.appendChild(announcer);

        window.announceToScreenReader = (message) => {
            announcer.textContent = message;
            setTimeout(() => announcer.textContent = '', 1000);
        };

        // Enhanced keyboard navigation
        document.addEventListener('keydown', (e) => {
            // Quick search with /
            if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey) {
                e.preventDefault();
                // Focus first filter button
                filterButtons[0]?.focus();
            }

            // Navigate cards with arrow keys
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                const cards = Array.from(document.querySelectorAll('.project-card'));
                const focusedCard = document.activeElement.closest('.project-card');

                if (focusedCard) {
                    e.preventDefault();
                    const currentIndex = cards.indexOf(focusedCard);
                    const nextIndex = e.key === 'ArrowDown'
                        ? Math.min(currentIndex + 1, cards.length - 1)
                        : Math.max(currentIndex - 1, 0);

                    cards[nextIndex]?.focus();
                }
            }
        });
    }

    // Add scroll to top functionality
    function setupScrollToTop() {
        const scrollBtn = document.createElement('button');
        scrollBtn.className = 'scroll-to-top';
        scrollBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 15l-6-6-6 6"/>
            </svg>
        `;
        scrollBtn.setAttribute('aria-label', 'Scroll to top');
        scrollBtn.style.display = 'none';
        document.body.appendChild(scrollBtn);

        let isVisible = false;
        const toggleVisibility = () => {
            const shouldShow = window.pageYOffset > 300;
            if (shouldShow !== isVisible) {
                isVisible = shouldShow;
                scrollBtn.style.display = isVisible ? 'flex' : 'none';
                scrollBtn.classList.toggle('visible', isVisible);
            }
        };

        const scrollToTop = () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        };

        window.addEventListener('scroll', debounce(toggleVisibility, 100));
        scrollBtn.addEventListener('click', scrollToTop);
    }

    // Utility functions
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log(`Page load time: ${perfData.loadEventEnd - perfData.loadEventStart}ms`);
        });
    }

    function generateMomentumSummary(repo) {
        const signals = repo.signals || {};
        const metrics = repo.metrics || {};
        const scoreDetails = repo.score_details || {};
        const score = repo.score || 0;

        let summary = [];

        // Use why_matters if available
        if (repo.why_matters) {
            return repo.why_matters;
        }

        // Score interpretation
        if (score >= 8) {
            summary.push("🚀 **Exceptional momentum** - This project is experiencing breakthrough growth");
        } else if (score >= 6) {
            summary.push("📈 **Strong momentum** - Growing rapidly with solid fundamentals");
        } else if (score >= 4) {
            summary.push("⚡ **Building momentum** - Showing promising early signals");
        } else {
            summary.push("🌱 **Early stage** - Recently discovered with potential");
        }

        // Highlight top signals
        const topSignals = Object.entries(signals)
            .filter(([key, value]) => value > 0.6)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 3);

        if (topSignals.length > 0) {
            const signalDescriptions = topSignals.map(([key, value]) => {
                const percentage = Math.round(value * 100);
                switch (key) {
                    case 'star_velocity': return `gaining stars rapidly (${percentage}% velocity)`;
                    case 'fork_velocity': return `high fork activity (${percentage}% velocity)`;
                    case 'contributor_growth': return `attracting new contributors (${percentage}% growth)`;
                    case 'commit_frequency': return `very active development (${percentage}% frequency)`;
                    case 'issue_resolution_rate': return `responsive maintainers (${percentage}% resolution rate)`;
                    case 'novelty_signal': return `innovative technology (${percentage}% novelty)`;
                    case 'founder_signal': return `strong founding team (${percentage}% founder signal)`;
                    case 'documentation_quality': return `excellent documentation (${percentage}% quality)`;
                    default: return `${key.replace(/_/g, ' ')} (${percentage}%)`;
                }
            });

            summary.push(`Key strengths: ${signalDescriptions.join(', ')}.`);
        }

        // Add specific metrics insights
        if (metrics.stars_gained_14d > 50) {
            summary.push(`Recently gained ${metrics.stars_gained_14d} stars in 2 weeks.`);
        }
        if (metrics.contributors_30d > 5) {
            summary.push(`Active community with ${metrics.contributors_30d} contributors in the last month.`);
        }
        if (metrics.commits_14d > 20) {
            summary.push(`High development activity with ${metrics.commits_14d} commits in 2 weeks.`);
        }

        return summary.join(' ');
    }

    function getSignalDisplayName(key) {
        const signalNames = {
            'star_velocity': '⭐ Star Growth',
            'fork_velocity': '🍴 Fork Activity',
            'contributor_growth': '👥 Contributor Growth',
            'commit_frequency': '📝 Development Activity',
            'issue_resolution_rate': '🔧 Issue Response',
            'novelty_signal': '💡 Innovation Level',
            'founder_signal': '👑 Team Quality',
            'documentation_quality': '📚 Documentation'
        };
        return signalNames[key] || formatMetricName(key);
    }

    // Page load time monitoring
    function setupPageLoadTimeMonitoring() {
        if ('performance' in window) {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    if (perfData) {
                        const loadTime = Math.round(perfData.loadEventEnd - perfData.navigationStart);
                        console.log(`Page load time: ${loadTime}ms`);
                        
                        // Display load time on page
                        displayPageLoadTime(loadTime);
                    }
                }, 100);
            });
        }
    }

    function displayPageLoadTime(loadTime) {
        // Create load time indicator
        let loadTimeElement = document.getElementById('page-load-time');
        if (!loadTimeElement) {
            loadTimeElement = document.createElement('div');
            loadTimeElement.id = 'page-load-time';
            loadTimeElement.className = 'load-time-indicator';
            loadTimeElement.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 1000;
                opacity: 0.7;
            `;
            document.body.appendChild(loadTimeElement);
        }
        
        loadTimeElement.textContent = `Load time: ${loadTime}ms`;
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (loadTimeElement && loadTimeElement.parentNode) {
                loadTimeElement.style.opacity = '0';
                loadTimeElement.style.transition = 'opacity 0.5s';
                setTimeout(() => {
                    if (loadTimeElement && loadTimeElement.parentNode) {
                        loadTimeElement.remove();
                    }
                }, 500);
            }
        }, 5000);
    }

    // Initialize page load monitoring
    setupPageLoadTimeMonitoring();

    setupScrollToTop();
});
