# Early-Stage GitHub Signals - Codebase Status Report

_Last updated: June 7, 2025 — Snapshot of codebase health before UI/UX redesign and system enhancement phase._

## ✅ What's Working Well

1. **Core Momentum Scoring Engine**
   - 10-point scoring system correctly implements all four criteria 
   - Clear separation between data collection, scoring, and output generation
   - Successfully identifies high-potential repositories with score 7+/10
   - Stable scoring attributes: commit_surge, star_velocity, team_traction, dev_ecosystem_fit

2. **Multi-Source Data Collection**
   - Successfully pulls from GitHub Trending, Product Hunt, and Hacker News
   - Modular collector architecture in `src/collectors/`
   - Skip options in CLI for different sources when needed

3. **Output Generation**
   - Multiple output formats: Markdown reports, JSON API, HTML dashboard
   - Clean dashboard interface in `docs/index.html`
   - JSON API structure follows consistent pattern
   - Historical data maintained in `docs/api/` directory

4. **Automation**
   - GitHub Actions workflow runs weekly
   - Tasks defined in VS Code for local development
   - Basic caching to minimize API calls

## ⚠️ What's Missing or Fragile

1. **Schema Inconsistencies**

   🚨 **Mismatch between `team_traction` (output) vs `new_contributors` (schema) will break validation in production.**
   - Field "new_contributors" is required in repo.schema.json
   - But output JSON uses "team_traction" instead
   ✅ Fix: Rename key in scorer to new_contributors or update schema to match actual implementation.

2. **Testing Infrastructure**
   - **Test Coverage (Est.):** ~35% — functional but limited. Schema and scoring logic lack dedicated unit tests.  
   - **CI Automation:** Weekly report runs via GitHub Actions; no full test suite or coverage badge integrated yet.
   - Missing unit tests for core components (MomentumScorer, APIGenerator) 
   - Integration tests are minimal and don't verify schema compliance

3. **Error Handling**
   - 🚨 **Cache initialization issues can break data collection: `Cache.__init__() got an unexpected keyword argument 'enabled'`**
   - Collector class initialization issues: `GitHubCollector.__init__() takes 1 positional argument but 3 were given`
   - Method name mismatches: `'GitHubCollector' object has no attribute 'collect_trending_repositories'`

4. **Documentation**
   - Developer setup documentation incomplete
   - API schema documentation missing
   - Limited code comments for complex scoring logic
   - Architecture diagram missing

## ❌ Critical Issues to Fix Immediately

1. **Schema Validation Failures**
   - 🚨 Mismatch between `team_traction` (output) vs `new_contributors` (schema) will break validation in production.
   - Fix requires either updating schema or renaming field in MomentumScorer

2. **Cache Implementation Issues**
   - Error logs show Cache initialization failures
   - Fix constructor parameter handling in Cache class

3. **Constructor Inconsistencies**
   - GitHubCollector, HackerNewsCollector, and BaseCollector have initialization errors
   - Standardize constructor signatures across collector classes

4. **Missing API Methods**
   - Some collectors reference non-existent methods like `collect_trending_repositories` and `collect_tech_discussions`
   - Implement missing methods or update method references

## 💡 Suggested Enhancements

1. **Scoring Engine Improvements**
   - Add configurable weights for scoring criteria
   - Implement time-based scoring adjustments
   - Support custom scoring rules for different ecosystems

2. **Data Collection**
   - Add more sources (e.g., Indie Hackers, DEV.to)
   - Implement rate limiting to avoid GitHub API throttling
   - Add detailed collector metrics and logging

3. **Output Generation**
   - Add more visualization options in dashboard
   - Implement trending comparisons between weeks
   - Create email digest feature for subscribers

4. **Infrastructure**
   - Add proper test suite with pytest fixtures
   - Set up coverage reporting in CI
   - Implement validation checks for schema compliance

## 🛠️ Developer Experience

1. **Improve Local Development**
   - Add Docker setup for consistent environment
   - Implement pre-commit hooks for linting/testing
   - Create developer documentation with architecture diagrams
   - Add VSCode debugger configuration

2. **Testing Tools**
   - Implement mock GitHub API responses
   - Create fixture generator for testing
   - Add schema validation tests

3. **CLI Improvements**
   - Add interactive mode for CLI
   - Implement progress indicators for long-running operations
   - Add verbose debug output option
   - Support configuration profiles for different use cases

## 📈 Investor-Facing Opportunities

1. **Enhanced Reporting**
   - Add investment trend analysis
   - Implement category-specific metrics
   - Create founder team analysis based on commit patterns

2. **Dashboard Customization**
   - Allow custom scoring criteria for investor-specific interests
   - Add private dashboard option with extended metrics
   - Implement notification system for high-potential matches

3. **API Enhancements**
   - Create authenticated API access
   - Add more detailed metadata about repositories
   - Implement history tracking for long-term trends

4. **Data Export**
   - Add Excel/CSV export options
   - Provide direct integration with CRM systems
   - Implement custom report generation

## Technical Architecture

- Static site with HTML/CSS dashboard pulling from JSON
- Core loop: Collectors → Momentum Scorer → JSON Generator → Dashboard
- Output path: `docs/api/latest.json`
- Weekly automation via GitHub Actions
- Uses: `argparse`, `typing`, `jsonschema`, `pytest`, `flake8`, `black`, `pre-commit`
