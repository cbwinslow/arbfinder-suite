#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enhanced CLI for ArbFinder Suite with subcommands."""

from __future__ import annotations

import argparse
import sys

from arbfinder import arb_finder
from arbfinder import config as config_module
from arbfinder import utils

try:
    from rich.console import Console

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False


__version__ = "0.4.0"


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="arbfinder",
        description="Find arbitrage opportunities across multiple marketplaces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  arbfinder search "RTX 3060" --csv deals.csv
  arbfinder watch "iPad Pro" --interval 1800
  arbfinder config show
  arbfinder server --port 8080
  arbfinder db stats

For more help on a subcommand: arbfinder <subcommand> --help
        """,
    )

    parser.add_argument("--version", action="version", version=f"ArbFinder Suite v{__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command (main functionality)
    search_parser = subparsers.add_parser(
        "search",
        help="Search for arbitrage opportunities",
        description="Search marketplaces for arbitrage opportunities",
    )
    search_parser.add_argument("query", help="Search query (e.g., 'RTX 3060')")
    search_parser.add_argument("--db", help="Database path")
    search_parser.add_argument(
        "--live-limit", type=int, default=80, help="Max live listings per provider"
    )
    search_parser.add_argument(
        "--comp-limit", type=int, default=150, help="Max sold comps to fetch"
    )
    search_parser.add_argument(
        "--sim-threshold", type=int, default=86, help="Similarity threshold 0-100"
    )
    search_parser.add_argument(
        "--threshold-pct", type=float, default=20.0, help="Min discount percentage"
    )
    search_parser.add_argument("--providers", help="Comma-separated provider list")
    search_parser.add_argument("--csv", help="Export to CSV file")
    search_parser.add_argument("--json", help="Export to JSON file")
    search_parser.add_argument(
        "-i", "--interactive", action="store_true", help="Interactive TUI mode"
    )
    search_parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress progress output"
    )
    search_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    # Watch command
    watch_parser = subparsers.add_parser(
        "watch",
        help="Continuously monitor for deals",
        description="Monitor marketplaces continuously for new deals",
    )
    watch_parser.add_argument("query", help="Search query")
    watch_parser.add_argument(
        "--interval", type=int, default=3600, help="Check interval in seconds"
    )
    watch_parser.add_argument(
        "--threshold-pct", type=float, default=20.0, help="Min discount percentage"
    )
    watch_parser.add_argument("--providers", help="Comma-separated provider list")
    watch_parser.add_argument("--config", help="Config file path")

    # Config command
    config_parser = subparsers.add_parser(
        "config", help="Manage configuration", description="Manage ArbFinder configuration"
    )
    config_subparsers = config_parser.add_subparsers(dest="config_action", help="Config actions")

    config_subparsers.add_parser("show", help="Show current configuration")

    config_init_parser = config_subparsers.add_parser("init", help="Create default config file")
    config_init_parser.add_argument("--path", help="Config file path")

    config_set_parser = config_subparsers.add_parser("set", help="Set a config value")
    config_set_parser.add_argument("key", help="Config key (e.g., threshold_pct)")
    config_set_parser.add_argument("value", help="Config value")
    config_set_parser.add_argument("--path", help="Config file path")

    config_get_parser = config_subparsers.add_parser("get", help="Get a config value")
    config_get_parser.add_argument("key", help="Config key")
    config_get_parser.add_argument("--path", help="Config file path")

    # Database command
    db_parser = subparsers.add_parser(
        "db", help="Database operations", description="Manage ArbFinder database"
    )
    db_subparsers = db_parser.add_subparsers(dest="db_action", help="Database actions")

    db_subparsers.add_parser("stats", help="Show database statistics")
    db_subparsers.add_parser("backup", help="Backup database")
    db_subparsers.add_parser("vacuum", help="Optimize database")

    db_clean_parser = db_subparsers.add_parser("clean", help="Clean old entries")
    db_clean_parser.add_argument(
        "--days", type=int, default=30, help="Remove entries older than N days"
    )

    # Server command
    server_parser = subparsers.add_parser(
        "server", help="Run API server", description="Start the FastAPI server"
    )
    server_parser.add_argument("--host", default="127.0.0.1", help="Server host")
    server_parser.add_argument("--port", type=int, default=8080, help="Server port")
    server_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    # Completion command
    completion_parser = subparsers.add_parser(
        "completion",
        help="Generate shell completion scripts",
        description="Generate shell completion scripts for bash/zsh",
    )
    completion_parser.add_argument("shell", choices=["bash", "zsh"], help="Shell type")

    return parser


def handle_search(args: argparse.Namespace) -> int:
    """Handle search command."""
    # Convert args to the format expected by arb_finder
    sys.argv = ["arbfinder"]
    sys.argv.append(args.query)

    if args.db:
        sys.argv.extend(["--db", args.db])
    if args.live_limit:
        sys.argv.extend(["--live-limit", str(args.live_limit)])
    if args.comp_limit:
        sys.argv.extend(["--comp-limit", str(args.comp_limit)])
    if args.sim_threshold:
        sys.argv.extend(["--sim-threshold", str(args.sim_threshold)])
    if args.threshold_pct:
        sys.argv.extend(["--threshold-pct", str(args.threshold_pct)])
    if args.providers:
        sys.argv.extend(["--providers", args.providers])
    if args.csv:
        sys.argv.extend(["--csv", args.csv])
    if args.json:
        sys.argv.extend(["--json", args.json])
    if args.interactive:
        sys.argv.append("--interactive")
    if args.quiet:
        sys.argv.append("--quiet")
    if args.verbose:
        sys.argv.append("--verbose")

    return arb_finder.main()


def handle_watch(args: argparse.Namespace) -> int:
    """Handle watch command."""
    sys.argv = ["arbfinder"]
    sys.argv.append(args.query)
    sys.argv.extend(["--watch", "--watch-interval", str(args.interval)])

    if args.threshold_pct:
        sys.argv.extend(["--threshold-pct", str(args.threshold_pct)])
    if args.providers:
        sys.argv.extend(["--providers", args.providers])
    if args.config:
        sys.argv.extend(["--config", args.config])

    return arb_finder.main()


def handle_config(args: argparse.Namespace) -> int:
    """Handle config command."""
    if args.config_action == "show":
        config = config_module.load_config(args.path if hasattr(args, "path") else None)
        if RICH_AVAILABLE:
            from rich.pretty import pprint

            pprint(config)
        else:
            import json

            print(json.dumps(config, indent=2))
        return 0

    elif args.config_action == "init":
        path = args.path if hasattr(args, "path") and args.path else None
        if config_module.create_default_config(path):
            print(f"Created default config at {path or config_module.DEFAULT_CONFIG_PATH}")
            return 0
        else:
            print("Failed to create config file", file=sys.stderr)
            return 1

    elif args.config_action == "set":
        config = config_module.load_config(args.path if hasattr(args, "path") else None)
        # Convert value to appropriate type
        value = args.value
        try:
            # Try to parse as number
            if "." in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            # Keep as string
            pass

        config[args.key] = value
        config_module.save_config(config, args.path if hasattr(args, "path") else None)
        print(f"Set {args.key} = {value}")
        return 0

    elif args.config_action == "get":
        config = config_module.load_config(args.path if hasattr(args, "path") else None)
        value = config.get(args.key)
        if value is not None:
            print(value)
            return 0
        else:
            print(f"Key '{args.key}' not found in config", file=sys.stderr)
            return 1

    return 0


def handle_db(args: argparse.Namespace) -> int:
    """Handle database command."""
    db_path = arb_finder.DEFAULT_DB_PATH

    if args.db_action == "stats":
        stats = utils.get_db_stats(db_path)
        if RICH_AVAILABLE:
            from rich.table import Table

            table = Table(title="Database Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            for key, value in stats.items():
                table.add_row(key.replace("_", " ").title(), str(value))

            console.print(table)
        else:
            for key, value in stats.items():
                print(f"{key}: {value}")
        return 0

    elif args.db_action == "backup":
        backup_path = utils.backup_db(db_path)
        if backup_path:
            print(f"Database backed up to: {backup_path}")
            return 0
        else:
            print("Backup failed", file=sys.stderr)
            return 1

    elif args.db_action == "clean":
        days = args.days if hasattr(args, "days") else 30
        count = utils.clean_old_entries(db_path, days)
        print(f"Cleaned {count} entries older than {days} days")
        return 0

    elif args.db_action == "vacuum":
        utils.vacuum_db(db_path)
        print("Database optimized")
        return 0

    return 0


def handle_server(args: argparse.Namespace) -> int:
    """Handle server command."""
    try:
        import uvicorn

        print(f"Starting server at http://{args.host}:{args.port}")
        uvicorn.run("arbfinder.api.main:app", host=args.host, port=args.port, reload=args.reload)
        return 0
    except ImportError:
        print("uvicorn not installed. Install with: pip install uvicorn", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nServer stopped")
        return 0


def handle_completion(args: argparse.Namespace) -> int:
    """Handle completion command."""
    if args.shell == "bash":
        print("""
# ArbFinder bash completion
_arbfinder_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="search watch config db server completion --help --version"
    
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}
complete -F _arbfinder_completion arbfinder

# Add to ~/.bashrc to enable permanently:
# eval "$(arbfinder completion bash)"
        """)
    elif args.shell == "zsh":
        print("""
#compdef arbfinder

_arbfinder() {
    local -a commands
    commands=(
        'search:Search for arbitrage opportunities'
        'watch:Continuously monitor for deals'
        'config:Manage configuration'
        'db:Database operations'
        'server:Run API server'
        'completion:Generate shell completion'
    )
    
    _describe 'command' commands
}

_arbfinder "$@"

# Add to ~/.zshrc to enable permanently:
# eval "$(arbfinder completion zsh)"
        """)
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()

    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    args = parser.parse_args()

    # Handle commands
    if args.command == "search":
        return handle_search(args)
    elif args.command == "watch":
        return handle_watch(args)
    elif args.command == "config":
        return handle_config(args)
    elif args.command == "db":
        return handle_db(args)
    elif args.command == "server":
        return handle_server(args)
    elif args.command == "completion":
        return handle_completion(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
