"""
API Endpoint Discovery Tool
Discovers and analyzes API endpoints through various methods
"""

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class APIDiscoverer:
    """Discover and analyze API endpoints"""

    def __init__(self, site_url: str):
        """Initialize API discoverer"""
        self.site_url = site_url.rstrip("/")
        self.base_domain = urlparse(self.site_url).netloc
        self.user_agent = "ArbFinder-Bot/1.0"
        self.discovered_endpoints: Set[str] = set()

    async def discover(self) -> Dict[str, Any]:
        """
        Discover API endpoints using multiple techniques

        Returns:
            Dict containing discovered endpoints and metadata
        """
        logger.info(f"Discovering API endpoints for {self.site_url}")

        results = {
            "endpoints": [],
            "documentation_url": None,
            "requires_auth": False,
            "api_version": None,
            "base_path": None,
        }

        # Run discovery methods in parallel
        (
            doc_endpoints,
            network_endpoints,
            sitemap_endpoints,
        ) = await asyncio.gather(
            self._discover_from_documentation(),
            self._discover_from_network_analysis(),
            self._discover_from_sitemap(),
            return_exceptions=True,
        )

        # Merge results
        all_endpoints = []

        if not isinstance(doc_endpoints, Exception):
            all_endpoints.extend(doc_endpoints.get("endpoints", []))
            if doc_endpoints.get("documentation_url"):
                results["documentation_url"] = doc_endpoints["documentation_url"]

        if not isinstance(network_endpoints, Exception):
            all_endpoints.extend(network_endpoints)

        if not isinstance(sitemap_endpoints, Exception):
            all_endpoints.extend(sitemap_endpoints)

        # Deduplicate and enrich endpoint data
        results["endpoints"] = self._deduplicate_endpoints(all_endpoints)

        # Detect API patterns
        if results["endpoints"]:
            results["base_path"] = self._detect_base_path(results["endpoints"])
            results["api_version"] = self._detect_api_version(results["endpoints"])
            results["requires_auth"] = self._detect_auth_requirement(results["endpoints"])

        logger.info(f"Discovered {len(results['endpoints'])} unique endpoints")

        return results

    async def _discover_from_documentation(self) -> Dict[str, Any]:
        """Try to find and parse API documentation"""

        results = {
            "endpoints": [],
            "documentation_url": None,
        }

        # Common API documentation URL patterns
        doc_patterns = [
            "/api/docs",
            "/api-docs",
            "/api/documentation",
            "/developers",
            "/developer",
            "/docs/api",
            "/swagger",
            "/openapi.json",
            "/api/v1/docs",
            "/api/v2/docs",
        ]

        for pattern in doc_patterns:
            url = urljoin(self.site_url, pattern)
            content = await self._fetch_page(url)

            if content:
                results["documentation_url"] = url

                # Try to parse as JSON (OpenAPI/Swagger)
                if pattern.endswith(".json") or "swagger" in url:
                    endpoints = self._parse_openapi_spec(content)
                    if endpoints:
                        results["endpoints"].extend(endpoints)
                        break

                # Parse HTML documentation
                endpoints = self._parse_html_documentation(content, url)
                if endpoints:
                    results["endpoints"].extend(endpoints)
                    break

        return results

    async def _discover_from_network_analysis(self) -> List[Dict[str, Any]]:
        """
        Analyze network requests by visiting main pages
        Note: This is basic - a browser automation approach would be more thorough
        """
        endpoints = []

        # Visit homepage and look for AJAX/API calls in JavaScript
        homepage = await self._fetch_page(self.site_url)
        if homepage:
            # Look for API endpoints in JavaScript code
            js_endpoints = self._extract_endpoints_from_js(homepage)
            endpoints.extend(js_endpoints)

        return endpoints

    async def _discover_from_sitemap(self) -> List[Dict[str, Any]]:
        """Check sitemap for API-like paths"""
        endpoints = []

        sitemap_url = urljoin(self.site_url, "/sitemap.xml")
        content = await self._fetch_page(sitemap_url)

        if content:
            # Parse sitemap XML
            try:
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(content, "xml")
                urls = soup.find_all("loc")

                for url_elem in urls:
                    url = url_elem.get_text()

                    # Look for API-like patterns
                    if any(
                        pattern in url.lower() for pattern in ["/api/", "/v1/", "/v2/", "/rest/"]
                    ):
                        endpoints.append(
                            {
                                "path": urlparse(url).path,
                                "method": "GET",
                                "source": "sitemap",
                            }
                        )

            except Exception as e:
                logger.error(f"Error parsing sitemap: {e}")

        return endpoints

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
            logger.debug(f"Error fetching {url}: {e}")

        return None

    def _parse_openapi_spec(self, content: str) -> List[Dict[str, Any]]:
        """Parse OpenAPI/Swagger specification"""
        endpoints = []

        try:
            spec = json.loads(content)

            # OpenAPI 3.x or Swagger 2.x
            paths = spec.get("paths", {})

            for path, methods in paths.items():
                for method, details in methods.items():
                    if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                        endpoint = {
                            "path": path,
                            "method": method.upper(),
                            "description": details.get("description", ""),
                            "summary": details.get("summary", ""),
                            "parameters": [],
                            "source": "openapi",
                        }

                        # Extract parameters
                        params = details.get("parameters", [])
                        for param in params:
                            endpoint["parameters"].append(
                                {
                                    "name": param.get("name"),
                                    "in": param.get("in"),
                                    "required": param.get("required", False),
                                    "type": param.get("type", "string"),
                                }
                            )

                        endpoints.append(endpoint)

        except json.JSONDecodeError:
            logger.debug("Content is not valid JSON")
        except Exception as e:
            logger.error(f"Error parsing OpenAPI spec: {e}")

        return endpoints

    def _parse_html_documentation(self, html: str, base_url: str) -> List[Dict[str, Any]]:
        """Parse HTML API documentation"""
        endpoints = []

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Look for common API documentation patterns
            # This is heuristic-based and may need adjustment per site

            # Pattern 1: Code blocks with API paths
            code_blocks = soup.find_all(["code", "pre"])
            for block in code_blocks:
                text = block.get_text()

                # Look for HTTP methods and paths
                pattern = r"(GET|POST|PUT|DELETE|PATCH)\s+(\/[^\s]+)"
                matches = re.findall(pattern, text, re.IGNORECASE)

                for method, path in matches:
                    endpoints.append(
                        {
                            "path": path,
                            "method": method.upper(),
                            "source": "html_docs",
                        }
                    )

        except Exception as e:
            logger.error(f"Error parsing HTML documentation: {e}")

        return endpoints

    def _extract_endpoints_from_js(self, html: str) -> List[Dict[str, Any]]:
        """Extract API endpoints from JavaScript code"""
        endpoints = []

        try:
            # Look for common API call patterns
            patterns = [
                r"['\"]/(api|v\d+)/[^'\"]+['\"]",  # "/api/..." or "/v1/..."
                r"fetch\(['\"]([^'\"]+)['\"]",  # fetch("...")
                r"axios\.(?:get|post|put|delete)\(['\"]([^'\"]+)['\"]",  # axios.get("...")
                r"\.ajax\(\{[^}]*url:\s*['\"]([^'\"]+)['\"]",  # jQuery ajax
            ]

            for pattern in patterns:
                matches = re.findall(pattern, html)

                for match in matches:
                    # Extract the path from the match
                    path = match if isinstance(match, str) else match[0]

                    # Filter out non-API paths
                    if any(
                        api_indicator in path.lower()
                        for api_indicator in ["/api/", "/v1/", "/v2/", "/rest/"]
                    ):
                        # Clean up the path
                        path = re.sub(r"\${[^}]+}", "{param}", path)  # Template vars

                        endpoints.append(
                            {
                                "path": path,
                                "method": "GET",  # Default assumption
                                "source": "javascript",
                            }
                        )

        except Exception as e:
            logger.error(f"Error extracting endpoints from JS: {e}")

        return endpoints

    def _deduplicate_endpoints(self, endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate endpoints"""
        seen = set()
        unique = []

        for endpoint in endpoints:
            # Create unique key from method + path
            key = f"{endpoint.get('method', 'GET')}:{endpoint.get('path', '')}"

            if key not in seen:
                seen.add(key)
                unique.append(endpoint)

        return unique

    def _detect_base_path(self, endpoints: List[Dict[str, Any]]) -> Optional[str]:
        """Detect common base path for API endpoints"""
        if not endpoints:
            return None

        paths = [e.get("path", "") for e in endpoints]

        # Common base paths to check
        common_bases = ["/api", "/v1", "/v2", "/api/v1", "/api/v2", "/rest"]

        for base in common_bases:
            if sum(1 for p in paths if p.startswith(base)) > len(paths) * 0.5:
                return base

        return None

    def _detect_api_version(self, endpoints: List[Dict[str, Any]]) -> Optional[str]:
        """Detect API version from endpoints"""
        version_pattern = r"/v(\d+)"

        for endpoint in endpoints:
            path = endpoint.get("path", "")
            match = re.search(version_pattern, path)
            if match:
                return f"v{match.group(1)}"

        return None

    def _detect_auth_requirement(self, endpoints: List[Dict[str, Any]]) -> bool:
        """Detect if endpoints likely require authentication"""

        # Check endpoint descriptions for auth keywords
        auth_keywords = ["auth", "token", "key", "bearer", "api key"]

        for endpoint in endpoints:
            description = (
                endpoint.get("description", "") + " " + endpoint.get("summary", "")
            ).lower()

            if any(keyword in description for keyword in auth_keywords):
                return True

            # Check for auth-related parameters
            params = endpoint.get("parameters", [])
            for param in params:
                param_name = param.get("name", "").lower()
                if any(keyword in param_name for keyword in auth_keywords):
                    return True

        return False


# Example usage
async def discover_shopgoodwill_api():
    """Discover ShopGoodwill API endpoints"""
    discoverer = APIDiscoverer("https://shopgoodwill.com")
    results = await discoverer.discover()

    print(f"\nAPI Discovery Results")
    print(f"{'=' * 60}")
    print(f"Documentation URL: {results['documentation_url']}")
    print(f"Base Path: {results['base_path']}")
    print(f"API Version: {results['api_version']}")
    print(f"Requires Auth: {results['requires_auth']}")
    print(f"\nDiscovered Endpoints ({len(results['endpoints'])}):")

    for endpoint in results["endpoints"][:10]:
        print(
            f"  {endpoint['method']:6s} {endpoint['path']:40s} ({endpoint.get('source', 'unknown')})"
        )

    if len(results["endpoints"]) > 10:
        print(f"  ... and {len(results['endpoints']) - 10} more")

    print(f"{'=' * 60}\n")

    return results


if __name__ == "__main__":
    asyncio.run(discover_shopgoodwill_api())
