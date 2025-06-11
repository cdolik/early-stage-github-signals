/**
 * Early Stage GitHub Signals Dashboard
 * Investor-Grade Dashboard for displaying promising early-stage repositories
 * Version 2.1 - UX Optimized
 */

document.addEventListener('DOMContentLoaded', () => {
    const moversContainer = document.getElementById('movers');
    const searchInput = document.getElementById('searchInput');
    const emptyState = document.getElementById('emptyState');
    let allRepos = [];

    async function fetchData() {
        try {
            const res = await fetch('api/venture-report.json');
            const data = await res.json();
            allRepos = data.repositories || [];
            renderRepos(allRepos);
            // Set metrics
            document.getElementById('qualifiedRepos').textContent = allRepos.length;
            const scores = allRepos.map(r => r.score).sort((a, b) => a - b);
            let median = '-';
            if (scores.length) {
                const mid = Math.floor(scores.length / 2);
                median = scores.length % 2 ? scores[mid] : ((scores[mid - 1] + scores[mid]) / 2).toFixed(1);
            }
            document.getElementById('medianScore').textContent = median;
            // Set date
            if (data.date_generated) {
                document.getElementById('report-date').textContent = new Date(data.date_generated).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
            }
            document.getElementById('current-year').textContent = new Date().getFullYear();
        } catch (e) {
            moversContainer.innerHTML = '<p style="color:red">Failed to load data.</p>';
        }
    }

    function buildCard(r) {
        const card = document.createElement('div');
        card.className = 'project-card';
        card.innerHTML = `
      <div class="card-header">
        <h3><a href="${r.repo_url || '#'}" target="_blank">${r.name || 'N/A'}</a></h3>
        <span class="venture-score">${r.score !== undefined ? r.score.toFixed(1) : '-'}</span>
      </div>
      <p class="description">${r.description || ''}</p>
    `;
        return card;
    }

    function renderRepos(repos) {
        moversContainer.innerHTML = '';
        const top = repos.slice(0, 5);
        top.forEach(r => moversContainer.appendChild(buildCard(r)));
        emptyState.style.display = top.length ? 'none' : 'block';
    }

    searchInput.addEventListener('input', e => {
        const q = e.target.value.toLowerCase();
        const filtered = allRepos.filter(r =>
            r.name.toLowerCase().includes(q) ||
            (r.description || '').toLowerCase().includes(q)
        );
        renderRepos(filtered);
    });

    fetchData();
});
