# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2024-10-26

### Added - Project Structure & Tooling
- Python package structure with `pyproject.toml` for proper packaging
- Makefile with common development tasks (install, test, lint, format, clean)
- Pre-commit hooks configuration for automated code quality checks
- VS Code workspace settings with debugger configurations
- Docker and Docker Compose support for easy deployment
- Comprehensive `.gitignore` for better artifact management
- Package `__init__.py` files for proper module structure

### Added - Enhanced CLI
- Complete CLI refactor with subcommands:
  - `arbfinder search` - Search for arbitrage opportunities
  - `arbfinder watch` - Continuous monitoring
  - `arbfinder config` - Configuration management (show, init, set, get)
  - `arbfinder db` - Database operations (stats, backup, clean, vacuum)
  - `arbfinder server` - Run API server
  - `arbfinder completion` - Shell completion generation (bash/zsh)
- Global `--version` flag showing proper version information
- Shell completion support for bash and zsh
- Better help text and command organization
- Installed as `arbfinder` command via pip

### Added - TypeScript/Node.js Packages
- `@arbfinder/client` - Official TypeScript/JavaScript API client SDK
  - Full TypeScript types for all API responses
  - Axios-based HTTP client with timeout support
  - Methods for all API endpoints
  - Comprehensive documentation and examples
- `@arbfinder/cli` - TypeScript CLI tool
  - `arbfinder-ts` command with rich terminal output
  - Commands: list, search, stats, info, comps
  - Colored output with chalk
  - Spinner animations with ora
  - Table formatting for results
  - Commander.js for argument parsing

### Added - Testing & Quality
- Comprehensive test suite with pytest
  - Tests for CLI module (11 tests)
  - Tests for config module (5 tests)
  - All tests passing (16/16)
- Test coverage reporting (baseline: 23%)
- pytest configuration in pyproject.toml
- Testing infrastructure for future expansion
- Code coverage HTML reports

### Added - Documentation
- `DEVELOPER.md` - Comprehensive developer guide
  - Architecture overview with diagrams
  - Development setup instructions
  - Testing guidelines
  - Code style standards
  - Debugging tips
  - API development guide
  - CLI development guide
  - Deployment instructions
  - Troubleshooting section
- Enhanced README with:
  - Badges for Python version, license, code style
  - Quick start section
  - Docker usage instructions
  - TypeScript SDK examples
  - Enhanced CLI examples
  - Development section
  - Makefile usage guide
- Package-specific READMEs for TypeScript packages
- Better structured documentation overall

### Added - Developer Tools
- Black configuration for code formatting (line length: 100)
- Flake8 configuration for linting
- mypy configuration for type checking
- pytest configuration with coverage
- Pre-commit hooks for automatic formatting
- Launch configurations for VS Code debugging
- Make targets for common tasks

### Enhanced
- Updated version to 0.4.0 across all files
- Better module organization with proper packages
- Improved import structure
- Enhanced error handling in CLI
- Better code organization and separation of concerns
- Comprehensive inline documentation

### Changed
- CLI now uses subcommand structure instead of single entry point
- Configuration management split into separate subcommands
- Database operations organized under `db` subcommand
- Server startup now a separate `server` subcommand
- Package structure follows Python best practices

### Technical Improvements
- Proper Python packaging with setuptools
- Entry points for CLI commands
- Optional dependencies for dev and test
- Better dependency management
- Cleaner import paths
- Type hints throughout new code

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
