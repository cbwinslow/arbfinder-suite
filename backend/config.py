#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuration file support for ArbFinder."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("ArbFinder")

DEFAULT_CONFIG_PATH = str(Path.home() / ".arbfinder_config.json")

DEFAULT_CONFIG = {
    "query": "",
    "db_path": str(Path.home() / ".arb_finder.sqlite3"),
    "live_limit": 80,
    "comp_limit": 150,
    "sim_threshold": 86,
    "threshold_pct": 20.0,
    "providers": "shopgoodwill,govdeals,governmentsurplus",
    "watch_interval": 3600,  # 1 hour in seconds
    "notifications": {"enabled": False, "email": "", "min_discount": 30.0},
    "export": {
        "auto_csv": False,
        "csv_path": "arbfinder_results.csv",
        "auto_json": False,
        "json_path": "arbfinder_results.json",
    },
}


def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    config_path = path or DEFAULT_CONFIG_PATH

    try:
        if Path(config_path).exists():
            with open(config_path, "r") as f:
                user_config = json.load(f)
                # Merge with defaults
                config = DEFAULT_CONFIG.copy()
                config.update(user_config)
                logger.info(f"Loaded config from {config_path}")
                return config
        else:
            logger.info(f"No config file found at {config_path}, using defaults")
            return DEFAULT_CONFIG.copy()
    except Exception as e:
        logger.warning(f"Failed to load config from {config_path}: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any], path: Optional[str] = None) -> bool:
    """Save configuration to JSON file."""
    config_path = path or DEFAULT_CONFIG_PATH

    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved config to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save config to {config_path}: {e}")
        return False


def create_default_config(path: Optional[str] = None) -> bool:
    """Create a default configuration file."""
    config_path = path or DEFAULT_CONFIG_PATH

    if Path(config_path).exists():
        logger.warning(f"Config file already exists at {config_path}")
        return False

    return save_config(DEFAULT_CONFIG, config_path)


def update_config(updates: Dict[str, Any], path: Optional[str] = None) -> Dict[str, Any]:
    """Update configuration with new values."""
    config = load_config(path)
    config.update(updates)
    save_config(config, path)
    return config
