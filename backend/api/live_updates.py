"""
API endpoints for live updates and activity feed
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["updates"])

logger = logging.getLogger(__name__)


class Update(BaseModel):
    """Model for live update"""

    id: int
    timestamp: str
    type: str
    message: str
    data: Optional[Dict[str, Any]] = None


class LiveUpdatesResponse(BaseModel):
    """Response model for live updates"""

    updates: List[Update]
    total: int


@router.get("/live-updates", response_model=LiveUpdatesResponse)
async def get_live_updates(limit: int = Query(50, ge=1, le=200), type_filter: Optional[str] = None):
    """Get live activity updates"""
    # Generate mock updates for demonstration
    base_time = datetime.utcnow()

    mock_updates = [
        Update(
            id=1,
            timestamp=(base_time - timedelta(seconds=5)).isoformat() + "Z",
            type="crawler",
            message="ShopGoodwill crawler completed: 45 items found",
        ),
        Update(
            id=2,
            timestamp=(base_time - timedelta(seconds=12)).isoformat() + "Z",
            type="agent",
            message="Data validator started processing batch #234",
        ),
        Update(
            id=3,
            timestamp=(base_time - timedelta(seconds=18)).isoformat() + "Z",
            type="price",
            message="Price specialist updated 15 item prices",
        ),
        Update(
            id=4,
            timestamp=(base_time - timedelta(seconds=25)).isoformat() + "Z",
            type="success",
            message="Image processor uploaded 8 images to Cloudflare R2",
        ),
        Update(
            id=5,
            timestamp=(base_time - timedelta(seconds=32)).isoformat() + "Z",
            type="crawler",
            message="GovDeals crawler started",
        ),
        Update(
            id=6,
            timestamp=(base_time - timedelta(seconds=45)).isoformat() + "Z",
            type="metadata",
            message="Metadata enricher filled 23 missing fields",
        ),
        Update(
            id=7,
            timestamp=(base_time - timedelta(seconds=58)).isoformat() + "Z",
            type="agent",
            message="Listing writer created 12 new listings",
        ),
        Update(
            id=8,
            timestamp=(base_time - timedelta(seconds=72)).isoformat() + "Z",
            type="crawler",
            message="GovDeals crawler completed: 32 items found",
        ),
        Update(
            id=9,
            timestamp=(base_time - timedelta(seconds=89)).isoformat() + "Z",
            type="error",
            message="Market researcher: API rate limit exceeded, retrying in 60s",
        ),
        Update(
            id=10,
            timestamp=(base_time - timedelta(seconds=105)).isoformat() + "Z",
            type="image",
            message="Image processor started batch processing",
        ),
        Update(
            id=11,
            timestamp=(base_time - timedelta(seconds=120)).isoformat() + "Z",
            type="success",
            message="Quality monitor: All checks passed",
        ),
        Update(
            id=12,
            timestamp=(base_time - timedelta(seconds=135)).isoformat() + "Z",
            type="crawler",
            message="GovernmentSurplus crawler started",
        ),
        Update(
            id=13,
            timestamp=(base_time - timedelta(seconds=150)).isoformat() + "Z",
            type="agent",
            message="Cross-lister posted 5 items to eBay",
        ),
        Update(
            id=14,
            timestamp=(base_time - timedelta(seconds=165)).isoformat() + "Z",
            type="price",
            message="Price specialist analyzing market trends",
        ),
        Update(
            id=15,
            timestamp=(base_time - timedelta(seconds=180)).isoformat() + "Z",
            type="info",
            message="System health check: All services operational",
        ),
    ]

    # Filter by type if provided
    if type_filter:
        mock_updates = [u for u in mock_updates if u.type == type_filter]

    # Apply limit
    filtered_updates = mock_updates[:limit]

    return LiveUpdatesResponse(updates=filtered_updates, total=len(mock_updates))


@router.get("/activity-stats")
async def get_activity_stats():
    """Get activity statistics"""
    return {
        "last_hour": {"crawls": 12, "items_found": 245, "agent_jobs": 45, "errors": 2},
        "last_24_hours": {"crawls": 156, "items_found": 3420, "agent_jobs": 892, "errors": 15},
        "uptime_seconds": 86400,
        "active_crawlers": 3,
        "active_agents": 5,
    }
