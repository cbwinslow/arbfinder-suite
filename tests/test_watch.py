"""Tests for backend/watch.py - watch mode functionality."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.watch import WatchMode


class TestWatchModeInit:
    """Tests for WatchMode initialization."""

    def test_default_initialization(self):
        wm = WatchMode()
        assert wm.interval == 3600
        assert wm.notify_threshold == 30.0
        assert wm.max_iterations is None
        assert wm.iteration == 0
        assert wm.best_deals == []

    def test_custom_initialization(self):
        wm = WatchMode(interval=60, notify_threshold=25.0, max_iterations=3)
        assert wm.interval == 60
        assert wm.notify_threshold == 25.0
        assert wm.max_iterations == 3

    def test_best_deals_starts_empty(self):
        wm = WatchMode()
        assert isinstance(wm.best_deals, list)
        assert len(wm.best_deals) == 0


class TestFindNewDeals:
    """Tests for WatchMode._find_new_deals method."""

    def test_find_new_deals_above_threshold(self):
        wm = WatchMode(notify_threshold=20.0)
        results = [
            {
                "url": "http://example.com/1",
                "title": "RTX 3060",
                "price": 100.0,
                "discount_vs_avg_pct": 30.0,
                "source": "test",
            },
            {
                "url": "http://example.com/2",
                "title": "iPad Pro",
                "price": 200.0,
                "discount_vs_avg_pct": 15.0,
                "source": "test",
            },
        ]
        new_deals = wm._find_new_deals(results)
        assert len(new_deals) == 1
        assert new_deals[0]["url"] == "http://example.com/1"

    def test_find_new_deals_no_duplicates(self):
        wm = WatchMode(notify_threshold=20.0)
        deal = {
            "url": "http://example.com/1",
            "title": "RTX 3060",
            "price": 100.0,
            "discount_vs_avg_pct": 30.0,
            "source": "test",
        }
        wm.best_deals.append(deal)

        new_deals = wm._find_new_deals([deal])
        assert len(new_deals) == 0

    def test_find_new_deals_adds_to_best_deals(self):
        wm = WatchMode(notify_threshold=20.0)
        results = [
            {
                "url": "http://example.com/1",
                "title": "RTX 3060",
                "price": 100.0,
                "discount_vs_avg_pct": 30.0,
                "source": "test",
            },
        ]
        wm._find_new_deals(results)
        assert len(wm.best_deals) == 1

    def test_find_new_deals_empty_results(self):
        wm = WatchMode()
        new_deals = wm._find_new_deals([])
        assert new_deals == []

    def test_find_new_deals_none_discount(self):
        wm = WatchMode(notify_threshold=20.0)
        results = [
            {
                "url": "http://example.com/1",
                "title": "Item",
                "price": 100.0,
                "discount_vs_avg_pct": None,
                "source": "test",
            },
        ]
        new_deals = wm._find_new_deals(results)
        assert len(new_deals) == 0

    def test_find_new_deals_missing_discount_key(self):
        wm = WatchMode(notify_threshold=20.0)
        results = [
            {"url": "http://example.com/1", "title": "Item", "price": 100.0, "source": "test"},
        ]
        new_deals = wm._find_new_deals(results)
        assert len(new_deals) == 0

    def test_find_new_deals_exactly_at_threshold(self):
        wm = WatchMode(notify_threshold=20.0)
        results = [
            {
                "url": "http://example.com/1",
                "title": "Item",
                "price": 100.0,
                "discount_vs_avg_pct": 20.0,
                "source": "test",
            },
        ]
        new_deals = wm._find_new_deals(results)
        assert len(new_deals) == 1


class TestLogDeal:
    """Tests for WatchMode._log_deal method."""

    def test_log_deal_does_not_raise(self):
        wm = WatchMode()
        deal = {
            "title": "RTX 3060",
            "price": 150.0,
            "discount_vs_avg_pct": 35.0,
            "source": "shopgoodwill",
            "url": "http://example.com/1",
        }
        # Should not raise
        wm._log_deal(deal)

    def test_log_deal_missing_optional_fields(self):
        wm = WatchMode()
        deal = {
            "title": "RTX 3060",
            "price": 150.0,
            "source": "shopgoodwill",
            "url": "http://example.com/1",
        }
        # Should not raise even without discount field
        wm._log_deal(deal)

    def test_log_deal_long_title(self):
        wm = WatchMode()
        deal = {
            "title": "A" * 200,
            "price": 150.0,
            "discount_vs_avg_pct": 25.0,
            "source": "test",
            "url": "http://example.com/1",
        }
        # Should not raise with very long title
        wm._log_deal(deal)


class TestWatchModeRun:
    """Tests for WatchMode.run method."""

    @pytest.mark.asyncio
    async def test_run_respects_max_iterations(self):
        wm = WatchMode(interval=0, max_iterations=2, notify_threshold=20.0)

        call_count = 0

        async def mock_search():
            nonlocal call_count
            call_count += 1
            return []

        result = await wm.run(mock_search)
        assert call_count == 2
        assert wm.iteration == 2

    @pytest.mark.asyncio
    async def test_run_returns_best_deals(self):
        wm = WatchMode(interval=0, max_iterations=1, notify_threshold=20.0)

        async def mock_search():
            return [
                {
                    "url": "http://example.com/1",
                    "title": "Deal Item",
                    "price": 100.0,
                    "discount_vs_avg_pct": 35.0,
                    "source": "test",
                }
            ]

        result = await wm.run(mock_search)
        assert len(result) == 1
        assert result[0]["url"] == "http://example.com/1"

    @pytest.mark.asyncio
    async def test_run_handles_search_error(self):
        wm = WatchMode(interval=0, max_iterations=1, notify_threshold=20.0)

        async def failing_search():
            raise ValueError("Search failed")

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await wm.run(failing_search)
        # Should complete without raising
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_run_with_no_deals(self):
        wm = WatchMode(interval=0, max_iterations=1, notify_threshold=50.0)

        async def mock_search():
            return [
                {
                    "url": "http://example.com/1",
                    "title": "Item",
                    "price": 100.0,
                    "discount_vs_avg_pct": 10.0,
                    "source": "test",
                }
            ]

        result = await wm.run(mock_search)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_run_accumulates_deals_across_iterations(self):
        wm = WatchMode(interval=0, max_iterations=2, notify_threshold=20.0)
        iteration = 0

        async def mock_search():
            nonlocal iteration
            iteration += 1
            return [
                {
                    "url": f"http://example.com/{iteration}",
                    "title": f"Deal {iteration}",
                    "price": 100.0,
                    "discount_vs_avg_pct": 35.0,
                    "source": "test",
                }
            ]

        result = await wm.run(mock_search)
        assert len(result) == 2
