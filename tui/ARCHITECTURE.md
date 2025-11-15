# ArbFinder TUI Architecture

## Overview

The ArbFinder TUI is a sophisticated terminal user interface built with the Bubbletea framework. It provides a multi-pane, interactive interface for searching arbitrage opportunities, managing configurations, and analyzing price data.

## Technology Stack

- **Framework**: [Bubbletea](https://github.com/charmbracelet/bubbletea) v1.3.10
- **UI Components**: [Bubbles](https://github.com/charmbracelet/bubbles) v0.21.0
- **Styling**: [Lipgloss](https://github.com/charmbracelet/lipgloss) v1.1.0
- **Database**: SQLite3 via [go-sqlite3](https://github.com/mattn/go-sqlite3) v1.14.32
- **Language**: Go 1.24+

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Main Application                      │
│                      (main.go)                          │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │  Search  │  │ Results  │  │  Stats   │  │  Config  ││
│  │   Pane   │  │   Pane   │  │   Pane   │  │   Pane   ││
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘│
│       │             │              │              │      │
└───────┼─────────────┼──────────────┼──────────────┼──────┘
        │             │              │              │
        └─────────────┴──────────────┴──────────────┘
                      │
        ┌─────────────┴──────────────┐
        │                            │
        ▼                            ▼
┌──────────────┐            ┌──────────────┐
│   Database   │            │  API Client  │
│  (SQLite3)   │            │   (HTTP)     │
└──────────────┘            └──────┬───────┘
                                   │
                                   ▼
                          ┌──────────────┐
                          │   FastAPI    │
                          │   Backend    │
                          └──────────────┘
```

## Core Components

### 1. Main Application (main.go)

**Responsibilities:**
- Initialize the application and all panes
- Manage global state and window dimensions
- Route messages between panes
- Handle keyboard navigation (Tab, Shift+Tab, Quit)
- Coordinate async operations

**Key Functions:**
- `initialModel()`: Sets up the application state
- `Init()`: Runs initialization commands
- `Update(msg)`: Handles all input and state updates
- `View()`: Renders the current UI state

### 2. Pane Components

Each pane is a self-contained module with:
- Independent state management
- `Update(msg)` method for handling inputs
- `View(width, height)` method for rendering
- Keyboard shortcuts specific to that pane

#### Search Pane (search_pane.go)
- Text input for search queries
- Provider selection (shopgoodwill, govdeals, etc.)
- Discount threshold configuration
- Search execution trigger

#### Results Pane (results_pane.go)
- Paginated listing display
- Keyboard navigation (j/k, ↑/↓)
- Result details view
- Refresh functionality

#### Stats Pane (stats_pane.go)
- Database statistics (searches, configs, cache)
- API statistics (total listings, price ranges)
- Price history analysis
- Real-time updates

#### Config Pane (config_pane.go)
- Configuration name and API URL inputs
- List of saved configurations
- Save/Load/Delete operations
- Configuration management

### 3. Database Layer (database.go)

**Schema:**

```sql
-- Search history
CREATE TABLE search_history (
    id INTEGER PRIMARY KEY,
    query TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    results INTEGER DEFAULT 0
);

-- Saved configurations
CREATE TABLE saved_configs (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    config TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Price history tracking
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY,
    item_title TEXT NOT NULL,
    price REAL NOT NULL,
    source TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

-- Cached listings
CREATE TABLE cached_listings (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    condition TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);
```

**Key Methods:**
- `SaveSearchHistory(query, results)`: Tracks searches
- `SaveConfig(name, config)`: Persists configurations
- `SavePriceHistory(title, price, source, metadata)`: Records prices
- `CacheListing(listing)`: Stores listings offline
- `GetStats()`: Retrieves aggregate statistics

### 4. API Client (api_client.go)

**Endpoints:**
- `GET /api/listings`: Fetch listings with pagination
- `GET /api/listings/search?q=query`: Search listings
- `GET /api/statistics`: Get database statistics
- `GET /api/comps`: Get comparable prices
- `GET /api/comps/search?q=query`: Search comps

**Features:**
- Configurable base URL
- 30-second timeout
- Error handling and retry logic
- JSON serialization/deserialization

### 5. Message System (messages.go)

**Message Types:**
- `SearchMsg`: Triggered when search is initiated
- `SearchResultMsg`: Contains search results or errors
- `StatsLoadedMsg`: Statistics data loaded
- `ConfigLoadedMsg`: Configurations loaded
- `ConfigSavedMsg`: Configuration saved confirmation
- `StatusMsg`: General status updates

## Data Flow

### Search Flow

```
1. User enters query in Search Pane
2. User presses Enter
3. SearchPane emits SearchMsg
4. Main receives SearchMsg
5. Main calls API Client (async)
6. API Client performs HTTP request
7. API Client emits SearchResultMsg
8. Main updates Results Pane
9. Main saves to Database
10. Results Pane re-renders with new data
```

### Configuration Flow

```
1. User enters config name and settings in Config Pane
2. User presses 's' (save)
3. Config Pane calls Database.SaveConfig()
4. Database persists to SQLite
5. Config Pane refreshes list
6. User can later press 'l' (load) to restore
```

## Design Patterns

### 1. Model-View-Update (MVU)

The TUI follows the Elm architecture (MVU pattern):
- **Model**: Application state (panes, database, etc.)
- **View**: Rendering functions that produce terminal output
- **Update**: Message handlers that modify state

### 2. Message Passing

Panes communicate via message passing rather than direct calls:
- Loose coupling between components
- Async operations without blocking
- Easier to test and reason about

### 3. Dependency Injection

Components receive their dependencies at initialization:
- Database passed to Stats and Config panes
- API Client embedded in Results pane
- Enables testing with mocks

### 4. Single Responsibility

Each file has a clear, focused purpose:
- One pane per file
- Database operations isolated
- API calls separated from UI logic

## State Management

### Global State (model)
- Current pane index
- Window dimensions
- References to all panes
- Database connection

### Pane-Local State
Each pane maintains:
- User inputs (text fields, selections)
- Display data (results, stats, configs)
- Loading/error states
- Pagination offsets

### Persistent State (Database)
- Search history
- Saved configurations
- Price history
- Cached listings

## Performance Considerations

### 1. Async Operations
- Search API calls run in goroutines
- Database queries don't block UI
- Results stream to UI as available

### 2. Pagination
- Results pane displays 10 items at a time
- Scrolling doesn't reload all data
- Efficient memory usage for large result sets

### 3. Caching
- Listings cached in SQLite
- Reduces API calls
- Enables offline mode

### 4. Incremental Rendering
- Only current pane fully renders
- Other panes use lightweight tabs
- Minimal terminal updates

## Testing Strategy

### Unit Tests (database_test.go)
- Test each database operation independently
- Use temporary databases for isolation
- Cover success and error cases
- Verify data integrity

### Integration Tests (planned)
- Test pane interactions
- Verify message passing
- Test API integration
- End-to-end workflows

### Manual Testing
- Run TUI and verify each pane
- Test keyboard navigation
- Verify API connectivity
- Check error handling

## Error Handling

### Database Errors
- Graceful degradation (continue without DB)
- User-friendly error messages
- Automatic table creation on startup

### API Errors
- Display errors in pane status
- Cache last successful results
- Offline mode when API unavailable

### Input Validation
- Type checking for numeric inputs
- URL validation for API endpoint
- Safe SQL parameter binding

## Future Enhancements

### Planned Features
1. **Export Functionality**: Save results to CSV/JSON
2. **Real-time Updates**: WebSocket connection for live data
3. **Chart Visualization**: ASCII charts for price trends
4. **Filtering**: Advanced result filtering in Results pane
5. **Theming**: Customizable color schemes
6. **Multi-language**: i18n support

### Technical Improvements
1. **Logging**: Structured logging with levels
2. **Metrics**: Performance monitoring
3. **Configuration**: TOML/YAML config file support
4. **Plugins**: Extension system for custom panes
5. **Testing**: Increase coverage to 90%+

## Contributing

When adding new features:

1. **Create a new pane?** Follow the pattern in existing pane files
2. **Add a message type?** Define it in `messages.go`
3. **Database changes?** Add migration logic
4. **API changes?** Update `api_client.go` methods
5. **Always add tests** for new functionality

## References

- [Bubbletea Documentation](https://github.com/charmbracelet/bubbletea)
- [Bubbles Components](https://github.com/charmbracelet/bubbles)
- [Lipgloss Styling](https://github.com/charmbracelet/lipgloss)
- [Go SQLite Driver](https://github.com/mattn/go-sqlite3)
- [ArbFinder Suite Main README](../README.md)
