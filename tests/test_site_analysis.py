"""
Tests for site analysis functionality
"""

import asyncio
import json
from pathlib import Path

import pytest

from backend.site_investigator import (
    RobotsAnalyzer,
    TermsAnalyzer,
    APIDiscoverer,
    HistoricalDataFetcher,
    SiteInvestigator,
)


class TestRobotsAnalyzer:
    """Test robots.txt analysis"""

    @pytest.mark.asyncio
    async def test_robots_analyzer_basic(self):
        """Test basic robots.txt analysis"""
        analyzer = RobotsAnalyzer("https://example.com")
        
        # Check initialization
        assert analyzer.site_url == "https://example.com"
        assert analyzer.robots_url == "https://example.com/robots.txt"

    @pytest.mark.asyncio
    async def test_parse_robots_txt(self):
        """Test robots.txt parsing"""
        analyzer = RobotsAnalyzer("https://example.com")
        
        content = """
User-agent: *
Disallow: /admin/
Disallow: /private/
Allow: /public/
Crawl-delay: 2

Sitemap: https://example.com/sitemap.xml
        """
        
        result = analyzer._parse_robots_txt(content)
        
        assert result["disallowed_paths"] == ["/admin/", "/private/"]
        assert result["allowed_paths"] == ["/public/"]
        assert result["crawl_delay"] == 2.0
        assert len(result["sitemaps"]) == 1


class TestAPIDiscoverer:
    """Test API discovery"""

    @pytest.mark.asyncio
    async def test_api_discoverer_init(self):
        """Test API discoverer initialization"""
        discoverer = APIDiscoverer("https://api.example.com")
        
        assert discoverer.site_url == "https://api.example.com"
        assert len(discoverer.discovered_endpoints) == 0

    def test_parse_openapi_spec(self):
        """Test OpenAPI specification parsing"""
        discoverer = APIDiscoverer("https://api.example.com")
        
        spec = json.dumps({
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Get users",
                        "description": "Retrieve list of users",
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "type": "integer",
                                "required": False,
                            }
                        ],
                    }
                }
            }
        })
        
        endpoints = discoverer._parse_openapi_spec(spec)
        
        assert len(endpoints) == 1
        assert endpoints[0]["method"] == "GET"
        assert endpoints[0]["path"] == "/users"
        assert len(endpoints[0]["parameters"]) == 1

    def test_detect_base_path(self):
        """Test API base path detection"""
        discoverer = APIDiscoverer("https://api.example.com")
        
        endpoints = [
            {"path": "/api/v1/users"},
            {"path": "/api/v1/posts"},
            {"path": "/api/v1/comments"},
        ]
        
        base_path = discoverer._detect_base_path(endpoints)
        assert base_path in ["/api", "/api/v1"]


class TestHistoricalDataFetcher:
    """Test historical data fetching"""

    @pytest.mark.asyncio
    async def test_historical_fetcher_init(self):
        """Test historical data fetcher initialization"""
        fetcher = HistoricalDataFetcher("https://example.com")
        
        assert fetcher.site_url == "https://example.com"
        assert fetcher.wayback_api == "https://archive.org/wayback/available"

    def test_parse_timestamp(self):
        """Test Wayback timestamp parsing"""
        fetcher = HistoricalDataFetcher("https://example.com")
        
        timestamp = "20240101120000"
        result = fetcher._parse_timestamp(timestamp)
        
        assert "2024-01-01" in result

    def test_build_wayback_url(self):
        """Test Wayback URL construction"""
        fetcher = HistoricalDataFetcher("https://example.com")
        
        url = fetcher._build_wayback_url(
            "20240101120000",
            "https://example.com/page"
        )
        
        assert "web.archive.org" in url
        assert "20240101120000" in url
        assert "example.com/page" in url


class TestSiteInvestigator:
    """Test site investigator orchestrator"""

    @pytest.mark.asyncio
    async def test_investigator_init(self):
        """Test investigator initialization"""
        investigator = SiteInvestigator(
            site_url="https://example.com",
            site_name="example",
            output_dir="/tmp/test_output",
        )
        
        assert investigator.site_url == "https://example.com"
        assert investigator.site_name == "example"
        assert Path("/tmp/test_output").exists()

    def test_determine_approach(self):
        """Test approach determination logic"""
        from backend.site_investigator.investigator import SiteInvestigationReport
        
        investigator = SiteInvestigator(
            site_url="https://example.com",
            site_name="example",
        )
        
        # Test API preferred
        report = SiteInvestigationReport(
            site_name="example",
            site_url="https://example.com",
            investigation_date="2024-01-01",
            robots_allowed=True,
            api_allowed=True,
            api_endpoints=[{"path": "/api/test"}],
        )
        
        approach = investigator._determine_approach(report)
        assert approach == "API_PREFERRED"
        
        # Test web scraping
        report.api_allowed = False
        report.api_endpoints = []
        report.scraping_allowed = True
        
        approach = investigator._determine_approach(report)
        assert approach == "WEB_SCRAPING"


def test_imports():
    """Test that all modules can be imported"""
    from backend.site_investigator import (
        SiteInvestigator,
        RobotsAnalyzer,
        TermsAnalyzer,
        APIDiscoverer,
        HistoricalDataFetcher,
    )
    
    from backend.agents import (
        APIAnalysisAgent,
        MCPServerAgent,
        SchemaGeneratorAgent,
        SiteAnalysisCrew,
    )
    
    # All imports successful
    assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
