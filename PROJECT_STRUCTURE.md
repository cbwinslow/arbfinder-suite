# Project Structure Guide

This document explains the organization of the ArbFinder Suite repository.

## 📁 Repository Organization

The repository follows a standardized structure with clear separation of concerns:

### Root Directory

Essential project files only:

```
arbfinder-suite/
├── README.md              # Main project documentation
├── CHANGELOG.md           # Version history and changes
├── CONTRIBUTING.md        # Contribution guidelines
├── CODE_OF_CONDUCT.md     # Community standards
├── SECURITY.md            # Security policy and reporting
├── SUPPORT.md             # Getting help and support
├── Makefile               # Common development tasks
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Multi-container orchestration
├── pyproject.toml         # Python project configuration
├── .gitignore             # Git ignore rules
└── .env.example           # Environment variables template
```

### Documentation (`docs/`)

All project documentation is organized by topic:

```
docs/
├── README.md              # Documentation index
├── getting-started/       # Quick starts and installation guides
├── guides/                # User guides and tutorials
├── architecture/          # Design and implementation docs
├── development/           # Developer guides and workflows
├── platform/              # Deployment and infrastructure
├── tui/                   # Terminal UI documentation
└── api/                   # API documentation (future)
```

See [docs/README.md](docs/README.md) for the complete documentation index.

### Source Code

#### Backend (`backend/`)

Python backend with FastAPI, crawlers, and AI agents:

```
backend/
├── arb_finder.py          # Core arbitrage finder
├── cli.py                 # Enhanced CLI
├── tui.py                 # Rich terminal UI components
├── config.py              # Configuration management
├── utils.py               # Database utilities
├── watch.py               # Continuous monitoring
├── agents/                # AI agents (CrewAI)
├── api/                   # FastAPI REST API
├── crawler/               # Web crawlers
├── openrouter/            # OpenRouter AI integration
├── site_investigator/     # Site analysis tools
└── storage/               # Storage utilities
```

#### Frontend (`frontend/`)

Next.js frontend with TypeScript and Tailwind CSS:

```
frontend/
├── app/                   # Next.js app directory
│   ├── page.tsx           # Main page
│   ├── layout.tsx         # App layout
│   └── comps/             # Comparables page
├── components/            # Reusable React components
└── public/                # Static assets
```

#### TUI (`tui/`)

Go-based Bubbletea terminal user interface:

```
tui/
├── main.go                # Entry point
├── database.go            # Database layer
├── api_client.go          # API client
├── search_pane.go         # Search interface
├── results_pane.go        # Results display
├── stats_pane.go          # Statistics view
├── config_pane.go         # Configuration UI
└── README.md              # Redirect to docs/tui/
```

#### Packages (`packages/`)

TypeScript/Node.js packages:

```
packages/
├── client/                # TypeScript SDK
│   ├── src/
│   └── README.md
└── cli/                   # TypeScript CLI
    ├── src/
    └── README.md
```

### Infrastructure and Deployment

#### Cloudflare (`cloudflare/`)

Cloudflare Workers and edge compute:

```
cloudflare/
└── src/                   # Worker source code
```

#### Infrastructure (`infrastructure/`)

Infrastructure as Code with Pulumi:

```
infrastructure/
├── pulumi/                # Pulumi configurations
└── README.md              # Redirect to docs/platform/INFRASTRUCTURE.md
```

#### Database (`database/`)

Database schemas and migrations:

```
database/
├── migrations/            # Database migration scripts
└── schemas/               # Database schema definitions
```

### Supporting Files

#### Scripts (`scripts/`)

Utility and automation scripts:

```
scripts/
├── cloudflare/            # Cloudflare deployment scripts
├── ai_code_analyzer.py    # Code analysis
├── ai_test_generator.py   # Test generation
├── crewai_dev_crew.py     # AI development crew
└── README.md              # Redirect to docs/development/SCRIPTS.md
```

#### Tests (`tests/`)

Test suite:

```
tests/
├── test_cli.py            # CLI tests
└── test_config.py         # Configuration tests
```

#### Configuration (`config/`)

Configuration templates and examples:

```
config/
└── (configuration files)
```

#### Examples (`examples/`)

Example scripts and usage patterns:

```
examples/
└── shopgoodwill_analysis.py
```

#### Crew (`crew/`)

CrewAI agent configurations:

```
crew/
└── crewai.yaml
```

#### Exporters (`exporters/`)

Export templates:

```
exporters/
└── fb_marketplace_template.csv
```

### GitHub Configuration (`.github/`)

GitHub-specific configurations:

```
.github/
├── workflows/             # GitHub Actions workflows
│   └── README.md          # Redirect to docs/development/WORKFLOWS.md
├── ISSUE_TEMPLATE/        # Issue templates
├── DISCUSSION_TEMPLATE/   # Discussion templates
├── PULL_REQUEST_TEMPLATE.md
├── copilot-instructions.md
└── (other GitHub configs)
```

## 🗺️ Navigation Guide

### For Users

- **Getting Started**: [docs/getting-started/QUICKSTART.md](docs/getting-started/QUICKSTART.md)
- **Features**: [docs/guides/FEATURES_OVERVIEW.md](docs/guides/FEATURES_OVERVIEW.md)
- **Support**: [SUPPORT.md](SUPPORT.md)

### For Developers

- **Development Setup**: [docs/development/DEVELOPER.md](docs/development/DEVELOPER.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Architecture**: [docs/architecture/IMPLEMENTATION_GUIDE.md](docs/architecture/IMPLEMENTATION_GUIDE.md)

### For Deployment

- **Platform Guide**: [docs/platform/PLATFORM_GUIDE.md](docs/platform/PLATFORM_GUIDE.md)
- **Cloudflare Setup**: [docs/platform/CLOUDFLARE_SETUP.md](docs/platform/CLOUDFLARE_SETUP.md)
- **Infrastructure**: [docs/platform/INFRASTRUCTURE.md](docs/platform/INFRASTRUCTURE.md)

## 📝 Documentation Standards

All documentation follows these principles:

1. **Organized by Topic**: Related docs are grouped together
2. **Clear Hierarchy**: Subdirectories for different categories
3. **Comprehensive Index**: [docs/README.md](docs/README.md) lists all documentation
4. **Cross-linking**: Documents link to related content
5. **Up-to-date**: Maintained alongside code changes

## 🔄 Maintenance

When adding new documentation:

1. Place it in the appropriate `docs/` subdirectory
2. Update [docs/README.md](docs/README.md) to include the new file
3. Add cross-references from related documents
4. Keep the main [README.md](README.md) focused on essentials

When adding new code:

1. Place it in the appropriate source directory
2. Follow existing naming conventions
3. Update relevant documentation
4. Add tests in the `tests/` directory

## 📋 Quick Reference

| Need to... | Look in... |
|------------|------------|
| Understand what the project does | [README.md](README.md) |
| Get started quickly | [docs/getting-started/](docs/getting-started/) |
| Learn how to use features | [docs/guides/](docs/guides/) |
| Understand the architecture | [docs/architecture/](docs/architecture/) |
| Contribute code | [docs/development/](docs/development/) |
| Deploy to production | [docs/platform/](docs/platform/) |
| Get help | [SUPPORT.md](SUPPORT.md) |
| Report a bug | [GitHub Issues](https://github.com/cbwinslow/arbfinder-suite/issues) |

## 🎯 Design Principles

The repository structure follows these principles:

1. **Minimal Root**: Keep root directory clean with only essential files
2. **Organized Docs**: All documentation in `docs/` with clear subdirectories
3. **Source Separation**: Backend, frontend, and TUI in separate directories
4. **Infrastructure as Code**: Deployment configs in dedicated directories
5. **Developer Tools**: Scripts, tests, and tooling clearly separated
6. **README Redirects**: Subdirectories have README files pointing to main docs

This structure makes it easy to:
- Find what you need quickly
- Understand the project organization
- Navigate between related files
- Maintain consistency across the project
- Onboard new contributors

## 🔗 Related Documentation

- [Documentation Index](docs/README.md) - Complete list of all documentation
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Developer Guide](docs/development/DEVELOPER.md) - Development setup and workflow
