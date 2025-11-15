# ArbFinder TUI - Bubbletea Interactive Interface

A powerful terminal user interface (TUI) built with [Bubbletea](https://github.com/charmbracelet/bubbletea) for the ArbFinder Suite. This TUI provides an interactive, multi-pane interface for searching retailers, managing configurations, viewing statistics, and analyzing price data.

## Features

### 🔍 Multi-Pane Interface
- **Search Pane**: Search for arbitrage opportunities across multiple retailers
- **Results Pane**: View and navigate search results with keyboard controls
- **Statistics Pane**: View real-time analytics and price history
- **Configuration Pane**: Save, load, and manage search configurations

### 💾 Data Persistence
- SQLite database for storing search history
- Save and recall search configurations
- Price history tracking and analysis
- Cached listings for offline viewing

### 🌐 API Integration
- Seamless integration with the ArbFinder FastAPI backend
- Real-time statistics from the server
- Search and filter listings from the API

### ⚙️ Configuration Management
- Save custom search configurations with names
- Load previously saved configurations
- Manage API endpoint URLs
- Persistent settings across sessions

## Installation

### Prerequisites
- Go 1.24 or later
- Access to ArbFinder API server (optional, defaults to localhost:8080)

### Build from Source

```bash
cd tui
go build -o arbfinder-tui
```

### Run

```bash
./arbfinder-tui
```

Or from the project root:

```bash
make run-tui
```

## Usage

### Navigation
- **Tab** / **Shift+Tab**: Switch between panes
- **↑** / **↓**: Navigate within panes
- **←** / **→**: Select options (in search pane)
- **Enter**: Execute action (search, load config, etc.)
- **Ctrl+C** / **Q**: Quit application

### Search Pane
1. Enter your search query in the search box
2. Select a provider using arrow keys (shopgoodwill, govdeals, etc.)
3. Set minimum discount threshold
4. Press **Enter** to execute search

### Results Pane
- **j** / **k** (or **↑** / **↓**): Navigate results
- **Enter**: View detailed information
- **r**: Refresh results from API

### Statistics Pane
- View database statistics (searches, configs, cached data)
- API statistics (total listings, price ranges)
- Price analysis and trends
- **r**: Refresh statistics

### Configuration Pane
- **s**: Save current configuration
- **l**: Load selected configuration
- **d**: Delete selected configuration
- **r**: Refresh configuration list

## Database

The TUI uses a SQLite database stored at `~/.arbfinder_tui.db` with the following tables:

- **search_history**: Tracks all searches performed
- **saved_configs**: Stores named configurations
- **price_history**: Historical price data for items
- **cached_listings**: Cached search results

## API Configuration

By default, the TUI connects to `http://localhost:8080`. To change the API URL:

1. Navigate to the **Config** pane (press Tab)
2. Enter a configuration name
3. Set the API URL
4. Press **s** to save

## Architecture

```
tui/
├── main.go           # Main application and UI orchestration
├── database.go       # SQLite database layer
├── api_client.go     # HTTP client for backend API
├── search_pane.go    # Search interface pane
├── results_pane.go   # Results display pane
├── stats_pane.go     # Statistics and analytics pane
├── config_pane.go    # Configuration management pane
├── go.mod            # Go module dependencies
└── README.md         # This file
```

## Dependencies

- [Bubbletea](https://github.com/charmbracelet/bubbletea): TUI framework
- [Bubbles](https://github.com/charmbracelet/bubbles): TUI components (text inputs, lists)
- [Lipgloss](https://github.com/charmbracelet/lipgloss): Style definitions for TUI
- [go-sqlite3](https://github.com/mattn/go-sqlite3): SQLite database driver

## Development

### Adding New Features

1. Create a new pane file (e.g., `mypane.go`)
2. Implement the pane structure with `Update` and `View` methods
3. Add the pane to the main model in `main.go`
4. Add navigation in the main `Update` method

### Running Tests

```bash
go test ./...
```

### Code Style

```bash
go fmt ./...
go vet ./...
```

## Troubleshooting

### Database Issues
If you encounter database errors, delete the database file and restart:
```bash
rm ~/.arbfinder_tui.db
./arbfinder-tui
```

### API Connection Issues
- Ensure the backend API server is running: `make run-server`
- Check the API URL in the configuration pane
- Verify network connectivity

### Build Issues
If you encounter build errors:
```bash
go mod tidy
go clean -cache
go build -o arbfinder-tui
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details
