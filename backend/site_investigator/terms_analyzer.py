"""
Terms of Service and Conditions of Use analyzer
Identifies usage policies, API permissions, and restrictions
"""

import logging
import re
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class TermsAnalyzer:
    """Analyze Terms of Service and usage policies"""

    def __init__(self, site_url: str, site_name: str):
        """Initialize terms analyzer"""
        self.site_url = site_url.rstrip("/")
        self.site_name = site_name
        self.user_agent = "ArbFinder-Bot/1.0"

        # Common ToS URL patterns
        self.tos_patterns = [
            "/terms",
            "/terms-of-service",
            "/terms-and-conditions",
            "/tos",
            "/legal/terms",
            "/policies/terms",
            "/conditions-of-use",
            "/user-agreement",
        ]

    async def analyze(self) -> Dict[str, Any]:
        """
        Analyze Terms of Service and usage policies

        Returns:
            Dict containing analysis results
        """
        logger.info(f"Analyzing Terms of Service for {self.site_url}")

        results = {
            "terms_url": None,
            "api_allowed": False,
            "scraping_allowed": False,
            "commercial_use_allowed": True,  # Default assumption
            "rate_limits": {},
            "restrictions": [],
            "key_findings": [],
        }

        # Find ToS page
        terms_url = await self._find_terms_page()
        if not terms_url:
            logger.warning("Could not locate Terms of Service page")
            results["key_findings"].append("Terms of Service page not found")
            return results

        results["terms_url"] = terms_url

        # Fetch and parse ToS content
        terms_content = await self._fetch_page(terms_url)
        if not terms_content:
            logger.warning(f"Could not fetch Terms page: {terms_url}")
            return results

        # Analyze terms content
        analysis = self._analyze_terms_content(terms_content)
        results.update(analysis)

        return results

    async def _find_terms_page(self) -> Optional[str]:
        """Try to find the Terms of Service page"""

        # First, try common URL patterns
        for pattern in self.tos_patterns:
            url = urljoin(self.site_url, pattern)
            if await self._check_url_exists(url):
                logger.info(f"Found ToS page: {url}")
                return url

        # Try to find link on homepage
        homepage_content = await self._fetch_page(self.site_url)
        if homepage_content:
            terms_link = self._find_terms_link_in_html(homepage_content)
            if terms_link:
                full_url = urljoin(self.site_url, terms_link)
                logger.info(f"Found ToS link in homepage: {full_url}")
                return full_url

        return None

    async def _check_url_exists(self, url: str) -> bool:
        """Check if a URL exists (returns 200)"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.head(
                    url,
                    headers={"User-Agent": self.user_agent},
                    follow_redirects=True,
                )
                return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": self.user_agent},
                    follow_redirects=True,
                )

                if response.status_code == 200:
                    return response.text

        except httpx.HTTPError as e:
            logger.error(f"Error fetching {url}: {e}")

        return None

    def _find_terms_link_in_html(self, html: str) -> Optional[str]:
        """Find Terms of Service link in HTML"""
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Look for links with common terms keywords
            terms_keywords = [
                "terms",
                "conditions",
                "legal",
                "policies",
                "agreement",
            ]

            for link in soup.find_all("a", href=True):
                link_text = link.get_text().lower()
                href = link["href"].lower()

                for keyword in terms_keywords:
                    if keyword in link_text or keyword in href:
                        # Filter out unrelated links
                        if not any(x in href for x in ["privacy", "cookie", "shipping", "return"]):
                            return link["href"]

        except Exception as e:
            logger.error(f"Error parsing HTML for terms link: {e}")

        return None

    def _analyze_terms_content(self, content: str) -> Dict[str, Any]:
        """Analyze Terms of Service content for key restrictions"""

        results = {
            "api_allowed": False,
            "scraping_allowed": False,
            "commercial_use_allowed": True,
            "rate_limits": {},
            "restrictions": [],
            "key_findings": [],
        }

        # Convert to lowercase for analysis
        content_lower = content.lower()

        # Check for API mentions
        api_patterns = [
            r"api[\s]+(?:access|usage|key|endpoint)",
            r"application[\s]+programming[\s]+interface",
            r"developer[\s]+(?:access|portal|api)",
        ]

        for pattern in api_patterns:
            if re.search(pattern, content_lower):
                results["api_allowed"] = True
                results["key_findings"].append("API usage mentioned in terms")
                break

        # Check for scraping restrictions
        scraping_patterns = [
            r"(?:prohibit|forbid|not[\s]+(?:allow|permit)).*?(?:scrap|crawl|automat|robot|bot)",
            r"(?:scrap|crawl|automat|robot|bot).*?(?:prohibit|forbid|not[\s]+(?:allow|permit))",
            r"unauthorized[\s]+(?:access|data[\s]+collection|extraction)",
        ]

        scraping_prohibited = False
        for pattern in scraping_patterns:
            if re.search(pattern, content_lower):
                scraping_prohibited = True
                results["restrictions"].append("Automated scraping/crawling prohibited in terms")
                break

        # If not explicitly prohibited, check for permissive language
        if not scraping_prohibited:
            permissive_patterns = [
                r"(?:allow|permit|may).*?(?:access|use).*?(?:data|content)",
                r"publicly[\s]+available",
            ]

            for pattern in permissive_patterns:
                if re.search(pattern, content_lower):
                    results["scraping_allowed"] = True
                    break

        # Check for commercial use restrictions
        commercial_patterns = [
            r"(?:prohibit|forbid|not[\s]+(?:allow|permit)).*?commercial[\s]+use",
            r"non[\s]*-?[\s]*commercial[\s]+use[\s]+only",
            r"personal[\s]+use[\s]+only",
        ]

        for pattern in commercial_patterns:
            if re.search(pattern, content_lower):
                results["commercial_use_allowed"] = False
                results["restrictions"].append("Commercial use restricted")
                break

        # Look for rate limit mentions
        rate_limit_patterns = [
            r"(?:rate[\s]+limit|request[\s]+limit).*?(\d+).*?(per|every|each)[\s]+(\w+)",
            r"(\d+)[\s]+requests?[\s]+per[\s]+(\w+)",
        ]

        for pattern in rate_limit_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                for match in matches:
                    if len(match) >= 2:
                        results["rate_limits"]["requests"] = match[0]
                        results["key_findings"].append(
                            f"Rate limit found: {match[0]} per {match[-1]}"
                        )

        # Check for data retention/usage restrictions
        data_patterns = [
            r"(?:data|information).*?(?:retain|store|keep)",
            r"(?:delete|remove).*?(?:data|information)",
            r"data[\s]+retention",
        ]

        for pattern in data_patterns:
            if re.search(pattern, content_lower):
                results["key_findings"].append("Data retention policies mentioned")
                break

        # Check for attribution requirements
        if re.search(r"attribut|credit|cite|source", content_lower):
            results["restrictions"].append("Attribution may be required")

        return results

    def generate_compliance_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable compliance report"""

        lines = [
            f"Terms of Service Analysis - {self.site_name}",
            "=" * 60,
            "",
        ]

        if results["terms_url"]:
            lines.append(f"Terms URL: {results['terms_url']}")
        else:
            lines.append("Terms URL: Not found")

        lines.extend(
            [
                "",
                "Permissions:",
                f"  API Access: {'Yes' if results['api_allowed'] else 'No'}",
                f"  Web Scraping: {'Yes' if results['scraping_allowed'] else 'No'}",
                f"  Commercial Use: {'Yes' if results['commercial_use_allowed'] else 'No'}",
                "",
            ]
        )

        if results["rate_limits"]:
            lines.append("Rate Limits:")
            for key, value in results["rate_limits"].items():
                lines.append(f"  {key}: {value}")
            lines.append("")

        if results["restrictions"]:
            lines.append("Restrictions:")
            for restriction in results["restrictions"]:
                lines.append(f"  - {restriction}")
            lines.append("")

        if results["key_findings"]:
            lines.append("Key Findings:")
            for finding in results["key_findings"]:
                lines.append(f"  - {finding}")

        lines.append("=" * 60)

        return "\n".join(lines)


# Example usage
async def analyze_shopgoodwill_terms():
    """Analyze ShopGoodwill Terms of Service"""
    analyzer = TermsAnalyzer("https://shopgoodwill.com", "shopgoodwill")
    results = await analyzer.analyze()

    report = analyzer.generate_compliance_report(results)
    print(f"\n{report}\n")

    return results


if __name__ == "__main__":
    import asyncio

    asyncio.run(analyze_shopgoodwill_terms())
