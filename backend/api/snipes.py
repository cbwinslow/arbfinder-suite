"""
API endpoints for auction sniping functionality
"""

import logging
import os
import sqlite3
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/snipes", tags=["snipes"])

DB_PATH = os.getenv("ARBF_DB", os.path.expanduser("~/.arb_finder.sqlite3"))


def init_snipes_table():
    """Initialize snipes table if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS snipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_url TEXT NOT NULL,
            listing_title TEXT,
            max_bid REAL NOT NULL,
            auction_end_time REAL NOT NULL,
            lead_time_seconds INTEGER DEFAULT 5,
            status TEXT DEFAULT 'scheduled',
            created_at REAL NOT NULL,
            executed_at REAL,
            result TEXT,
            metadata TEXT
        )
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_snipes_status ON snipes(status)
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_snipes_auction_end ON snipes(auction_end_time)
    """)
    conn.commit()
    conn.close()


# Initialize table on module load
init_snipes_table()


class SnipeCreate(BaseModel):
    """Model for creating a new snipe"""

    listing_url: str
    listing_title: Optional[str] = None
    max_bid: float
    auction_end_time: str  # ISO 8601 format
    lead_time_seconds: int = 5


class Snipe(BaseModel):
    """Model for a snipe"""

    id: int
    listing_url: str
    listing_title: Optional[str]
    max_bid: float
    auction_end_time: float
    lead_time_seconds: int
    status: str
    created_at: float
    executed_at: Optional[float]
    result: Optional[str]


class SnipesResponse(BaseModel):
    """Response model for snipes list"""

    snipes: List[Snipe]
    total: int


@router.post("")
async def create_snipe(snipe: SnipeCreate) -> Dict[str, Any]:
    """Schedule a new auction snipe"""
    try:
        # Parse auction end time
        auction_end_dt = datetime.fromisoformat(snipe.auction_end_time.replace("Z", "+00:00"))
        auction_end_ts = auction_end_dt.timestamp()

        # Validate that auction end time is in the future
        current_time = time.time()
        if auction_end_ts <= current_time:
            raise HTTPException(status_code=400, detail="Auction end time must be in the future")

        # Validate lead time
        if snipe.lead_time_seconds < 1 or snipe.lead_time_seconds > 300:
            raise HTTPException(
                status_code=400, detail="Lead time must be between 1 and 300 seconds"
            )

        # Insert into database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO snipes (
                listing_url, listing_title, max_bid, auction_end_time,
                lead_time_seconds, status, created_at
            ) VALUES (?, ?, ?, ?, ?, 'scheduled', ?)
        """,
            (
                snipe.listing_url,
                snipe.listing_title,
                snipe.max_bid,
                auction_end_ts,
                snipe.lead_time_seconds,
                current_time,
            ),
        )
        snipe_id = c.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Created snipe {snipe_id} for auction ending at {snipe.auction_end_time}")

        return {
            "success": True,
            "snipe_id": snipe_id,
            "message": "Snipe scheduled successfully",
            "execute_at": auction_end_ts - snipe.lead_time_seconds,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating snipe: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create snipe: {str(e)}")


@router.get("", response_model=SnipesResponse)
async def list_snipes(
    status: Optional[str] = Query(None, regex="^(scheduled|executed|cancelled|failed)$"),
    limit: int = Query(50, ge=1, le=200),
) -> SnipesResponse:
    """List scheduled snipes"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Build query with optional status filter
    where_clause = ""
    params: List[Any] = []

    if status:
        where_clause = "WHERE status = ?"
        params.append(status)

    query = f"""
        SELECT id, listing_url, listing_title, max_bid, auction_end_time,
               lead_time_seconds, status, created_at, executed_at, result
        FROM snipes
        {where_clause}
        ORDER BY auction_end_time DESC
        LIMIT ?
    """
    params.append(limit)

    c.execute(query, params)
    rows = c.fetchall()

    # Get total count
    count_query = f"SELECT COUNT(*) FROM snipes {where_clause}"
    c.execute(count_query, params[:-1])  # Exclude limit
    total = c.fetchone()[0]

    conn.close()

    snipes = [
        Snipe(
            id=row[0],
            listing_url=row[1],
            listing_title=row[2],
            max_bid=row[3],
            auction_end_time=row[4],
            lead_time_seconds=row[5],
            status=row[6],
            created_at=row[7],
            executed_at=row[8],
            result=row[9],
        )
        for row in rows
    ]

    return SnipesResponse(snipes=snipes, total=total)


@router.get("/{snipe_id}", response_model=Snipe)
async def get_snipe(snipe_id: int) -> Snipe:
    """Get details of a specific snipe"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        SELECT id, listing_url, listing_title, max_bid, auction_end_time,
               lead_time_seconds, status, created_at, executed_at, result
        FROM snipes
        WHERE id = ?
    """,
        (snipe_id,),
    )
    row = c.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Snipe not found")

    return Snipe(
        id=row[0],
        listing_url=row[1],
        listing_title=row[2],
        max_bid=row[3],
        auction_end_time=row[4],
        lead_time_seconds=row[5],
        status=row[6],
        created_at=row[7],
        executed_at=row[8],
        result=row[9],
    )


@router.delete("/{snipe_id}")
async def cancel_snipe(snipe_id: int) -> Dict[str, Any]:
    """Cancel a scheduled snipe"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if snipe exists and is scheduled
    c.execute("SELECT status FROM snipes WHERE id = ?", (snipe_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Snipe not found")

    if row[0] != "scheduled":
        conn.close()
        raise HTTPException(
            status_code=400, detail=f"Cannot cancel snipe with status '{row[0]}'"
        )

    # Update status to cancelled
    c.execute("UPDATE snipes SET status = 'cancelled' WHERE id = ?", (snipe_id,))
    conn.commit()
    conn.close()

    logger.info(f"Cancelled snipe {snipe_id}")

    return {"success": True, "message": "Snipe cancelled successfully"}


@router.post("/execute-pending")
async def execute_pending_snipes() -> Dict[str, Any]:
    """Execute snipes that are due (called by cron/scheduler)"""
    current_time = time.time()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Find snipes that should be executed now
    c.execute(
        """
        SELECT id, listing_url, max_bid, auction_end_time, lead_time_seconds
        FROM snipes
        WHERE status = 'scheduled'
        AND (auction_end_time - lead_time_seconds) <= ?
    """,
        (current_time,),
    )
    rows = c.fetchall()

    executed_count = 0
    failed_count = 0

    for row in rows:
        snipe_id, listing_url, max_bid, auction_end_time, lead_time_seconds = row

        try:
            # TODO: PRODUCTION INTEGRATION REQUIRED
            # Integrate with actual auction platform APIs (eBay, ShopGoodwill, etc.)
            # This is currently a simulation for testing purposes
            # Required steps:
            # 1. Identify auction platform from listing_url
            # 2. Call platform's bidding API with authentication
            # 3. Handle rate limits and retries
            # 4. Verify bid was placed successfully
            result = f"Bid of ${max_bid} placed successfully (SIMULATED)"

            c.execute(
                """
                UPDATE snipes
                SET status = 'executed', executed_at = ?, result = ?
                WHERE id = ?
            """,
                (current_time, result, snipe_id),
            )
            executed_count += 1
            logger.info(f"Executed snipe {snipe_id} for {listing_url}")

        except Exception as e:
            error_msg = f"Failed to execute bid: {str(e)}"
            c.execute(
                """
                UPDATE snipes
                SET status = 'failed', executed_at = ?, result = ?
                WHERE id = ?
            """,
                (current_time, error_msg, snipe_id),
            )
            failed_count += 1
            logger.error(f"Failed to execute snipe {snipe_id}: {str(e)}")

    conn.commit()
    conn.close()

    return {
        "success": True,
        "executed": executed_count,
        "failed": failed_count,
        "message": f"Processed {executed_count + failed_count} pending snipes",
    }
