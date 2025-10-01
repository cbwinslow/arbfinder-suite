# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2024-10-01

### Added
- Interactive TUI mode with Rich library for beautiful terminal output
- Progress bars and colored output for better UX
- Watch mode for continuous monitoring of deals
- Configuration file support (JSON)
- Enhanced API with search and filtering endpoints
- Statistics and analytics dashboard
- Comparable prices viewer page in frontend
- Modern responsive UI with Tailwind CSS
- Navigation between pages
- Loading states and animations
- Verbose and quiet modes
- Database utility functions (backup, vacuum, inspect)
- Quick start guide (QUICKSTART.md)
- Contributing guide (CONTRIBUTING.md)
- CI/CD workflow with GitHub Actions
- Helper scripts (start.sh)

### Enhanced
- API now supports pagination for listings
- Search functionality for listings and comps
- Better error handling throughout
- Improved logging with Rich formatting
- Enhanced CLI help text
- Updated README with comprehensive documentation
- Frontend UI with gradient styling and cards

### Changed
- CLI now supports optional query for interactive mode
- run_arbfinder returns results instead of exit code
- Better separation of concerns in modules

### Fixed
- Improved type hints coverage
- Better input validation in API endpoints

## [0.2.0] - 2024-09-15

### Added
- FastAPI backend for listings management
- Next.js frontend for viewing deals
- Stripe payment integration
- Manual import from CSV/JSON
- Multiple marketplace providers
- Database persistence with SQLite
- CrewAI configuration

### Enhanced
- Async HTTP client with retry logic
- Rate limiting and politeness
- Similar title matching with fuzzy search

## [0.1.0] - 2024-09-01

### Added
- Initial release
- eBay sold comps provider
- ShopGoodwill live listings provider
- GovDeals live listings provider
- GovernmentSurplus live listings provider
- Basic CLI interface
- CSV/JSON export functionality
- Comparable price computation
- Discount calculation

[0.3.0]: https://github.com/cbwinslow/arbfinder-suite/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/cbwinslow/arbfinder-suite/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/cbwinslow/arbfinder-suite/releases/tag/v0.1.0
