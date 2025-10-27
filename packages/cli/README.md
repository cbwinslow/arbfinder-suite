# @arbfinder/cli

Command-line interface for ArbFinder (TypeScript/Node.js version).

## Installation

```bash
npm install -g @arbfinder/cli
```

## Usage

```bash
# List all listings
arbfinder-ts list

# List with pagination
arbfinder-ts list --limit 20 --offset 0

# Search for listings
arbfinder-ts search "RTX 3060"

# Get statistics
arbfinder-ts stats

# Get API info
arbfinder-ts info

# Get comparable prices
arbfinder-ts comps

# Search comparable prices
arbfinder-ts comps "iPad"
```

## Options

### Global Options

- `--api-url <url>` - API base URL (default: `http://localhost:8080`)
- `--timeout <ms>` - Request timeout in milliseconds (default: `30000`)

### List Command

```bash
arbfinder-ts list [options]
```

Options:
- `-l, --limit <number>` - Number of results (default: `10`)
- `-o, --offset <number>` - Offset for pagination (default: `0`)
- `-s, --sort <field>` - Sort by field: `ts`, `price`, or `title` (default: `ts`)
- `--source <source>` - Filter by source

### Search Command

```bash
arbfinder-ts search <query>
```

Search for listings matching the query.

### Stats Command

```bash
arbfinder-ts stats
```

Display database statistics.

### Info Command

```bash
arbfinder-ts info
```

Get API information.

### Comps Command

```bash
arbfinder-ts comps [query] [options]
```

Get comparable prices, optionally filtered by query.

Options:
- `-l, --limit <number>` - Number of results (default: `10`)

## Examples

```bash
# Get latest 20 listings
arbfinder-ts list --limit 20

# Search for GPUs
arbfinder-ts search "RTX 3080"

# Get comps for iPads
arbfinder-ts comps "iPad"

# Connect to remote API
arbfinder-ts --api-url https://api.arbfinder.com list
```

## License

MIT
