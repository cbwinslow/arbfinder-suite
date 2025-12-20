"""
Historical Data Fetcher
Uses Wayback Machine API to access historical price and item data
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class HistoricalDataFetcher:
    """Fetch historical data using Wayback Machine"""

    def __init__(self, site_url: str):
        """Initialize historical data fetcher"""
        self.site_url = site_url.rstrip("/")
        self.wayback_api = "https://archive.org/wayback/available"
        self.wayback_cdx_api = "https://web.archive.org/cdx/search/cdx"
        self.user_agent = "ArbFinder-Bot/1.0"

    async def check_availability(self) -> Dict[str, Any]:
        """
        Check if historical snapshots are available for the site

        Returns:
            Dict containing availability information
        """
        logger.info(f"Checking Wayback Machine availability for {self.site_url}")

        results = {
            "available": False,
            "snapshot_count": 0,
            "first_snapshot": None,
            "last_snapshot": None,
            "date_range": None,
        }

        try:
            # Query Wayback Machine CDX API for snapshot count
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get first and last snapshot
                params = {
                    "url": self.site_url,
                    "output": "json",
                    "limit": "1",
                }

                # Get first snapshot
                first_response = await client.get(
                    self.wayback_cdx_api,
                    params=params,
                    headers={"User-Agent": self.user_agent},
                )

                if first_response.status_code == 200:
                    first_data = first_response.json()
                    if len(first_data) > 1:  # First row is headers
                        results["available"] = True
                        first_snapshot = first_data[1]
                        results["first_snapshot"] = self._parse_timestamp(first_snapshot[1])

                # Get last snapshot (most recent)
                params["fl"] = "timestamp"
                params["filter"] = "statuscode:200"
                params["limit"] = "-1"  # Get most recent

                last_response = await client.get(
                    self.wayback_cdx_api,
                    params=params,
                    headers={"User-Agent": self.user_agent},
                )

                if last_response.status_code == 200:
                    last_data = last_response.json()
                    if len(last_data) > 1:
                        last_snapshot = last_data[1]
                        results["last_snapshot"] = self._parse_timestamp(last_snapshot[1])

                # Count total snapshots (approximate)
                count_params = {
                    "url": self.site_url,
                    "output": "json",
                    "showNumPages": "true",
                }

                count_response = await client.get(
                    self.wayback_cdx_api,
                    params=count_params,
                    headers={"User-Agent": self.user_agent},
                )

                if count_response.status_code == 200:
                    count_data = count_response.json()
                    if count_data and len(count_data) > 0:
                        results["snapshot_count"] = len(count_data) - 1  # Exclude header

                # Build date range
                if results["first_snapshot"] and results["last_snapshot"]:
                    results["date_range"] = {
                        "from": results["first_snapshot"],
                        "to": results["last_snapshot"],
                    }

        except Exception as e:
            logger.error(f"Error checking Wayback Machine: {e}")

        return results

    async def get_snapshots(
        self,
        url: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get list of snapshots for a specific URL

        Args:
            url: Specific URL to get snapshots for
            from_date: Start date for snapshots
            to_date: End date for snapshots
            limit: Maximum number of snapshots to return

        Returns:
            List of snapshot metadata
        """
        snapshots = []

        try:
            params = {
                "url": url,
                "output": "json",
                "limit": str(limit),
                "filter": "statuscode:200",
            }

            # Add date filters if provided
            if from_date:
                params["from"] = from_date.strftime("%Y%m%d")
            if to_date:
                params["to"] = to_date.strftime("%Y%m%d")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.wayback_cdx_api,
                    params=params,
                    headers={"User-Agent": self.user_agent},
                )

                if response.status_code == 200:
                    data = response.json()

                    # Skip header row
                    for row in data[1:]:
                        if len(row) >= 5:
                            snapshot = {
                                "urlkey": row[0],
                                "timestamp": self._parse_timestamp(row[1]),
                                "original_url": row[2],
                                "mimetype": row[3],
                                "statuscode": row[4],
                                "wayback_url": self._build_wayback_url(row[1], row[2]),
                            }
                            snapshots.append(snapshot)

        except Exception as e:
            logger.error(f"Error fetching snapshots: {e}")

        return snapshots

    async def fetch_snapshot(self, url: str, timestamp: str) -> Optional[str]:
        """
        Fetch content from a specific snapshot

        Args:
            url: Original URL
            timestamp: Wayback timestamp (format: YYYYMMDDhhmmss)

        Returns:
            Snapshot content as string, or None if not available
        """
        wayback_url = self._build_wayback_url(timestamp, url)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    wayback_url,
                    headers={"User-Agent": self.user_agent},
                    follow_redirects=True,
                )

                if response.status_code == 200:
                    return response.text

        except Exception as e:
            logger.error(f"Error fetching snapshot from {wayback_url}: {e}")

        return None

    async def get_historical_prices(
        self,
        item_url: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get historical price data for an item by analyzing snapshots

        Args:
            item_url: URL of the specific item/listing
            from_date: Start date for analysis
            to_date: End date for analysis

        Returns:
            List of price data points with timestamps
        """
        price_history = []

        # Get snapshots for the item URL
        snapshots = await self.get_snapshots(
            item_url, from_date=from_date, to_date=to_date, limit=50
        )

        logger.info(f"Found {len(snapshots)} snapshots for {item_url}")

        # Fetch and parse each snapshot (with rate limiting)
        for i, snapshot in enumerate(snapshots):
            try:
                # Rate limit: wait between requests
                if i > 0:
                    await asyncio.sleep(2)

                content = await self.fetch_snapshot(
                    snapshot["original_url"], snapshot["timestamp"].replace("-", "")
                )

                if content:
                    # Parse price from content (site-specific logic needed)
                    price_data = self._extract_price_from_html(content, snapshot["timestamp"])
                    if price_data:
                        price_history.append(price_data)

            except Exception as e:
                logger.error(f"Error processing snapshot: {e}")

        return price_history

    def _parse_timestamp(self, timestamp: str) -> str:
        """Convert Wayback timestamp to ISO format"""
        try:
            # Wayback format: YYYYMMDDhhmmss
            dt = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
            return dt.isoformat()
        except Exception:
            return timestamp

    def _build_wayback_url(self, timestamp: str, original_url: str) -> str:
        """Build Wayback Machine URL for a snapshot"""
        # Remove any special formatting from timestamp
        timestamp = timestamp.replace("-", "").replace(":", "").replace("T", "")[:14]
        return f"https://web.archive.org/web/{timestamp}/{original_url}"

    def _extract_price_from_html(self, html: str, timestamp: str) -> Optional[Dict[str, Any]]:
        """
        Extract price from HTML snapshot

        Note: This is site-specific and would need customization
        per target site's HTML structure
        """
        try:
            import re

            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")

            # Common price selectors (customize per site)
            price_selectors = [
                ".price",
                ".item-price",
                "[class*='price']",
                "[id*='price']",
            ]

            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text()

                    # Extract numeric price
                    price_match = re.search(r"\$?(\d+(?:\.\d{2})?)", price_text)
                    if price_match:
                        return {
                            "timestamp": timestamp,
                            "price": float(price_match.group(1)),
                            "currency": "USD",
                            "source": "wayback_machine",
                        }

        except Exception as e:
            logger.error(f"Error extracting price: {e}")

        return None

    async def get_yearly_snapshots(self, url: str, years_back: int = 5) -> List[Dict]:
        """
        Get snapshots from specific dates over multiple years
        Useful for long-term trend analysis

        Args:
            url: URL to get snapshots for
            years_back: Number of years to look back

        Returns:
            List of snapshots, one per year
        """
        snapshots = []
        end_date = datetime.now()

        for year in range(years_back):
            target_date = end_date - timedelta(days=365 * year)

            # Get snapshot closest to this date
            params = {
                "url": url,
                "timestamp": target_date.strftime("%Y%m%d"),
                "output": "json",
            }

            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.get(
                        self.wayback_api,
                        params=params,
                        headers={"User-Agent": self.user_agent},
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if data.get("archived_snapshots") and data["archived_snapshots"].get(
                            "closest"
                        ):
                            closest = data["archived_snapshots"]["closest"]
                            snapshots.append(
                                {
                                    "url": closest["url"],
                                    "timestamp": closest["timestamp"],
                                    "available": closest["available"],
                                    "target_year": target_date.year,
                                }
                            )

            except Exception as e:
                logger.error(f"Error getting snapshot for {target_date.year}: {e}")

        return snapshots


# Example usage
async def check_shopgoodwill_history():
    """Check ShopGoodwill historical data availability"""
    fetcher = HistoricalDataFetcher("https://shopgoodwill.com")
    results = await fetcher.check_availability()

    print(f"\nWayback Machine Analysis")
    print(f"{'=' * 60}")
    print(f"Available: {results['available']}")
    print(f"Snapshot Count: {results['snapshot_count']}")
    print(f"First Snapshot: {results['first_snapshot']}")
    print(f"Last Snapshot: {results['last_snapshot']}")

    if results["date_range"]:
        print(f"Date Range: {results['date_range']['from']} to {results['date_range']['to']}")

    print(f"{'=' * 60}\n")

    return results


if __name__ == "__main__":
    asyncio.run(check_shopgoodwill_history())
