# Changelog

## [Unreleased]

### Added (2025-12-22)
- 📦 **Python Lock Files**: Added `requirements.lock` and `requirements-dev.lock` for reproducible builds
- 📖 **TESTING.md**: Comprehensive testing guide covering Python, TypeScript, and browser tests
- 📖 **DEPLOYMENT.md**: Complete deployment guide for Docker, Cloudflare, and traditional hosting
- ✅ **TypeScript Tests**: 22 passing tests for @arbfinder/client package with full coverage
- ✅ **Frontend Tests**: 10 component tests for Next.js frontend with Jest
- ✅ **Python Tests**: Expanded test suite with test_utils.py and test_cloudflare_client.py
- 🤖 **CI/CD Workflows**: comprehensive-ci.yml with multi-version Python testing (3.9-3.12)
- 🚀 **Deploy Workflow**: deploy-production.yml for automated Cloudflare and Docker deployments
- 🔒 **Security Scanning**: Integrated Trivy security scanner and npm audit
- 📦 **Package Lock Files**: Created lock files for all 4 npm packages (frontend, client, cli, cloudflare)

### Fixed (2025-12-17 - 2025-12-22)
- 🔒 **CVE-2025-12-11**: Upgraded Next.js from 14.2.32 to 14.2.35 (High severity DoS)
- 🔒 **esbuild vulnerabilities**: Upgraded from <=0.24.2 to 0.27.2 (Moderate severity)
- 🐛 **Backend imports**: Fixed import issues in backend/__init__.py
- 🐛 **Cloudflare client**: Implemented real boto3 S3-compatible API (replaced placeholder)
- 🐛 **Config compatibility**: Converted next.config.ts to next.config.mjs for Next.js 14.2.35
- 🐛 **Package references**: Fixed @arbfinder/client local package reference in CLI

### Improved (2025-12-17 - 2025-12-22)
- ♻️ **Code refactoring**: Moved boto3 imports to module level (eliminated anti-pattern)
- ♻️ **DRY principle**: Extracted _get_s3_client() helper method
- 📝 **Go TUI**: Implemented 7 TODO items (stats refresh, config operations, search, results)
- 📝 **Concurrency**: Added documentation for Go goroutine patterns
- 📊 **Coverage**: Integrated Codecov for coverage reporting
- 📖 **README**: Updated installation instructions with lock file usage
- 📖 **README**: Added comprehensive testing and CI/CD section
- 🗂️ **.gitignore**: Added requirements-frozen.txt exclusion

### Technical Details
- **Files changed**: 30+ files
- **Lines added**: 30,000+ lines
- **Tests created**: 57+ automated tests
- **Security fixes**: 3 vulnerabilities addressed
- **Packages locked**: 1,047 total packages

## Previous Releases

- docs: update changelog [skip ci] (07172d7)
- Add comprehensive WORK_SUMMARY.md documenting all deliverables and achievements (ead3d60)
- Add comprehensive IMPLEMENTATION_STRATEGY.md with high-level implementation guide (a937eed)
- Add GitHub configuration files and update README with comprehensive documentation (53f87cf)
- Address code review suggestions: add env var for project URL and update notes (acac679)
- Add complete OpenRouter SDK integration with client, models, completion, streaming, and utilities (c6abaf2)
- Address final review feedback: add timeline note to TASKS.md and fix remaining contact placeholder (77e9cf9)
- Add Cloudflare setup orchestrator script and comprehensive setup guide (0da2eda)
- Fix code review issues: update contact placeholders and PR context refs (d6aa839)
- Add comprehensive documentation: OpenRouter integration, Implementation Guide, Cloudflare setup script (f2b8058)
- Add RULES.md, copilot-instructions.md, and PROMPTS.md documentation (6c50674)
- Add project setup summary for quick reference (cb78d11)
- Add comprehensive GitHub project management structure (d053453)
- Add core documentation files: TASKS.md, SRS.md, AGENTS.md, CLOUDFLARE_SETUP.md, copilot-instructions.md (21b4dc6)
- Add comprehensive documentation: TASKS.md, SRS.md, FEATURES.md, AGENTS.md (a7df94d)
- Initial plan (416aec7)
- Initial plan (4cb0f52)
- Initial plan (0451cb3)
- chore: auto-format code with AI assistance (b835b0a)
- docs: update changelog [skip ci] (2b0d227)
- Clean up build artifacts and update .gitignore (31f818f)
- Add visual features overview and validate code syntax (50fd276)
- Add comprehensive implementation summary for platform features (4c8a23b)
- Add setup script, quickstart guide, and improve .gitignore (c1f60e7)
- Add comprehensive web platform with retro Windows theme, Crawl4AI, CrewAI agents, and cloud storage (64ef0b3)
- Initial plan (000831d)
- docs: update changelog [skip ci] (4ea1bb2)
- Add implementation summary document (b8deefb)
- Add visual mockups and interface documentation (1b0e0cd)
- Add comprehensive architecture documentation for TUI (5650100)
- Add message passing, search integration, tests, and examples for TUI (53077a2)
- Add Bubbletea TUI with multi-pane interface and database integration (8820cf0)
- Initial plan (7e62011)
- chore: auto-format code with AI assistance (7842eb3)
- docs: update changelog [skip ci] (1d5378f)
- Consolidate duplicate tests and improve test generator mock handling (3753197)
- Add implementation summary and update gitignore for AI-generated files (27d00d6)
- Fix code review issues - improve error handling and remove bc dependency (eb1e9ce)
- Add comprehensive CI/CD and AI automation documentation (2855a9b)
- Add AI-powered CI/CD workflows and automation scripts (3eb29ab)
- Initial plan (704f7de)
- docs: update changelog [skip ci] (2b12a0a)
- Add comprehensive GitHub Actions workflows and CI/CD automation (a053c0e)
- Add comprehensive documentation and examples (863d5d7)
- Add comprehensive price analysis system and infrastructure (d4f171e)
- Initial plan (e18a5ce)
- Address code review feedback on improvements summary (d4a95e0)
- Add comprehensive improvements summary for v0.4.0 (b336c46)
- Update README and CHANGELOG for v0.4.0 (5f105a1)
- Add project structure, CLI enhancements, TypeScript packages, and tooling (4f4a237)
- Initial plan (ef7995e)
- Bump next in /frontend in the npm_and_yarn group across 1 directory (7a0f035)
- Fix inconsistent params usage at line 85 in backend/api/main.py (74e9ac1)
- Apply suggestion from @qodo-merge-pro[bot] (24a14eb)
- Add comprehensive improvement summary document (31cab13)
- Add documentation, utilities, CI/CD, and project infrastructure (46b8ba6)
- Add watch mode, config support, comps viewer, and enhanced features (e249f0c)
- Add CLI/TUI improvements with rich library and enhanced API (4064c2a)
- Add files via upload (48277e9)
- Initial plan (a7d42ba)
- Initial commit (a173498)
