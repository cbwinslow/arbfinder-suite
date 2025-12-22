"""
API endpoints for running Crawl4AI/CrewAI agents and crews
"""

import json
import logging
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/crews", tags=["crews"])

DB_PATH = os.getenv("ARBF_DB", os.path.expanduser("~/.arb_finder.sqlite3"))


def init_crews_table():
    """Initialize crews table if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS crew_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crew_type TEXT NOT NULL,
            targets TEXT,
            query TEXT,
            status TEXT DEFAULT 'queued',
            started_at REAL NOT NULL,
            completed_at REAL,
            duration_seconds REAL,
            items_processed INTEGER DEFAULT 0,
            items_created INTEGER DEFAULT 0,
            error_message TEXT,
            result_data TEXT
        )
    """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_crew_runs_status ON crew_runs(status)
    """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_crew_runs_type ON crew_runs(crew_type)
    """
    )
    conn.commit()
    conn.close()


# Initialize table on module load
init_crews_table()


class CrewRunRequest(BaseModel):
    """Model for requesting a crew run"""

    crew_type: str  # price_ingestion, metadata_enrichment, listing_generation, etc.
    targets: Optional[List[str]] = None  # e.g., ["shopgoodwill", "govdeals"]
    query: Optional[str] = None  # search query for crawlers
    config: Optional[Dict[str, Any]] = None  # additional configuration


class CrewRun(BaseModel):
    """Model for a crew run"""

    id: int
    crew_type: str
    targets: Optional[str]
    query: Optional[str]
    status: str
    started_at: float
    completed_at: Optional[float]
    duration_seconds: Optional[float]
    items_processed: int
    items_created: int
    error_message: Optional[str]


class CrewRunsResponse(BaseModel):
    """Response model for crew runs list"""

    runs: List[CrewRun]
    total: int


@router.post("/run")
async def start_crew_run(request: CrewRunRequest) -> Dict[str, Any]:
    """Start a new crew run"""
    # Validate crew type
    valid_crew_types = [
        "price_ingestion",
        "metadata_enrichment",
        "listing_generation",
        "market_research",
        "image_processing",
        "quality_check",
    ]

    if request.crew_type not in valid_crew_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid crew type. Must be one of: {', '.join(valid_crew_types)}",
        )

    try:
        current_time = time.time()
        targets_json = json.dumps(request.targets) if request.targets else None

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO crew_runs (
                crew_type, targets, query, status, started_at,
                items_processed, items_created
            ) VALUES (?, ?, ?, 'queued', ?, 0, 0)
        """,
            (request.crew_type, targets_json, request.query, current_time),
        )
        run_id = c.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Started crew run {run_id} of type '{request.crew_type}'")

        # In production, this would trigger the actual crew execution
        # For now, we'll simulate it by immediately updating to 'running'
        # and the actual execution would happen via a queue worker

        return {
            "success": True,
            "run_id": run_id,
            "crew_type": request.crew_type,
            "status": "queued",
            "message": "Crew run started successfully",
        }

    except Exception as e:
        logger.error(f"Error starting crew run: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start crew run: {str(e)}")


@router.get("/runs", response_model=CrewRunsResponse)
async def list_crew_runs(
    crew_type: Optional[str] = None,
    status: Optional[str] = Query(None, regex="^(queued|running|completed|failed)$"),
    limit: int = Query(50, ge=1, le=200),
) -> CrewRunsResponse:
    """List crew runs"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Build query with optional filters
    where_clauses = []
    params: List[Any] = []

    if crew_type:
        where_clauses.append("crew_type = ?")
        params.append(crew_type)

    if status:
        where_clauses.append("status = ?")
        params.append(status)

    where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    query = f"""
        SELECT id, crew_type, targets, query, status, started_at, completed_at,
               duration_seconds, items_processed, items_created, error_message
        FROM crew_runs
        {where_clause}
        ORDER BY started_at DESC
        LIMIT ?
    """
    params.append(limit)

    c.execute(query, params)
    rows = c.fetchall()

    # Get total count
    count_query = f"SELECT COUNT(*) FROM crew_runs {where_clause}"
    c.execute(count_query, params[:-1])  # Exclude limit
    total = c.fetchone()[0]

    conn.close()

    runs = [
        CrewRun(
            id=row[0],
            crew_type=row[1],
            targets=row[2],
            query=row[3],
            status=row[4],
            started_at=row[5],
            completed_at=row[6],
            duration_seconds=row[7],
            items_processed=row[8],
            items_created=row[9],
            error_message=row[10],
        )
        for row in rows
    ]

    return CrewRunsResponse(runs=runs, total=total)


@router.get("/status/{run_id}")
async def get_crew_status(run_id: int) -> Dict[str, Any]:
    """Get status of a specific crew run"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        SELECT id, crew_type, targets, query, status, started_at, completed_at,
               duration_seconds, items_processed, items_created, error_message
        FROM crew_runs
        WHERE id = ?
    """,
        (run_id,),
    )
    row = c.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Crew run not found")

    return {
        "id": row[0],
        "crew_type": row[1],
        "targets": json.loads(row[2]) if row[2] else None,
        "query": row[3],
        "status": row[4],
        "started_at": row[5],
        "completed_at": row[6],
        "duration_seconds": row[7],
        "items_processed": row[8],
        "items_created": row[9],
        "error_message": row[10],
    }


@router.get("/results/{run_id}")
async def get_crew_results(run_id: int) -> Dict[str, Any]:
    """Get results of a completed crew run"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        SELECT status, result_data, items_processed, items_created, error_message
        FROM crew_runs
        WHERE id = ?
    """,
        (run_id,),
    )
    row = c.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Crew run not found")

    status = row[0]
    if status not in ["completed", "failed"]:
        raise HTTPException(
            status_code=400, detail=f"Crew run is still {status}, results not available yet"
        )

    result_data = json.loads(row[1]) if row[1] else {}

    return {
        "success": status == "completed",
        "items_processed": row[2],
        "items_created": row[3],
        "error_message": row[4],
        "results": result_data,
    }


@router.post("/cancel/{run_id}")
async def cancel_crew_run(run_id: int) -> Dict[str, Any]:
    """Cancel a running or queued crew run"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT status FROM crew_runs WHERE id = ?", (run_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Crew run not found")

    status = row[0]
    if status not in ["queued", "running"]:
        conn.close()
        raise HTTPException(
            status_code=400, detail=f"Cannot cancel crew run with status '{status}'"
        )

    # Update status
    current_time = time.time()
    c.execute(
        """
        UPDATE crew_runs
        SET status = 'failed', completed_at = ?, error_message = 'Cancelled by user'
        WHERE id = ?
    """,
        (current_time, run_id),
    )
    conn.commit()
    conn.close()

    logger.info(f"Cancelled crew run {run_id}")

    return {"success": True, "message": "Crew run cancelled successfully"}


@router.get("/types")
async def list_crew_types() -> Dict[str, Any]:
    """List available crew types and their descriptions"""
    crew_types = [
        {
            "type": "price_ingestion",
            "name": "Price Data Ingestion",
            "description": "Crawl marketplaces and ingest price data using Crawl4AI",
            "icon": "💰",
            "agents": ["web_crawler", "data_validator", "price_specialist"],
        },
        {
            "type": "metadata_enrichment",
            "name": "Metadata Enrichment",
            "description": "Enrich product metadata using AI agents",
            "icon": "🔍",
            "agents": ["metadata_enricher", "image_processor", "title_enhancer"],
        },
        {
            "type": "listing_generation",
            "name": "Listing Generation",
            "description": "Generate optimized product listings for multiple platforms",
            "icon": "✍️",
            "agents": ["listing_writer", "seo_optimizer", "quality_monitor"],
        },
        {
            "type": "market_research",
            "name": "Market Research",
            "description": "Analyze market trends and pricing strategies",
            "icon": "📊",
            "agents": ["market_researcher", "price_specialist", "trend_analyzer"],
        },
        {
            "type": "image_processing",
            "name": "Image Processing",
            "description": "Process and optimize product images",
            "icon": "🖼️",
            "agents": ["image_processor", "background_remover", "quality_enhancer"],
        },
        {
            "type": "quality_check",
            "name": "Quality Check",
            "description": "Verify data quality and compliance",
            "icon": "✅",
            "agents": ["quality_monitor", "data_validator", "compliance_checker"],
        },
    ]

    return {"crew_types": crew_types}


@router.post("/simulate/{run_id}")
async def simulate_crew_completion(run_id: int) -> Dict[str, Any]:
    """Simulate completion of a crew run (for testing)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT status, started_at FROM crew_runs WHERE id = ?", (run_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Crew run not found")

    if row[0] not in ["queued", "running"]:
        conn.close()
        raise HTTPException(
            status_code=400, detail=f"Cannot simulate completion for status '{row[0]}'"
        )

    current_time = time.time()
    duration = current_time - row[1]

    # Simulate successful completion
    result_data = json.dumps(
        {
            "message": "Crew run completed successfully",
            "details": "This is a simulated completion for testing purposes",
        }
    )

    c.execute(
        """
        UPDATE crew_runs
        SET status = 'completed',
            completed_at = ?,
            duration_seconds = ?,
            items_processed = 45,
            items_created = 32,
            result_data = ?
        WHERE id = ?
    """,
        (current_time, duration, result_data, run_id),
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Crew run marked as completed (simulated)",
        "run_id": run_id,
    }
