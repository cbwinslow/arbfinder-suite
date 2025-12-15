"""
Cloudflare Integration Scripts for ArbFinder Suite.

This package provides scripts for setting up and managing Cloudflare infrastructure
including Workers, Pages, R2, D1, KV, and security features.
"""

__version__ = "1.0.0"
__author__ = "ArbFinder Development Team"

from .config import CloudflareConfig

__all__ = ["CloudflareConfig"]
