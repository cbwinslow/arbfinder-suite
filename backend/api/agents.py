"""
API endpoints for AI agent management and monitoring
"""

import json
import logging
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/agents", tags=["agents"])

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("ARBF_DB", os.path.expanduser("~/.arb_finder.sqlite3"))

VALID_AGENT_TYPES = [
    "web_crawler",
    "data_validator",
    "market_researcher",
    "price_specialist",
    "listing_writer",
    "image_processor",
    "metadata_enricher",
    "title_enhancer",
    "crosslister",
    "quality_monitor",
]

VALID_STATUS_PATTERN = "^(queued|running|completed|failed)$"


def init_agent_jobs_table():
    """Initialize agent_jobs table if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS agent_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_type TEXT NOT NULL,
            status TEXT DEFAULT 'queued',
            input_data TEXT,
            output_data TEXT,
            error_msg TEXT,
            started_at REAL NOT NULL,
            completed_at REAL,
            duration INTEGER
        )
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_jobs_status ON agent_jobs(status)
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_jobs_type ON agent_jobs(agent_type)
    """)
    conn.commit()
    conn.close()


# Initialize table on module load
init_agent_jobs_table()


class AgentJob(BaseModel):
    """Model for agent job"""

    id: int
    agentType: str
    status: str
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    errorMsg: Optional[str] = None
    startedAt: float
    completedAt: Optional[float] = None
    duration: Optional[int] = None


class AgentJobsResponse(BaseModel):
    """Response model for agent jobs"""

    jobs: List[AgentJob]
    total: int


def _row_to_job(row) -> AgentJob:
    """Convert a DB row to an AgentJob model."""
    return AgentJob(
        id=row[0],
        agentType=row[1],
        status=row[2],
        input=json.loads(row[3]) if row[3] else None,
        output=json.loads(row[4]) if row[4] else None,
        errorMsg=row[5],
        startedAt=row[6],
        completedAt=row[7],
        duration=row[8],
    )


@router.get("/jobs", response_model=AgentJobsResponse)
async def get_agent_jobs(
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, pattern=VALID_STATUS_PATTERN),
    agent_type: Optional[str] = None,
):
    """Get list of agent jobs"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    where_clauses = []
    params: List[Any] = []

    if status:
        where_clauses.append("status = ?")
        params.append(status)

    if agent_type:
        where_clauses.append("agent_type = ?")
        params.append(agent_type)

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    count_query = f"SELECT COUNT(*) FROM agent_jobs {where_sql}"
    total = c.execute(count_query, params).fetchone()[0]

    query = f"""
        SELECT id, agent_type, status, input_data, output_data, error_msg,
               started_at, completed_at, duration
        FROM agent_jobs
        {where_sql}
        ORDER BY started_at DESC
        LIMIT ?
    """
    params.append(limit)
    rows = c.execute(query, params).fetchall()
    conn.close()

    jobs = [_row_to_job(r) for r in rows]
    return AgentJobsResponse(jobs=jobs, total=total)


@router.get("/jobs/{job_id}", response_model=AgentJob)
async def get_agent_job(job_id: int):
    """Get details of a specific agent job"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    row = c.execute(
        """
        SELECT id, agent_type, status, input_data, output_data, error_msg,
               started_at, completed_at, duration
        FROM agent_jobs
        WHERE id = ?
        """,
        (job_id,),
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Job not found")

    return _row_to_job(row)


@router.post("/jobs")
async def create_agent_job(agent_type: str, input_data: Optional[Dict[str, Any]] = None):
    """Create a new agent job"""
    if agent_type not in VALID_AGENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent type. Must be one of: {', '.join(VALID_AGENT_TYPES)}",
        )

    current_time = time.time()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO agent_jobs (agent_type, status, input_data, started_at)
        VALUES (?, 'queued', ?, ?)
        """,
        (agent_type, json.dumps(input_data) if input_data else None, current_time),
    )
    job_id = c.lastrowid
    conn.commit()
    conn.close()

    logger.info(f"Created agent job {job_id} for agent: {agent_type}")

    return {
        "success": True,
        "job_id": job_id,
        "agent_type": agent_type,
        "status": "queued",
        "message": "Job created successfully",
    }


@router.get("/types")
async def list_agent_types():
    """List all available agent types"""
    agent_types = [
        {
            "type": "web_crawler",
            "name": "Web Crawler",
            "description": "Crawls target websites and extracts price data",
            "icon": "🕷️",
        },
        {
            "type": "data_validator",
            "name": "Data Validator",
            "description": "Validates and cleans incoming data",
            "icon": "✅",
        },
        {
            "type": "market_researcher",
            "name": "Market Researcher",
            "description": "Researches market prices and trends",
            "icon": "📊",
        },
        {
            "type": "price_specialist",
            "name": "Price Specialist",
            "description": "Computes optimal pricing strategies",
            "icon": "💰",
        },
        {
            "type": "listing_writer",
            "name": "Listing Writer",
            "description": "Creates SEO-optimized product listings",
            "icon": "✍️",
        },
        {
            "type": "image_processor",
            "name": "Image Processor",
            "description": "Processes and optimizes product images",
            "icon": "🖼️",
        },
        {
            "type": "metadata_enricher",
            "name": "Metadata Enricher",
            "description": "Enriches missing metadata fields",
            "icon": "🔍",
        },
        {
            "type": "title_enhancer",
            "name": "Title Enhancer",
            "description": "Enhances product titles",
            "icon": "📝",
        },
        {
            "type": "crosslister",
            "name": "Cross-lister",
            "description": "Posts listings to multiple platforms",
            "icon": "📤",
        },
        {
            "type": "quality_monitor",
            "name": "Quality Monitor",
            "description": "Monitors data quality and compliance",
            "icon": "👁️",
        },
    ]

    return {"agent_types": agent_types}
