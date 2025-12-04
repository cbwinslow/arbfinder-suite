"""
API endpoints for crawler management and monitoring
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import logging

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

# Global crawler instance
_crawler_service = None


def get_crawler_service():
    """Get or create crawler service instance"""
    global _crawler_service
    if _crawler_service is None and CrawlerService is not None:
        _crawler_service = CrawlerService()
    return _crawler_service


class CrawlerStatusResponse(BaseModel):
    """Response model for crawler status"""
    results: List[Dict[str, Any]]
    total_items: int
    active_targets: int


@router.get("/status", response_model=CrawlerStatusResponse)
async def get_crawler_status():
    """Get current status of all crawlers"""
    crawler = get_crawler_service()
    
    if crawler is None:
        return CrawlerStatusResponse(
            results=[],
            total_items=0,
            active_targets=0
        )
    
    # Get mock data for now (replace with actual DB queries in production)
    results = [
        {
            "target_name": "shopgoodwill",
            "url": "https://shopgoodwill.com",
            "status": "success",
            "items_found": 45,
            "duration_ms": 3500,
            "metadata": {"timestamp": "2024-12-04T07:00:00Z"}
        },
        {
            "target_name": "govdeals",
            "url": "https://www.govdeals.com",
            "status": "success",
            "items_found": 32,
            "duration_ms": 2800,
            "metadata": {"timestamp": "2024-12-04T07:05:00Z"}
        },
        {
            "target_name": "governmentsurplus",
            "url": "https://www.governmentsurplus.com",
            "status": "partial",
            "items_found": 18,
            "duration_ms": 4200,
            "error_msg": "Timeout on category page 3",
            "metadata": {"timestamp": "2024-12-04T07:10:00Z"}
        }
    ]
    
    total_items = sum(r.get("items_found", 0) for r in results)
    active_targets = len(crawler.targets) if crawler else 0
    
    return CrawlerStatusResponse(
        results=results,
        total_items=total_items,
        active_targets=active_targets
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
    
    return {
        "success": True,
        "target": target_name,
        "items_found": result.items_found,
        "status": result.status,
        "duration_ms": result.duration_ms
    }


@router.post("/run-all")
async def run_all_crawlers():
    """Run all enabled crawlers"""
    crawler = get_crawler_service()
    
    if crawler is None:
        raise HTTPException(status_code=503, detail="Crawler service not available")
    
    results = await crawler.crawl_all()
    
    return {
        "success": True,
        "total_targets": len(results),
        "total_items": sum(r.items_found for r in results),
        "results": [
            {
                "target": r.target_name,
                "status": r.status,
                "items": r.items_found
            }
            for r in results
        ]
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
            "category_count": len(t.category_urls)
        }
        for t in crawler.targets
    ]
    
    return {"targets": targets}
