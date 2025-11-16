# ArbFinder TUI Examples

This document provides examples of how to use the ArbFinder TUI effectively.

## Basic Usage

### Starting the TUI

```bash
# From the tui directory
./arbfinder-tui

# Or from the project root
make run-tui
```

### Navigation Basics

1. **Switch Panes**: Press `Tab` to cycle through panes (Search → Results → Stats → Config)
2. **Move Back**: Press `Shift+Tab` to go back one pane
3. **Quit**: Press `Ctrl+C` or `q` to exit

## Example Workflows

### Workflow 1: Simple Search

1. Start the TUI
2. In the Search pane:
   - Type "RTX 3060" in the search box
   - Press `↓` to navigate to provider selection
   - Use `←/→` to select "shopgoodwill"
   - Press `↓` to navigate to threshold
   - Enter "25.0"
   - Press `Enter` to execute search
3. Press `Tab` to view results in the Results pane
4. Use `↑/↓` or `j/k` to navigate through listings

### Workflow 2: Save and Reuse Configuration

1. Navigate to the Config pane (press `Tab` until you reach it)
2. Enter a configuration name: "rtx_search_config"
3. Set your API URL: "http://localhost:8080"
4. Press `s` to save
5. Next time:
   - Navigate to Config pane
   - Use `↑/↓` to select your saved config
   - Press `l` to load it

### Workflow 3: Price Analysis

1. Perform several searches for the same item (e.g., "iPad Pro")
2. Navigate to the Stats pane
3. View:
   - Total searches performed
   - Price history entries
   - Average prices
4. Press `r` to refresh statistics

### Workflow 4: Working with Multiple Retailers

1. In Search pane, enter query: "laptop"
2. Press `↓` to navigate to providers
3. Press `→` to cycle through:
   - shopgoodwill
   - govdeals
   - governmentsurplus
4. Execute searches with each provider
5. Compare results in the Results pane

## Advanced Features

### Database Queries

The TUI stores all your data locally in `~/.arbfinder_tui.db`. You can query this directly:

```bash
sqlite3 ~/.arbfinder_tui.db "SELECT * FROM search_history ORDER BY timestamp DESC LIMIT 10;"
```

### Custom API Endpoint

If your backend API is running on a different host:

1. Navigate to Config pane
2. Create new config: "remote_api"
3. Set API URL: "http://192.168.1.100:8080"
4. Save with `s`
5. Load with `l` when needed

### Keyboard Shortcuts Summary

| Key         | Action                              | Where             |
|-------------|-------------------------------------|-------------------|
| `Tab`       | Next pane                           | Anywhere          |
| `Shift+Tab` | Previous pane                       | Anywhere          |
| `Ctrl+C`/`q`| Quit                                | Anywhere          |
| `↑/↓`       | Navigate fields/items               | Any pane          |
| `←/→`       | Select options                      | Search pane       |
| `Enter`     | Execute/Confirm                     | Any pane          |
| `j/k`       | Navigate results (Vim-style)        | Results pane      |
| `r`         | Refresh                             | Results/Stats     |
| `s`         | Save configuration                  | Config pane       |
| `l`         | Load selected configuration         | Config pane       |
| `d`         | Delete selected configuration       | Config pane       |

## Tips and Tricks

### Tip 1: Quick Searches
Save commonly used search configurations with descriptive names like:
- `rtx_25pct` - RTX cards with 25% discount
- `apple_deals` - Apple products with default settings
- `furniture_high` - Furniture with high discount threshold

### Tip 2: Price Tracking
The TUI automatically saves price history. Search for the same item periodically to build up historical data and spot trends.

### Tip 3: Offline Mode
Even without an API connection, you can:
- View cached listings in the Results pane
- Check statistics in the Stats pane
- Manage configurations in the Config pane

### Tip 4: Multiple Searches
You can switch between panes while a search is running. The Results pane will update automatically when data is available.

### Tip 5: Clean Database
To start fresh or if database becomes too large:

```bash
rm ~/.arbfinder_tui.db
```

The TUI will create a new database on next startup.

## Integration with Backend

### Start Backend API

Before using the TUI, start the backend API:

```bash
# From project root
make run-server

# Or manually
uvicorn backend.api.main:app --reload --port 8080
```

### Verify API Connection

1. Start the TUI
2. Navigate to Stats pane
3. Check "API Statistics" section
4. If it shows "API not connected", verify:
   - Backend server is running
   - API URL in Config is correct
   - No firewall blocking connection

## Troubleshooting

### Problem: "Database locked" error
**Solution**: Only one TUI instance can run at a time. Close other instances.

### Problem: No search results
**Solution**: 
1. Verify backend API is running
2. Check API URL in Config pane
3. Try searching via API directly: `curl http://localhost:8080/api/listings`

### Problem: Can't see typed input
**Solution**: This is normal for some fields. The text is captured even if not visible.

### Problem: TUI layout broken
**Solution**: 
1. Make terminal window larger (minimum 80x24)
2. Restart TUI

## Sample Data

To populate the database with sample data for testing:

```bash
cd tui
go run . << EOF
test search 1
EOF
```

Or use the Python backend to populate the API:

```bash
python3 backend/arb_finder.py "RTX 3060" --csv /tmp/test.csv
```

Then search from the TUI to see results.
