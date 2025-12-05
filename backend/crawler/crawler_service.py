"""
Crawler service using Crawl4AI for web scraping
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import toml

try:
    from crawl4ai import AsyncWebCrawler

    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("Warning: crawl4ai not installed. Install with: pip install crawl4ai")

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class CrawlerConfig(BaseModel):
    """Crawler configuration model"""

    user_agent: str
    timeout: int
    max_retries: int
    delay_between_requests: int
    concurrent_requests: int


class TargetSite(BaseModel):
    """Target site configuration"""

    name: str
    url: str
    enabled: bool
    schedule: str
    category_urls: List[str]
    selectors: Dict[str, str]


class CrawlResult(BaseModel):
    """Result from a crawl operation"""

    target_name: str
    url: str
    status: str
    items_found: int
    price_data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    error_msg: Optional[str] = None
    duration_ms: int


class CrawlerService:
    """Service for managing web crawling operations"""

    def __init__(self, config_path: str = "config/crawler.toml"):
        """Initialize crawler service with configuration"""
        self.config_path = Path(config_path)
        self.config = None
        self.targets = []
        self.load_config()

    def load_config(self) -> None:
        """Load crawler configuration from TOML file"""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return

        try:
            config_data = toml.load(self.config_path)
            self.config = CrawlerConfig(**config_data.get("crawler", {}))

            # Load target sites
            for target_data in config_data.get("targets", []):
                if target_data.get("enabled", True):
                    target = TargetSite(**target_data)
                    self.targets.append(target)

            logger.info(f"Loaded {len(self.targets)} target sites from config")
        except Exception as e:
            logger.error(f"Error loading config: {e}")

    async def crawl_target(self, target: TargetSite) -> CrawlResult:
        """Crawl a single target site"""
        start_time = time.time()
        items_found = 0
        price_data = []
        error_msg = None
        status = "success"

        if not CRAWL4AI_AVAILABLE:
            error_msg = "crawl4ai library not available"
            status = "error"
            return CrawlResult(
                target_name=target.name,
                url=target.url,
                status=status,
                items_found=0,
                price_data=[],
                metadata={},
                error_msg=error_msg,
                duration_ms=int((time.time() - start_time) * 1000),
            )

        try:
            async with AsyncWebCrawler(
                verbose=False,
                headless=True,
            ) as crawler:
                for category_url in target.category_urls:
                    try:
                        # Crawl the page
                        result = await crawler.arun(
                            url=category_url,
                            bypass_cache=True,
                            user_agent=self.config.user_agent if self.config else None,
                        )

                        if result.success:
                            # Extract structured data
                            extracted = self._extract_items(result.html, target.selectors)
                            items_found += len(extracted)
                            price_data.extend(extracted)

                        await asyncio.sleep(
                            self.config.delay_between_requests if self.config else 2
                        )

                    except Exception as e:
                        logger.error(f"Error crawling {category_url}: {e}")
                        error_msg = str(e)
                        status = "partial"

        except Exception as e:
            logger.error(f"Error in crawler for {target.name}: {e}")
            error_msg = str(e)
            status = "error"

        duration_ms = int((time.time() - start_time) * 1000)

        return CrawlResult(
            target_name=target.name,
            url=target.url,
            status=status,
            items_found=items_found,
            price_data=price_data,
            metadata={
                "category_urls_crawled": len(target.category_urls),
                "timestamp": datetime.utcnow().isoformat(),
            },
            error_msg=error_msg,
            duration_ms=duration_ms,
        )

    def _extract_items(self, html: str, selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract items from HTML using CSS selectors"""
        # This is a simplified implementation
        # In production, use BeautifulSoup or lxml for robust parsing
        items = []

        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")

            # Find all item containers
            containers = soup.select(selectors.get("item_container", ".item"))

            for container in containers:
                item = {}

                # Extract title
                title_elem = container.select_one(selectors.get("title", ".title"))
                if title_elem:
                    item["title"] = title_elem.get_text(strip=True)

                # Extract price
                price_elem = container.select_one(selectors.get("price", ".price"))
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    item["price"] = self._parse_price(price_text)

                # Extract image URL
                image_elem = container.select_one(selectors.get("image", "img"))
                if image_elem:
                    item["image_url"] = image_elem.get("src") or image_elem.get("data-src")

                # Extract link
                link_elem = container.select_one(selectors.get("link", "a"))
                if link_elem:
                    item["url"] = link_elem.get("href")

                # Extract condition
                condition_elem = container.select_one(selectors.get("condition", ".condition"))
                if condition_elem:
                    item["condition"] = condition_elem.get_text(strip=True)

                if item.get("title") and item.get("price"):
                    items.append(item)

        except ImportError:
            logger.warning("BeautifulSoup not available for HTML parsing")
        except Exception as e:
            logger.error(f"Error extracting items: {e}")

        return items

    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price from text"""
        try:
            # Remove currency symbols and commas
            price_clean = price_text.replace("$", "").replace(",", "").strip()
            return float(price_clean)
        except (ValueError, AttributeError):
            return None

    async def crawl_all(self) -> List[CrawlResult]:
        """Crawl all enabled target sites"""
        logger.info(f"Starting crawl of {len(self.targets)} targets")
        results = []

        for target in self.targets:
            result = await self.crawl_target(target)
            results.append(result)
            logger.info(
                f"Crawled {target.name}: {result.items_found} items, "
                f"status={result.status}, duration={result.duration_ms}ms"
            )

        return results

    async def crawl_by_name(self, target_name: str) -> Optional[CrawlResult]:
        """Crawl a specific target by name"""
        for target in self.targets:
            if target.name == target_name:
                return await self.crawl_target(target)
        return None


# Example usage
async def main():
    """Example crawler usage"""
    crawler = CrawlerService()
    results = await crawler.crawl_all()

    for result in results:
        print(f"\n{result.target_name}:")
        print(f"  Status: {result.status}")
        print(f"  Items: {result.items_found}")
        print(f"  Duration: {result.duration_ms}ms")
        if result.error_msg:
            print(f"  Error: {result.error_msg}")


if __name__ == "__main__":
    asyncio.run(main())
