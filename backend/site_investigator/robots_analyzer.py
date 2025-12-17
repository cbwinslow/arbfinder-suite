"""
Robots.txt and llms.txt analyzer
Checks crawling permissions and AI-specific rules
"""

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import httpx

logger = logging.getLogger(__name__)


class RobotsAnalyzer:
    """Analyze robots.txt and llms.txt for a website"""

    def __init__(self, site_url: str):
        """Initialize robots analyzer"""
        self.site_url = site_url.rstrip("/")
        self.base_domain = urlparse(self.site_url).netloc
        self.robots_url = urljoin(self.site_url, "/robots.txt")
        self.llms_url = urljoin(self.site_url, "/llms.txt")
        self.user_agent = "ArbFinder-Bot/1.0"

    async def analyze(self) -> Dict[str, Any]:
        """
        Analyze robots.txt and llms.txt files
        
        Returns:
            Dict containing analysis results
        """
        logger.info(f"Analyzing robots.txt for {self.site_url}")
        
        results = {
            "allowed": True,
            "crawl_delay": None,
            "disallowed_paths": [],
            "allowed_paths": [],
            "sitemaps": [],
            "rules": {},
            "llms_txt_found": False,
            "llms_rules": {},
        }
        
        # Fetch robots.txt
        robots_content = await self._fetch_file(self.robots_url)
        if robots_content:
            results.update(self._parse_robots_txt(robots_content))
        
        # Fetch llms.txt
        llms_content = await self._fetch_file(self.llms_url)
        if llms_content:
            results["llms_txt_found"] = True
            results["llms_rules"] = self._parse_llms_txt(llms_content)
        
        return results

    async def _fetch_file(self, url: str) -> Optional[str]:
        """Fetch a text file from URL"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": self.user_agent},
                    follow_redirects=True,
                )
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 404:
                    logger.info(f"File not found: {url}")
                else:
                    logger.warning(
                        f"Unexpected status {response.status_code} for {url}"
                    )
                
        except httpx.HTTPError as e:
            logger.error(f"Error fetching {url}: {e}")
        
        return None

    def _parse_robots_txt(self, content: str) -> Dict[str, Any]:
        """Parse robots.txt content"""
        results = {
            "allowed": True,
            "crawl_delay": None,
            "disallowed_paths": [],
            "allowed_paths": [],
            "sitemaps": [],
            "rules": {},
        }
        
        current_user_agent = None
        user_agent_rules = {}
        
        for line in content.split("\n"):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            
            # Parse directives
            if ":" in line:
                directive, value = line.split(":", 1)
                directive = directive.strip().lower()
                value = value.strip()
                
                if directive == "user-agent":
                    current_user_agent = value
                    if current_user_agent not in user_agent_rules:
                        user_agent_rules[current_user_agent] = {
                            "disallow": [],
                            "allow": [],
                            "crawl_delay": None,
                        }
                
                elif directive == "disallow" and current_user_agent:
                    if value:
                        user_agent_rules[current_user_agent]["disallow"].append(value)
                
                elif directive == "allow" and current_user_agent:
                    if value:
                        user_agent_rules[current_user_agent]["allow"].append(value)
                
                elif directive == "crawl-delay" and current_user_agent:
                    try:
                        user_agent_rules[current_user_agent]["crawl_delay"] = float(
                            value
                        )
                    except ValueError:
                        logger.warning(f"Invalid crawl-delay value: {value}")
                
                elif directive == "sitemap":
                    results["sitemaps"].append(value)
        
        # Apply rules for our bot or * (all bots)
        applicable_rules = None
        
        # Check for specific bot rules
        for ua in ["arbfinder", "arbfinder-bot", self.user_agent.lower()]:
            if ua in user_agent_rules:
                applicable_rules = user_agent_rules[ua]
                break
        
        # Fall back to wildcard rules
        if not applicable_rules and "*" in user_agent_rules:
            applicable_rules = user_agent_rules["*"]
        
        if applicable_rules:
            results["disallowed_paths"] = applicable_rules["disallow"]
            results["allowed_paths"] = applicable_rules["allow"]
            results["crawl_delay"] = applicable_rules["crawl_delay"]
            
            # Check if root is disallowed
            if "/" in applicable_rules["disallow"]:
                results["allowed"] = False
        
        results["rules"] = user_agent_rules
        
        return results

    def _parse_llms_txt(self, content: str) -> Dict[str, Any]:
        """
        Parse llms.txt content
        
        This is an emerging standard for AI/LLM-specific rules
        Format is still evolving, but typically follows similar structure to robots.txt
        """
        rules = {
            "ai_allowed": True,
            "training_allowed": False,
            "api_preferred": False,
            "instructions": [],
            "restrictions": [],
        }
        
        for line in content.split("\n"):
            line = line.strip()
            
            if not line or line.startswith("#"):
                continue
            
            # Parse key-value pairs
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key in ["ai-allowed", "training-allowed", "api-preferred"]:
                    rules[key.replace("-", "_")] = value.lower() in [
                        "yes",
                        "true",
                        "1",
                    ]
                elif key == "instruction":
                    rules["instructions"].append(value)
                elif key == "restriction":
                    rules["restrictions"].append(value)
        
        return rules

    def is_path_allowed(self, path: str, rules: Dict[str, Any]) -> bool:
        """
        Check if a specific path is allowed to be crawled
        
        Args:
            path: URL path to check
            rules: Parsed rules from analyze()
        
        Returns:
            True if path is allowed, False otherwise
        """
        # Check explicit allows first
        for allowed_path in rules.get("allowed_paths", []):
            if path.startswith(allowed_path):
                return True
        
        # Check disallows
        for disallowed_path in rules.get("disallowed_paths", []):
            if path.startswith(disallowed_path):
                return False
        
        # Default to allowed if not explicitly disallowed
        return rules.get("allowed", True)

    def get_recommended_delay(self, rules: Dict[str, Any]) -> float:
        """
        Get recommended crawl delay in seconds
        
        Args:
            rules: Parsed rules from analyze()
        
        Returns:
            Crawl delay in seconds (minimum 1.0)
        """
        crawl_delay = rules.get("crawl_delay")
        
        if crawl_delay:
            return max(float(crawl_delay), 1.0)
        
        # Default to 2 seconds if not specified
        return 2.0


# Example usage
async def analyze_shopgoodwill_robots():
    """Analyze ShopGoodwill robots.txt"""
    analyzer = RobotsAnalyzer("https://shopgoodwill.com")
    results = await analyzer.analyze()
    
    print(f"\nRobots.txt Analysis for shopgoodwill.com")
    print(f"{'=' * 60}")
    print(f"Crawling Allowed: {results['allowed']}")
    print(f"Crawl Delay: {results['crawl_delay']} seconds")
    print(f"\nDisallowed Paths ({len(results['disallowed_paths'])}):")
    for path in results["disallowed_paths"][:10]:
        print(f"  - {path}")
    print(f"\nSitemaps ({len(results['sitemaps'])}):")
    for sitemap in results["sitemaps"]:
        print(f"  - {sitemap}")
    
    if results["llms_txt_found"]:
        print(f"\nLLMs.txt Found:")
        print(f"  AI Allowed: {results['llms_rules'].get('ai_allowed')}")
        print(f"  Training Allowed: {results['llms_rules'].get('training_allowed')}")
    else:
        print(f"\nNo llms.txt found")
    
    print(f"{'=' * 60}\n")
    
    return results


if __name__ == "__main__":
    import asyncio
    
    asyncio.run(analyze_shopgoodwill_robots())
