#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility functions for ArbFinder development and maintenance."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Any
import json


def inspect_database(db_path: str) -> Dict[str, Any]:
    """Inspect database contents and return statistics."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    stats = {}
    
    # Get table info
    tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    stats['tables'] = [t[0] for t in tables]
    
    # Listings stats
    stats['listings'] = {}
    stats['listings']['total'] = c.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
    stats['listings']['by_source'] = {}
    for row in c.execute("SELECT source, COUNT(*) FROM listings GROUP BY source"):
        stats['listings']['by_source'][row[0]] = row[1]
    
    # Get price range
    price_range = c.execute("SELECT MIN(price), MAX(price), AVG(price) FROM listings WHERE price > 0").fetchone()
    stats['listings']['price_range'] = {
        'min': price_range[0],
        'max': price_range[1],
        'avg': price_range[2]
    }
    
    # Comps stats
    stats['comps'] = {}
    stats['comps']['total'] = c.execute("SELECT COUNT(*) FROM comps").fetchone()[0]
    
    conn.close()
    return stats


def clean_old_listings(db_path: str, days: int = 30) -> int:
    """Remove listings older than specified days."""
    import time
    cutoff = time.time() - (days * 86400)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM listings WHERE ts < ?", (cutoff,))
    count = c.fetchone()[0]
    
    c.execute("DELETE FROM listings WHERE ts < ?", (cutoff,))
    conn.commit()
    conn.close()
    
    return count


def export_database_stats(db_path: str, output_path: str) -> bool:
    """Export database statistics to JSON file."""
    stats = inspect_database(db_path)
    
    try:
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)
        return True
    except Exception as e:
        print(f"Error exporting stats: {e}")
        return False


def backup_database(db_path: str, backup_dir: str = None) -> str:
    """Create a backup of the database."""
    import shutil
    from datetime import datetime
    
    if backup_dir is None:
        backup_dir = str(Path.home() / "arbfinder_backups")
    
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = str(Path(backup_dir) / f"arb_finder_backup_{timestamp}.sqlite3")
    
    shutil.copy2(db_path, backup_path)
    return backup_path


def vacuum_database(db_path: str) -> bool:
    """Optimize database by running VACUUM."""
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("VACUUM")
        conn.close()
        return True
    except Exception as e:
        print(f"Error vacuuming database: {e}")
        return False


def list_recent_listings(db_path: str, limit: int = 10) -> list:
    """Get most recent listings."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    query = """
        SELECT source, title, price, currency, ts 
        FROM listings 
        ORDER BY ts DESC 
        LIMIT ?
    """
    
    results = []
    for row in c.execute(query, (limit,)):
        results.append({
            'source': row[0],
            'title': row[1],
            'price': row[2],
            'currency': row[3],
            'timestamp': row[4]
        })
    
    conn.close()
    return results


if __name__ == "__main__":
    import sys
    
    db_path = str(Path.home() / ".arb_finder.sqlite3")
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "inspect":
            stats = inspect_database(db_path)
            print(json.dumps(stats, indent=2))
        
        elif command == "clean":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            count = clean_old_listings(db_path, days)
            print(f"Removed {count} listings older than {days} days")
        
        elif command == "backup":
            backup_path = backup_database(db_path)
            print(f"Backup created: {backup_path}")
        
        elif command == "vacuum":
            if vacuum_database(db_path):
                print("Database optimized successfully")
            else:
                print("Failed to optimize database")
        
        elif command == "recent":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            listings = list_recent_listings(db_path, limit)
            for listing in listings:
                print(f"{listing['source']}: {listing['title'][:50]} - ${listing['price']}")
        
        else:
            print("Unknown command. Available: inspect, clean, backup, vacuum, recent")
    else:
        print("Usage: python utils.py <command>")
        print("Commands: inspect, clean [days], backup, vacuum, recent [limit]")
