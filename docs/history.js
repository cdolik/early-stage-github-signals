/**
 * History.js - Handles historical trend data for GitHub Signals
 * Loads past snapshot files and builds in-memory trends
 */

class SignalsHistory {
    constructor() {
        this.trendMap = {};
        this.snapshotDates = [];
        this.dataDir = './data/';
    }

    /**
     * Initialize history by loading the last 3 snapshots
     */
    async init() {
        try {
            // Get current date in YYYY-MM-DD format
            const today = new Date();
            const formatDate = (date) => {
                return date.toISOString().split('T')[0];
            };

            // Generate dates for the past 3 weeks
            const dates = [];
            for (let i = 0; i < 3; i++) {
                const date = new Date(today);
                date.setDate(date.getDate() - (i * 7)); // Go back i weeks
                dates.push(formatDate(date));
            }

            // Store dates for reference
            this.snapshotDates = dates;

            // Load snapshot data
            const snapshots = await Promise.all(
                dates.map(async (date) => {
                    try {
                        // Determine base URL path for GitHub Pages compatibility
                        const basePath = location.hostname === 'cdolik.github.io' ? '/early-stage-github-signals/' : '/';
                        const dataPath = `${basePath}${this.dataDir}${date}.json`.replace('//', '/');
                        
                        console.log(`Fetching historical data from: ${dataPath}`);
                        const response = await fetch(dataPath);
                        if (response.ok) {
                            return { date, data: await response.json() };
                        }
                        console.log(`No snapshot for ${date}`);
                        return { date, data: null };
                    } catch (err) {
                        console.log(`Error loading snapshot for ${date}:`, err);
                        return { date, data: null };
                    }
                })
            );

            // Build trend map
            this.buildTrendMap(snapshots.filter(s => s.data !== null));
            
            console.log(`Loaded ${Object.keys(this.trendMap).length} historical trends`);
            
            return this.trendMap;
        } catch (error) {
            console.error('Failed to initialize history:', error);
            return {};
        }
    }

    /**
     * Build in-memory map of repository trends
     */
    buildTrendMap(snapshots) {
        // Initialize map
        this.trendMap = {};
        
        // Process each snapshot
        snapshots.forEach((snapshot, index) => {
            const { date, data } = snapshot;
            
            if (!data) return;
            
            data.forEach(repo => {
                const fullName = repo.full_name;
                
                if (!this.trendMap[fullName]) {
                    this.trendMap[fullName] = {
                        scores: Array(3).fill(null), // Placeholder for up to 3 scores
                        dates: Array(3).fill(null)   // Corresponding dates
                    };
                }
                
                // Add score at the correct position (based on index)
                this.trendMap[fullName].scores[index] = repo.score;
                this.trendMap[fullName].dates[index] = date;
            });
        });
    }

    /**
     * Get trend data for a specific repository
     * @param {string} repoFullName - The full name of the repository
     * @returns {Array|null} - Array of scores or null if no trend data exists
     */
    getTrend(repoFullName) {
        if (!this.trendMap[repoFullName]) {
            return null;
        }
        
        return this.trendMap[repoFullName].scores.filter(score => score !== null);
    }

    /**
     * Get trend data for multiple repositories
     * @param {Array} repos - Array of repository objects
     * @returns {Object} - Object with repository full_name as keys and trend arrays as values
     */
    getTrendsForRepositories(repos) {
        const trends = {};
        
        repos.forEach(repo => {
            const trend = this.getTrend(repo.full_name);
            if (trend && trend.length > 0) {
                trends[repo.full_name] = trend;
            }
        });
        
        return trends;
    }
}

// Export for use in dashboard.js
window.SignalsHistory = SignalsHistory;
