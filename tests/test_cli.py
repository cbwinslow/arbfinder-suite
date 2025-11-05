"""Test CLI module."""

import sys
from io import StringIO

import pytest
from arbfinder import cli


def test_version():
    """Test version is defined."""
    assert cli.__version__ == "0.4.0"


def test_create_parser():
    """Test parser creation."""
    parser = cli.create_parser()
    assert parser is not None
    assert parser.prog == "arbfinder"


def test_parser_search_command():
    """Test search command parsing."""
    parser = cli.create_parser()
    args = parser.parse_args(["search", "RTX 3060", "--csv", "output.csv"])

    assert args.command == "search"
    assert args.query == "RTX 3060"
    assert args.csv == "output.csv"


def test_parser_watch_command():
    """Test watch command parsing."""
    parser = cli.create_parser()
    args = parser.parse_args(["watch", "iPad Pro", "--interval", "1800"])

    assert args.command == "watch"
    assert args.query == "iPad Pro"
    assert args.interval == 1800


def test_parser_config_show():
    """Test config show command."""
    parser = cli.create_parser()
    args = parser.parse_args(["config", "show"])

    assert args.command == "config"
    assert args.config_action == "show"


def test_parser_config_set():
    """Test config set command."""
    parser = cli.create_parser()
    args = parser.parse_args(["config", "set", "threshold_pct", "30.0"])

    assert args.command == "config"
    assert args.config_action == "set"
    assert args.key == "threshold_pct"
    assert args.value == "30.0"


def test_parser_db_stats():
    """Test db stats command."""
    parser = cli.create_parser()
    args = parser.parse_args(["db", "stats"])

    assert args.command == "db"
    assert args.db_action == "stats"


def test_parser_server_command():
    """Test server command parsing."""
    parser = cli.create_parser()
    args = parser.parse_args(["server", "--port", "9000", "--reload"])

    assert args.command == "server"
    assert args.port == 9000
    assert args.reload is True


def test_parser_completion_bash():
    """Test completion command for bash."""
    parser = cli.create_parser()
    args = parser.parse_args(["completion", "bash"])

    assert args.command == "completion"
    assert args.shell == "bash"


def test_handle_completion_bash(capsys):
    """Test bash completion generation."""
    from argparse import Namespace

    args = Namespace(shell="bash")

    result = cli.handle_completion(args)
    assert result == 0

    captured = capsys.readouterr()
    assert "_arbfinder_completion" in captured.out
    assert "complete -F" in captured.out


def test_handle_completion_zsh(capsys):
    """Test zsh completion generation."""
    from argparse import Namespace

    args = Namespace(shell="zsh")

    result = cli.handle_completion(args)
    assert result == 0

    captured = capsys.readouterr()
    assert "#compdef arbfinder" in captured.out
    assert "_arbfinder" in captured.out
