"""Test configuration module."""

import json
import tempfile
from pathlib import Path

import pytest
from arbfinder import config as config_module


def test_default_config():
    """Test default configuration values."""
    config = config_module.DEFAULT_CONFIG

    assert config["live_limit"] == 80
    assert config["comp_limit"] == 150
    assert config["sim_threshold"] == 86
    assert config["threshold_pct"] == 20.0
    assert config["watch_interval"] == 3600


def test_load_nonexistent_config():
    """Test loading non-existent config returns defaults."""
    with tempfile.NamedTemporaryFile(mode="w", delete=True, suffix=".json") as f:
        config_path = f.name + "_nonexistent"
        config = config_module.load_config(config_path)

        assert config == config_module.DEFAULT_CONFIG


def test_save_and_load_config():
    """Test saving and loading configuration."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        config_path = f.name

    try:
        test_config = config_module.DEFAULT_CONFIG.copy()
        test_config["threshold_pct"] = 35.0
        test_config["live_limit"] = 100

        # Save config
        result = config_module.save_config(test_config, config_path)
        assert result is True

        # Load config
        loaded_config = config_module.load_config(config_path)
        assert loaded_config["threshold_pct"] == 35.0
        assert loaded_config["live_limit"] == 100
    finally:
        Path(config_path).unlink(missing_ok=True)


def test_update_config():
    """Test updating configuration."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        config_path = f.name

    try:
        # Create initial config
        config_module.save_config(config_module.DEFAULT_CONFIG, config_path)

        # Update config
        updates = {"threshold_pct": 50.0, "new_key": "new_value"}
        updated_config = config_module.update_config(updates, config_path)

        assert updated_config["threshold_pct"] == 50.0
        assert updated_config["new_key"] == "new_value"

        # Verify it was saved
        loaded_config = config_module.load_config(config_path)
        assert loaded_config["threshold_pct"] == 50.0
        assert loaded_config["new_key"] == "new_value"
    finally:
        Path(config_path).unlink(missing_ok=True)


def test_create_default_config():
    """Test creating default config file."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        config_path = f.name

    # Delete the file first
    Path(config_path).unlink()

    try:
        # Create default config
        result = config_module.create_default_config(config_path)
        assert result is True

        # Verify file was created
        assert Path(config_path).exists()

        # Load and verify content
        loaded_config = config_module.load_config(config_path)
        assert loaded_config == config_module.DEFAULT_CONFIG

        # Try creating again (should fail)
        result = config_module.create_default_config(config_path)
        assert result is False
    finally:
        Path(config_path).unlink(missing_ok=True)
