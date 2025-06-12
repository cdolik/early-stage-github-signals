# Signal-First Dashboard Folder Structure

This document outlines the organization of files and folders in the Signal-First Dashboard project.

## Directory Structure

```
docs/
├── index.html         # Main dashboard HTML
├── styles.css         # Dashboard styling
├── dashboard.js       # Dashboard functionality
├── about.html         # About page
├── about.md           # About page source
├── CODEBASE_STATUS.md # Development status
├── DASHBOARD_IMPLEMENTATION.md # Dashboard implementation details
├── DEVELOPER_SETUP.md # Setup instructions
├── prompts.md         # Feature prompts
├── roadmap.md         # Project roadmap
├── api/               # API endpoint files
│   ├── latest.json    # Latest data
│   ├── simplified.json # Simplified data format
│   └── README.md      # API documentation
├── assets/            # Static assets
│   ├── logo.png       # Logo image file
│   ├── logo.svg       # Logo vector file
│   ├── css/           # Additional CSS files
│   └── js/            # Additional JavaScript files
└── data/              # Historical data files
    └── _last_week_scores.json # Previous week's scores
```

## File Purposes

### Main Files
- `index.html`: Core dashboard UI with HTML structure
- `styles.css`: All styling for the dashboard, including responsive design
- `dashboard.js`: JavaScript that powers the dashboard functionality

### Data Files
- `/api/latest.json`: Most recent repository data
- `/api/simplified.json`: Simplified data format for faster loading

### Documentation
- `DASHBOARD_IMPLEMENTATION.md`: Details on the dashboard implementation
- `DEVELOPER_SETUP.md`: Instructions for setting up the development environment

## Organization Principles

1. **Separation of Concerns**: HTML structure, CSS styling, and JavaScript functionality are kept in separate files
2. **API Versioning**: All API endpoints are in the `/api` folder for clean organization
3. **Static Assets**: All images, icons, and other static files are in the `/assets` folder
4. **Historical Data**: Previous data snapshots are stored in the `/data` folder

## Disclaimer

This dashboard is not an official GitHub project. It uses public GitHub API data to analyze repository momentum.
