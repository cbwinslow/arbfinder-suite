"""
API endpoints for live updates and activity feed
"""

import logging
import os
import sqlite3
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["updates"])

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("ARBF_DB", os.path.expanduser("~/.arb_finder.sqlite3"))


class Update(BaseModel):
    """Model for live update"""

    id: int
    timestamp: float
    type: str
    message: str
    data: Optional[Dict[str, Any]] = None


class LiveUpdatesResponse(BaseModel):
    """Response model for live updates"""

    updates: List[Update]
    total: int


@router.get("/live-updates", response_model=LiveUpdatesResponse)
async def get_live_updates(
    limit: int = Query(50, ge=1, le=200), type_filter: Optional[str] = None
):
    """Get live activity updates sourced from DB tables (crawl_results, crew_runs, agent_jobs)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    updates: List[Dict[str, Any]] = []

    # Crawl results
    try:
        rows = c.execute(
            "SELECT id, crawled_at, target_name, status, items_found, error_msg "
            "FROM crawl_results ORDER BY crawled_at DESC LIMIT 100"
        ).fetchall()
        for row in rows:
            rid, ts, target, status, items, err = row
            if status == "error":
                msg = f"Crawler '{target}' failed: {err or 'unknown error'}"
                upd_type = "error"
            elif status == "partial":
                msg = f"Crawler '{target}' completed with warnings: {items} items found"
                upd_type = "crawler"
            else:
                msg = f"Crawler '{target}' completed: {items} items found"
                upd_type = "crawler"
            updates.append(
                {"id": f"crawl-{rid}", "timestamp": ts, "type": upd_type, "message": msg}
            )
    except sqlite3.OperationalError:
        pass  # Table not yet created

    # Crew runs
    try:
        rows = c.execute(
            "SELECT id, started_at, completed_at, crew_type, status, items_processed, error_message "
            "FROM crew_runs ORDER BY started_at DESC LIMIT 100"
        ).fetchall()
        for row in rows:
            rid, started, completed, crew, status, items, err = row
            ts = completed if completed else started
            if status == "completed":
                msg = f"Crew '{crew}' completed: {items} items processed"
                upd_type = "agent"
            elif status == "failed":
                msg = f"Crew '{crew}' failed: {err or 'unknown error'}"
                upd_type = "error"
            elif status == "running":
                msg = f"Crew '{crew}' is running"
                upd_type = "agent"
            else:
                msg = f"Crew '{crew}' queued"
                upd_type = "agent"
            updates.append(
                {"id": f"crew-{rid}", "timestamp": ts, "type": upd_type, "message": msg}
            )
    except sqlite3.OperationalError:
        pass  # Table not yet created

    # Agent jobs
    try:
        rows = c.execute(
            "SELECT id, started_at, completed_at, agent_type, status, error_msg "
            "FROM agent_jobs ORDER BY started_at DESC LIMIT 100"
        ).fetchall()
        for row in rows:
            rid, started, completed, agent, status, err = row
            ts = completed if completed else started
            if status == "completed":
                msg = f"Agent '{agent}' completed successfully"
                upd_type = "agent"
            elif status == "failed":
                msg = f"Agent '{agent}' failed: {err or 'unknown error'}"
                upd_type = "error"
            else:
                msg = f"Agent '{agent}' is {status}"
                upd_type = "agent"
            updates.append(
                {"id": f"job-{rid}", "timestamp": ts, "type": upd_type, "message": msg}
            )
    except sqlite3.OperationalError:
        pass  # Table not yet created

    conn.close()

    # Sort by timestamp descending
    updates.sort(key=lambda u: u["timestamp"], reverse=True)

    if type_filter:
        updates = [u for u in updates if u["type"] == type_filter]

    total = len(updates)
    updates = updates[:limit]

    result = [
        Update(id=i + 1, timestamp=u["timestamp"], type=u["type"], message=u["message"])
        for i, u in enumerate(updates)
    ]

    return LiveUpdatesResponse(updates=result, total=total)


@router.get("/activity-stats")
async def get_activity_stats():
    """Get real activity statistics from the database"""
    import time

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = time.time()
    one_hour_ago = now - 3600
    one_day_ago = now - 86400

    stats: Dict[str, Any] = {
        "last_hour": {"crawls": 0, "items_found": 0, "agent_jobs": 0, "errors": 0},
        "last_24_hours": {"crawls": 0, "items_found": 0, "agent_jobs": 0, "errors": 0},
        "uptime_seconds": 0,
        "active_crawlers": 0,
        "active_agents": 0,
    }

    try:
        for window_key, threshold in [("last_hour", one_hour_ago), ("last_24_hours", one_day_ago)]:
            row = c.execute(
                "SELECT COUNT(*), COALESCE(SUM(items_found), 0) "
                "FROM crawl_results WHERE crawled_at > ?",
                (threshold,),
            ).fetchone()
            stats[window_key]["crawls"] = row[0]
            stats[window_key]["items_found"] = row[1]

            error_row = c.execute(
                "SELECT COUNT(*) FROM crawl_results WHERE crawled_at > ? AND status = 'error'",
                (threshold,),
            ).fetchone()
            stats[window_key]["errors"] = error_row[0]
    except sqlite3.OperationalError:
        pass

    try:
        for window_key, threshold in [("last_hour", one_hour_ago), ("last_24_hours", one_day_ago)]:
            row = c.execute(
                "SELECT COUNT(*) FROM agent_jobs WHERE started_at > ?", (threshold,)
            ).fetchone()
            stats[window_key]["agent_jobs"] += row[0]

            fail_row = c.execute(
                "SELECT COUNT(*) FROM agent_jobs WHERE started_at > ? AND status = 'failed'",
                (threshold,),
            ).fetchone()
            stats[window_key]["errors"] += fail_row[0]

        stats["active_agents"] = c.execute(
            "SELECT COUNT(*) FROM agent_jobs WHERE status IN ('queued','running')"
        ).fetchone()[0]
    except sqlite3.OperationalError:
        pass

    try:
        stats["active_crawlers"] = c.execute(
            "SELECT COUNT(DISTINCT target_name) FROM crawl_results "
            "WHERE crawled_at > ? AND status != 'error'",
            (one_hour_ago,),
        ).fetchone()[0]
    except sqlite3.OperationalError:
        pass

    conn.close()
    return stats
