#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Interactive TUI for ArbFinder using Rich library."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.prompt import Prompt, Confirm
from rich.text import Text

console = Console()


def show_welcome():
    """Display welcome banner."""
    welcome_text = Text()
    welcome_text.append("ArbFinder Suite", style="bold cyan")
    welcome_text.append("\n")
    welcome_text.append("Find arbitrage deals across multiple marketplaces", style="dim")
    
    panel = Panel(
        welcome_text,
        box=box.DOUBLE,
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)


def create_listings_table(rows: List[Dict[str, Any]], show_comps: bool = True) -> Table:
    """Create a rich table for displaying listings."""
    table = Table(
        title="📊 Arbitrage Opportunities",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )
    
    table.add_column("Source", style="cyan", no_wrap=True)
    table.add_column("Title", style="white", max_width=40)
    table.add_column("Price", justify="right", style="green")
    
    if show_comps:
        table.add_column("Comp Avg", justify="right", style="yellow")
        table.add_column("Discount %", justify="right", style="bold red")
        table.add_column("Match", justify="center", style="dim")
    
    for row in rows:
        price_str = f"${row['price']:.2f}"
        
        if show_comps and row.get('avg_price'):
            avg_str = f"${row['avg_price']:.2f}"
            discount = row.get('discount_vs_avg_pct', 0)
            discount_str = f"{discount:.1f}%" if discount else "N/A"
            match_str = f"{row.get('similarity', 0)}%"
            
            # Color code based on discount
            if discount >= 30:
                discount_style = "bold green"
            elif discount >= 20:
                discount_style = "green"
            elif discount >= 10:
                discount_style = "yellow"
            else:
                discount_style = "dim"
            
            table.add_row(
                row['source'],
                row['title'][:40],
                price_str,
                avg_str,
                Text(discount_str, style=discount_style),
                match_str
            )
        else:
            table.add_row(
                row['source'],
                row['title'][:40],
                price_str
            )
    
    return table


def create_progress_display() -> Progress:
    """Create a progress display for crawling operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=True
    )


def show_summary(stats: Dict[str, Any]):
    """Display summary statistics."""
    table = Table(title="📈 Summary Statistics", box=box.SIMPLE)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="green")
    
    for key, value in stats.items():
        table.add_row(key, str(value))
    
    console.print(table)


def prompt_search_query() -> str:
    """Prompt user for search query."""
    return Prompt.ask(
        "[bold cyan]Enter search query[/bold cyan]",
        default="RTX 3060"
    )


def prompt_providers() -> str:
    """Prompt user for provider selection."""
    console.print("\n[bold]Available Providers:[/bold]")
    console.print("  • shopgoodwill - ShopGoodwill auctions")
    console.print("  • govdeals - Government surplus auctions")
    console.print("  • governmentsurplus - GovernmentSurplus.com")
    console.print("  • manual - Import from CSV/JSON")
    
    return Prompt.ask(
        "\n[bold cyan]Select providers (comma-separated)[/bold cyan]",
        default="shopgoodwill,govdeals,governmentsurplus"
    )


def prompt_threshold() -> float:
    """Prompt user for discount threshold."""
    threshold = Prompt.ask(
        "[bold cyan]Minimum discount percentage[/bold cyan]",
        default="20.0"
    )
    return float(threshold)


def confirm_export() -> bool:
    """Ask user if they want to export results."""
    return Confirm.ask("\n[bold]Export results to CSV?[/bold]", default=True)


def prompt_export_path() -> str:
    """Prompt user for export file path."""
    return Prompt.ask(
        "[bold cyan]Export file path[/bold cyan]",
        default="arbfinder_results.csv"
    )


def display_error(message: str, exception: Optional[Exception] = None):
    """Display error message."""
    error_text = Text()
    error_text.append("❌ Error: ", style="bold red")
    error_text.append(message, style="red")
    
    if exception:
        error_text.append(f"\n{str(exception)}", style="dim red")
    
    console.print(Panel(error_text, border_style="red", box=box.ROUNDED))


def display_success(message: str):
    """Display success message."""
    success_text = Text()
    success_text.append("✅ ", style="bold green")
    success_text.append(message, style="green")
    console.print(success_text)


def display_info(message: str):
    """Display info message."""
    console.print(f"ℹ️  [cyan]{message}[/cyan]")


def display_warning(message: str):
    """Display warning message."""
    console.print(f"⚠️  [yellow]{message}[/yellow]")


async def interactive_mode():
    """Run interactive TUI mode."""
    show_welcome()
    console.print()
    
    # Get user input
    query = prompt_search_query()
    providers = prompt_providers()
    threshold = prompt_threshold()
    
    console.print(f"\n[dim]Searching for: {query}[/dim]")
    console.print(f"[dim]Providers: {providers}[/dim]")
    console.print(f"[dim]Min discount: {threshold}%[/dim]\n")
    
    return {
        "query": query,
        "providers": providers,
        "threshold_pct": threshold
    }
