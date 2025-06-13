/**
 * Early Stage GitHub Signals Platform - Dashboard JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  class GitHubSignalsDashboard {
    constructor() {
        this.data = null;
        this.currentCategory = 'hot';
        this.init();
    }

    async init() {
        try {
            await this.loadData();
            this.setupEventListeners();
            this.renderStatistics();
            this.renderChart();
            this.showCategory('hot');
            this.hideLoading();
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
            this.showError();
        }
    }

    async loadData() {
        try {
            // Try to load simplified format first
            try {
                // Determine base URL path for GitHub Pages compatibility
                const basePath = location.hostname === 'cdolik.github.io' ? '/early-stage-github-signals/' : '/';
                const simplifiedPath = `${basePath}api/simplified.json`.replace('//', '/');
                
                console.log(`Fetching simplified data from: ${simplifiedPath}`);
                const simplifiedResponse = await fetch(simplifiedPath);
                if (simplifiedResponse.ok) {
                    const simplifiedData = await simplifiedResponse.json();
                    if (simplifiedData.repositories && simplifiedData.repositories.length > 0) {
                        console.log("Loaded simplified data format");
                        
                        // Convert to our expected format
                        this.data = {
                            repositories: simplifiedData.repositories.map(repo => ({
                                name: repo.name,
                                description: repo.description || '',
                                language: repo.language || 'Unknown',
                                total_score: repo.score,
                                why: repo.why
                            }))
                        };
                        return;
                    }
                }
            } catch (e) {
                console.log("Simplified format not available, falling back to legacy format");
            }
            
            // Fall back to legacy format
            const response = await fetch('./api/latest.json');
            if (!response.ok) throw new Error('Failed to fetch data');
            
            this.data = await response.json();
            this.categorizeRepositories();
        } catch (error) {
            console.error('Error loading data:', error);
            throw error;
        }
    }

    categorizeRepositories() {
        if (!this.data.repositories) return;
        
        this.categories = {
            hot: this.data.repositories.filter(repo => 
                repo.total_score >= 8 && 
                this.isDaysOld(repo.created_at, 7)
            ),
            'vc-ready': this.data.repositories.filter(repo => 
                repo.total_score >= 7 && 
                repo.organization_score >= 2 &&
                (repo.has_website || repo.yc_mention)
            ),
            'ai-ml': this.data.repositories.filter(repo => 
                this.hasKeywords(repo, ['ai', 'ml', 'machine learning', 'artificial intelligence', 'neural', 'deep learning'])
            ),
            fintech: this.data.repositories.filter(repo => 
                this.hasKeywords(repo, ['fintech', 'payment', 'banking', 'crypto', 'blockchain', 'defi', 'finance'])
            ),
            all: this.data.repositories
        };

        // Sort each category by score
        Object.keys(this.categories).forEach(key => {
            this.categories[key].sort((a, b) => b.total_score - a.total_score);
        });
    }

    isDaysOld(dateString, days) {
        const created = new Date(dateString);
        const now = new Date();
        const daysDiff = (now - created) / (1000 * 60 * 60 * 24);
        return daysDiff <= days;
    }

    hasKeywords(repo, keywords) {
        const text = `${repo.description || ''} ${repo.name} ${(repo.topics || []).join(' ')}`.toLowerCase();
        return keywords.some(keyword => text.includes(keyword.toLowerCase()));
    }

    setupEventListeners() {
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const category = e.target.getAttribute('data-category');
                this.showCategory(category);
                
                // Update active tab
                document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
    }

    showCategory(category) {
        this.currentCategory = category;
        const repos = this.categories[category] || [];
        this.renderRepositories(repos);
        this.updateCategoryStats(category, repos.length);
    }

    updateCategoryStats(category, count) {
        const categoryNames = {
            hot: 'Hot This Week',
            'vc-ready': 'VC-Ready',
            'ai-ml': 'AI/ML',
            fintech: 'Fintech',
            all: 'All Startups'
        };
        
        const statsElement = document.querySelector('.stats-grid');
        if (statsElement) {
            statsElement.innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${count}</div>
                    <div class="stat-label">${categoryNames[category]} Repos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${this.data.repositories.length}</div>
                    <div class="stat-label">Total Analyzed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${Math.round(this.data.repositories.reduce((sum, repo) => sum + repo.total_score, 0) / this.data.repositories.length)}</div>
                    <div class="stat-label">Average Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${new Date().toLocaleDateString()}</div>
                    <div class="stat-label">Last Updated</div>
                </div>
            `;
        }
    }

    renderRepositories(repositories) {
        const container = document.getElementById('repositoriesGrid');
        if (!container) return;
        
        container.innerHTML = '';

        if (repositories.length === 0) {
            container.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-secondary);">
                    <h3>No startups found in this category</h3>
                    <p>Try another category or check back later for new discoveries.</p>
                </div>
            `;
            return;
        }

        repositories.forEach(repo => {
            const card = this.createRepositoryCard(repo);
            container.appendChild(card);
        });
    }

    createRepositoryCard(repo) {
        const card = document.createElement('div');
        card.className = 'repository-card';
        
        // Create the why info (signals that contributed to the score)
        const whyInfo = repo.why && repo.why.length ? 
            `<p class="repo-signals">${repo.why.join(', ')}</p>` : '';
            
        card.innerHTML = `
            <h3>${repo.name}</h3>
            <p>${repo.description}</p>
            <p>Score: ${repo.total_score}/10</p>
            ${whyInfo}
        `;
        return card;
    }
}

  new GitHubSignalsDashboard();
});
