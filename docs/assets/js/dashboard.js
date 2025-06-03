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
            this.showCategory('hot');
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
        }
    }

    async loadData() {
        try {
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
                repo.total_score >= 30 && 
                this.isDaysOld(repo.created_at, 7)
            ),
            'vc-ready': this.data.repositories.filter(repo => 
                repo.total_score >= 25 && 
                repo.organization_score >= 8 &&
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

                document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
    }

    showCategory(category) {
        this.currentCategory = category;
        const repos = this.categories[category] || [];
        this.renderRepositories(repos);
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
        card.innerHTML = `
            <h3>${repo.name}</h3>
            <p>${repo.description}</p>
            <p>Score: ${repo.total_score}</p>
        `;
        return card;
    }
}

  new GitHubSignalsDashboard();
});
