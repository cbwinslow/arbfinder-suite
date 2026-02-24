"""
API endpoints for crawler management and monitoring
"""

import json
import logging
import os
import sqlite3
import time
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Try to import crawler service
try:
    from backend.crawler.crawler_service import CrawlerService, CrawlResult
except ImportError:
    try:
        from crawler.crawler_service import CrawlerService, CrawlResult
    except ImportError:
        CrawlerService = None
        CrawlResult = None
        logging.warning("CrawlerService not available")

router = APIRouter(prefix="/api/crawler", tags=["crawler"])

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("ARBF_DB", os.path.expanduser("~/.arb_finder.sqlite3"))

# Global crawler instance
_crawler_service = None


def init_crawl_results_table():
    """Initialize crawl_results table if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS crawl_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_name TEXT NOT NULL,
            url TEXT,
            status TEXT NOT NULL,
            items_found INTEGER DEFAULT 0,
            duration_ms INTEGER,
            error_msg TEXT,
            metadata TEXT,
            crawled_at REAL NOT NULL
        )
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_crawl_results_target ON crawl_results(target_name)
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_crawl_results_crawled_at ON crawl_results(crawled_at)
    """)
    conn.commit()
    conn.close()


# Initialize table on module load
init_crawl_results_table()


def get_crawler_service():
    """Get or create crawler service instance"""
    global _crawler_service
    if _crawler_service is None and CrawlerService is not None:
        _crawler_service = CrawlerService()
    return _crawler_service


def _store_crawl_result(result: Any) -> None:
    """Persist a CrawlResult to the crawl_results table."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO crawl_results
            (target_name, url, status, items_found, duration_ms, error_msg, metadata, crawled_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            result.target_name,
            result.url,
            result.status,
            result.items_found,
            result.duration_ms,
            result.error_msg,
            json.dumps(result.metadata) if result.metadata else None,
            time.time(),
        ),
    )
    conn.commit()
    conn.close()


class CrawlerStatusResponse(BaseModel):
    """Response model for crawler status"""

    results: List[Dict[str, Any]]
    total_items: int
    active_targets: int


@router.get("/status", response_model=CrawlerStatusResponse)
async def get_crawler_status():
    """Get status of most recent crawl per target from the database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Fetch the most recent crawl result for each target
    c.execute("""
        SELECT target_name, url, status, items_found, duration_ms, error_msg, metadata, crawled_at
        FROM crawl_results
        WHERE id IN (
            SELECT MAX(id) FROM crawl_results GROUP BY target_name
        )
        ORDER BY crawled_at DESC
    """)
    rows = c.fetchall()
    conn.close()

    results = [
        {
            "target_name": row[0],
            "url": row[1],
            "status": row[2],
            "items_found": row[3],
            "duration_ms": row[4],
            "error_msg": row[5],
            "metadata": json.loads(row[6]) if row[6] else {},
            "crawled_at": row[7],
        }
        for row in rows
    ]

    crawler = get_crawler_service()
    active_targets = len(crawler.targets) if crawler else 0
    total_items = sum(r["items_found"] for r in results)

    return CrawlerStatusResponse(
        results=results, total_items=total_items, active_targets=active_targets
    )


@router.post("/run/{target_name}")
async def run_crawler(target_name: str):
    """Run crawler for a specific target"""
    crawler = get_crawler_service()

    if crawler is None:
        raise HTTPException(status_code=503, detail="Crawler service not available")

    result = await crawler.crawl_by_name(target_name)

    if result is None:
        raise HTTPException(status_code=404, detail=f"Target {target_name} not found")

    _store_crawl_result(result)

    return {
        "success": True,
        "target": target_name,
        "items_found": result.items_found,
        "status": result.status,
        "duration_ms": result.duration_ms,
    }


@router.post("/run-all")
async def run_all_crawlers():
    """Run all enabled crawlers"""
    crawler = get_crawler_service()

    if crawler is None:
        raise HTTPException(status_code=503, detail="Crawler service not available")

    results = await crawler.crawl_all()

    for result in results:
        _store_crawl_result(result)

    return {
        "success": True,
        "total_targets": len(results),
        "total_items": sum(r.items_found for r in results),
        "results": [
            {"target": r.target_name, "status": r.status, "items": r.items_found} for r in results
        ],
    }


@router.get("/targets")
async def list_targets():
    """List all configured crawler targets"""
    crawler = get_crawler_service()

    if crawler is None:
        return {"targets": []}

    targets = [
        {
            "name": t.name,
            "url": t.url,
            "enabled": t.enabled,
            "schedule": t.schedule,
            "category_count": len(t.category_urls),
        }
        for t in crawler.targets
    ]

    return {"targets": targets}
