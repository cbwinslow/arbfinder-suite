"""
API endpoints for price alerts functionality
"""

import json
import logging
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

DB_PATH = os.getenv("ARBF_DB", os.path.expanduser("~/.arb_finder.sqlite3"))


def init_alerts_table():
    """Initialize alerts table if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_query TEXT NOT NULL,
            min_price REAL,
            max_price REAL,
            notification_method TEXT NOT NULL,
            notification_target TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at REAL NOT NULL,
            last_triggered_at REAL,
            trigger_count INTEGER DEFAULT 0,
            metadata TEXT
        )
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS alert_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id INTEGER NOT NULL,
            listing_id INTEGER,
            listing_url TEXT,
            listing_title TEXT,
            listing_price REAL,
            matched_at REAL NOT NULL,
            notification_sent BOOLEAN DEFAULT 0,
            FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE
        )
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_alert_matches_alert_id ON alert_matches(alert_id)
    """)
    conn.commit()
    conn.close()


# Initialize table on module load
init_alerts_table()


class AlertCreate(BaseModel):
    """Model for creating a new alert"""

    search_query: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    notification_method: str = "email"  # email, webhook, or twitter
    notification_target: str  # email address, webhook URL, or twitter handle


class Alert(BaseModel):
    """Model for an alert"""

    id: int
    search_query: str
    min_price: Optional[float]
    max_price: Optional[float]
    notification_method: str
    notification_target: str
    status: str
    created_at: float
    last_triggered_at: Optional[float]
    trigger_count: int


class AlertsResponse(BaseModel):
    """Response model for alerts list"""

    alerts: List[Alert]
    total: int


class AlertMatch(BaseModel):
    """Model for an alert match"""

    id: int
    alert_id: int
    listing_url: Optional[str]
    listing_title: Optional[str]
    listing_price: float
    matched_at: float
    notification_sent: bool


@router.post("")
async def create_alert(alert: AlertCreate) -> Dict[str, Any]:
    """Create a new price alert"""
    # Validate price range
    if alert.min_price is not None and alert.max_price is not None:
        if alert.min_price >= alert.max_price:
            raise HTTPException(status_code=400, detail="min_price must be less than max_price")

    # Validate notification method
    valid_methods = ["email", "webhook", "twitter", "facebook"]
    if alert.notification_method not in valid_methods:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid notification method. Must be one of: {', '.join(valid_methods)}",
        )

    # Basic email validation for email method
    if alert.notification_method == "email" and "@" not in alert.notification_target:
        raise HTTPException(status_code=400, detail="Invalid email address")

    try:
        current_time = time.time()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO alerts (
                search_query, min_price, max_price, notification_method,
                notification_target, status, created_at, trigger_count
            ) VALUES (?, ?, ?, ?, ?, 'active', ?, 0)
        """,
            (
                alert.search_query,
                alert.min_price,
                alert.max_price,
                alert.notification_method,
                alert.notification_target,
                current_time,
            ),
        )
        alert_id = c.lastrowid
        conn.commit()
        conn.close()

        logger.info(
            f"Created alert {alert_id} for '{alert.search_query}' "
            f"(${alert.min_price}-${alert.max_price})"
        )

        return {
            "success": True,
            "alert_id": alert_id,
            "message": "Alert created successfully",
        }

    except Exception as e:
        logger.error(f"Error creating alert: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")


@router.get("", response_model=AlertsResponse)
async def list_alerts(
    status: Optional[str] = Query(None, regex="^(active|paused|deleted)$"),
    limit: int = Query(50, ge=1, le=200),
) -> AlertsResponse:
    """List price alerts"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Build query with optional status filter
    where_clause = ""
    params: List[Any] = []

    if status:
        where_clause = "WHERE status = ?"
        params.append(status)

    query = f"""
        SELECT id, search_query, min_price, max_price, notification_method,
               notification_target, status, created_at, last_triggered_at, trigger_count
        FROM alerts
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ?
    """
    params.append(limit)

    c.execute(query, params)
    rows = c.fetchall()

    # Get total count
    count_query = f"SELECT COUNT(*) FROM alerts {where_clause}"
    c.execute(count_query, params[:-1])  # Exclude limit
    total = c.fetchone()[0]

    conn.close()

    alerts = [
        Alert(
            id=row[0],
            search_query=row[1],
            min_price=row[2],
            max_price=row[3],
            notification_method=row[4],
            notification_target=row[5],
            status=row[6],
            created_at=row[7],
            last_triggered_at=row[8],
            trigger_count=row[9],
        )
        for row in rows
    ]

    return AlertsResponse(alerts=alerts, total=total)


@router.get("/{alert_id}", response_model=Alert)
async def get_alert(alert_id: int) -> Alert:
    """Get details of a specific alert"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        SELECT id, search_query, min_price, max_price, notification_method,
               notification_target, status, created_at, last_triggered_at, trigger_count
        FROM alerts
        WHERE id = ?
    """,
        (alert_id,),
    )
    row = c.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")

    return Alert(
        id=row[0],
        search_query=row[1],
        min_price=row[2],
        max_price=row[3],
        notification_method=row[4],
        notification_target=row[5],
        status=row[6],
        created_at=row[7],
        last_triggered_at=row[8],
        trigger_count=row[9],
    )


@router.delete("/{alert_id}")
async def delete_alert(alert_id: int) -> Dict[str, Any]:
    """Delete an alert"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if alert exists
    c.execute("SELECT id FROM alerts WHERE id = ?", (alert_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Alert not found")

    # Soft delete by updating status
    c.execute("UPDATE alerts SET status = 'deleted' WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()

    logger.info(f"Deleted alert {alert_id}")

    return {"success": True, "message": "Alert deleted successfully"}


@router.patch("/{alert_id}/pause")
async def pause_alert(alert_id: int) -> Dict[str, Any]:
    """Pause an active alert"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT status FROM alerts WHERE id = ?", (alert_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Alert not found")

    if row[0] != "active":
        conn.close()
        raise HTTPException(status_code=400, detail="Alert is not active")

    c.execute("UPDATE alerts SET status = 'paused' WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()

    return {"success": True, "message": "Alert paused successfully"}


@router.patch("/{alert_id}/resume")
async def resume_alert(alert_id: int) -> Dict[str, Any]:
    """Resume a paused alert"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT status FROM alerts WHERE id = ?", (alert_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Alert not found")

    if row[0] != "paused":
        conn.close()
        raise HTTPException(status_code=400, detail="Alert is not paused")

    c.execute("UPDATE alerts SET status = 'active' WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()

    return {"success": True, "message": "Alert resumed successfully"}


@router.get("/{alert_id}/matches")
async def get_alert_matches(
    alert_id: int, limit: int = Query(50, ge=1, le=200)
) -> Dict[str, Any]:
    """Get matches for a specific alert"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Verify alert exists
    c.execute("SELECT id FROM alerts WHERE id = ?", (alert_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Alert not found")

    # Get matches
    c.execute(
        """
        SELECT id, alert_id, listing_url, listing_title, listing_price,
               matched_at, notification_sent
        FROM alert_matches
        WHERE alert_id = ?
        ORDER BY matched_at DESC
        LIMIT ?
    """,
        (alert_id, limit),
    )
    rows = c.fetchall()

    # Get total count
    c.execute("SELECT COUNT(*) FROM alert_matches WHERE alert_id = ?", (alert_id,))
    total = c.fetchone()[0]

    conn.close()

    matches = [
        AlertMatch(
            id=row[0],
            alert_id=row[1],
            listing_url=row[2],
            listing_title=row[3],
            listing_price=row[4],
            matched_at=row[5],
            notification_sent=bool(row[6]),
        )
        for row in rows
    ]

    return {"matches": matches, "total": total}


@router.post("/check-and-notify")
async def check_alerts_and_notify() -> Dict[str, Any]:
    """Check active alerts against new listings and send notifications"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get all active alerts
    c.execute(
        """
        SELECT id, search_query, min_price, max_price, notification_method,
               notification_target, last_triggered_at
        FROM alerts
        WHERE status = 'active'
    """
    )
    alerts = c.fetchall()

    total_matches = 0
    notifications_sent = 0

    for alert_row in alerts:
        alert_id, search_query, min_price, max_price, notif_method, notif_target, last_triggered = (
            alert_row
        )

        # Build query to find matching listings
        query_conditions = ["title LIKE ?"]
        query_params = [f"%{search_query}%"]

        if min_price is not None:
            query_conditions.append("price >= ?")
            query_params.append(min_price)

        if max_price is not None:
            query_conditions.append("price <= ?")
            query_params.append(max_price)

        # Only check listings created since last trigger (or last hour if never triggered)
        time_threshold = last_triggered if last_triggered else (time.time() - 3600)
        query_conditions.append("ts > ?")
        query_params.append(time_threshold)

        query = f"""
            SELECT id, url, title, price
            FROM listings
            WHERE {' AND '.join(query_conditions)}
            ORDER BY ts DESC
            LIMIT 50
        """

        c.execute(query, query_params)
        matches = c.fetchall()

        if matches:
            current_time = time.time()

            # Record matches
            for match in matches:
                listing_id, listing_url, listing_title, listing_price = match

                c.execute(
                    """
                    INSERT INTO alert_matches (
                        alert_id, listing_id, listing_url, listing_title,
                        listing_price, matched_at, notification_sent
                    ) VALUES (?, ?, ?, ?, ?, ?, 0)
                """,
                    (alert_id, listing_id, listing_url, listing_title, listing_price, current_time),
                )

            total_matches += len(matches)

            # Send notification (simulated for now)
            try:
                if notif_method == "email":
                    # In production, integrate with email service (SendGrid, AWS SES, etc.)
                    logger.info(f"Would send email to {notif_target} about {len(matches)} matches")
                elif notif_method == "webhook":
                    # In production, call the webhook URL
                    logger.info(f"Would call webhook {notif_target} with {len(matches)} matches")
                elif notif_method in ["twitter", "facebook"]:
                    # In production, integrate with social media APIs
                    logger.info(
                        f"Would post to {notif_method} at {notif_target} about {len(matches)} matches"
                    )

                # Update alert last triggered time and count
                c.execute(
                    """
                    UPDATE alerts
                    SET last_triggered_at = ?, trigger_count = trigger_count + 1
                    WHERE id = ?
                """,
                    (current_time, alert_id),
                )

                # Mark notifications as sent
                c.execute(
                    """
                    UPDATE alert_matches
                    SET notification_sent = 1
                    WHERE alert_id = ? AND matched_at = ?
                """,
                    (alert_id, current_time),
                )

                notifications_sent += 1

            except Exception as e:
                logger.error(f"Failed to send notification for alert {alert_id}: {str(e)}")

    conn.commit()
    conn.close()

    return {
        "success": True,
        "alerts_checked": len(alerts),
        "total_matches": total_matches,
        "notifications_sent": notifications_sent,
    }
