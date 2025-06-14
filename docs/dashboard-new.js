/**
 * Early Stage GitHub Signals Dashboard
 * Enhanced UX Dashboard for displaying promising early-stage repositories
 * Version 5.0 - Professional Grade UX
 */

document.addEventListener('DOMContentLoaded', () => {
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
            await fetchData();
            hideLoadingScreen();
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
            showError('Failed to initialize dashboard');
            hideLoadingScreen();
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
        if (isLoading) return;

        try {
            isLoading = true;
            showLoadingState();

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

                    const res = await fetch(apiPath);
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
            showError(error.message);
        } finally {
            isLoading = false;
        }
    }

    function processData(data) {
        allRepos = (data.repositories || []).map((repo, index) => ({
            ...repo,
            id: repo.id || repo.name || `repo-${index}`,
            score: repo.score || 0,
            name: repo.name || 'Unknown Repository',
            description: repo.description || '',
            why_matters: repo.why_matters || '',
            repo_url: repo.repo_url || repo.url || '#',
            trend: repo.trend || [],
            score_change: repo.score_change
        }));

        // Sort by score
        allRepos.sort((a, b) => b.score - a.score);

        // Set initial filter
        applyFilter(currentFilter);

        // Update date
        if (data.date_generated) {
            const date = new Date(data.date_generated);
            const formattedDate = date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            document.getElementById('report-date').textContent = formattedDate;
        }

        document.getElementById('current-year').textContent = new Date().getFullYear();
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
                    <a href="${repo.repo_url}" target="_blank" 
                       aria-label="Visit ${repo.name} on GitHub">${repo.name}</a>
                </h3>
                <div class="score-container">
                    <div class="momentum-score" title="Momentum score: ${repo.score.toFixed(1)}">
                        ${repo.score.toFixed(1)}
                    </div>
                    ${scoreChangeHtml}
                </div>
            </div>
            ${sparklineHtml}
            <p class="why-matters">${repo.why_matters || repo.description}</p>
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

    function createTrendVisualization(trend) {
        return trend.map((value, index, arr) => {
            if (index === 0) return `<span>${value}</span>`;

            const prev = parseFloat(arr[index - 1]);
            const current = parseFloat(value);
            let className = 'neutral';
            let icon = '→';

            if (current > prev) {
                className = 'positive';
                icon = '↗';
            } else if (current < prev) {
                className = 'negative';
                icon = '↘';
            }

            return `<span class="trend-${className}" title="Previous: ${prev}, Current: ${current}">
                        ${icon} ${value}
                    </span>`;
        }).join(' ');
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

        return `
            <div class="modal-repo-header">
                <h3><a href="${repo.repo_url}" target="_blank">${repo.name}</a></h3>
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
                <h4>Why It Matters</h4>
                <p>${repo.why_matters || 'This repository shows promising momentum signals.'}</p>
            </div>
            
            ${Object.keys(metrics).length > 0 ? `
            <div class="modal-section">
                <h4>Key Metrics</h4>
                <div class="metrics-grid">
                    ${Object.entries(metrics).map(([key, value]) => `
                        <div class="metric-item">
                            <span class="metric-label">${formatMetricName(key)}</span>
                            <span class="metric-value">${value}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
            
            ${Object.keys(signals).length > 0 ? `
            <div class="modal-section">
                <h4>Signal Breakdown</h4>
                <div class="signals-grid">
                    ${Object.entries(signals).map(([key, value]) => `
                        <div class="signal-item">
                            <span class="signal-label">${formatMetricName(key)}</span>
                            <span class="signal-value">${typeof value === 'number' ? value.toFixed(2) : value}</span>
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

    function formatMetricName(name) {
        return name.replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
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
                <div class="loading">
                    <div class="loading-spinner"></div>
                    Loading repositories...
                </div>
            `;
        }
    }

    function showError(message) {
        if (moversContainer) {
            moversContainer.innerHTML = `
                <div class="error-state" role="alert">
                    <h3>Unable to load data</h3>
                    <p>${message}</p>
                    <button class="retry-btn" onclick="location.reload()">
                        Try Again
                    </button>
                </div>
            `;
        }
    }

    function hideLoadingScreen() {
        if (loadingScreen) {
            loadingScreen.classList.add('hidden');
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 300);
        }
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
});
