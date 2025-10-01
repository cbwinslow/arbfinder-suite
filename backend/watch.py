#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Watch mode for continuous monitoring of arbitrage opportunities."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger("ArbFinder")


class WatchMode:
    """Continuous monitoring mode for arbitrage opportunities."""
    
    def __init__(
        self,
        interval: int = 3600,  # 1 hour default
        notify_threshold: float = 30.0,
        max_iterations: Optional[int] = None
    ):
        self.interval = interval
        self.notify_threshold = notify_threshold
        self.max_iterations = max_iterations
        self.iteration = 0
        self.best_deals: List[Dict[str, Any]] = []
        
    async def run(self, search_func, *args, **kwargs):
        """
        Run search function continuously at specified intervals.
        
        Args:
            search_func: Async function to call for searching
            *args, **kwargs: Arguments to pass to search_func
        """
        logger.info(f"Starting watch mode (interval: {self.interval}s)")
        
        while True:
            self.iteration += 1
            
            if self.max_iterations and self.iteration > self.max_iterations:
                logger.info(f"Reached max iterations ({self.max_iterations}), stopping")
                break
            
            try:
                logger.info(f"--- Watch iteration {self.iteration} at {datetime.now().isoformat()} ---")
                
                # Run the search
                results = await search_func(*args, **kwargs)
                
                # Process results
                new_deals = self._find_new_deals(results)
                
                if new_deals:
                    logger.info(f"Found {len(new_deals)} new deals!")
                    for deal in new_deals:
                        self._log_deal(deal)
                else:
                    logger.info("No new deals found in this iteration")
                
                # Wait for next iteration
                if self.max_iterations is None or self.iteration < self.max_iterations:
                    logger.info(f"Sleeping for {self.interval}s until next check...")
                    await asyncio.sleep(self.interval)
                    
            except KeyboardInterrupt:
                logger.info("Watch mode interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in watch iteration {self.iteration}: {e}")
                logger.info(f"Retrying in {self.interval}s...")
                await asyncio.sleep(self.interval)
        
        logger.info(f"Watch mode completed after {self.iteration} iterations")
        return self.best_deals
    
    def _find_new_deals(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find deals that exceed the notification threshold and are new."""
        new_deals = []
        existing_urls = {d['url'] for d in self.best_deals}
        
        for result in results:
            discount = result.get('discount_vs_avg_pct', 0)
            if discount >= self.notify_threshold and result['url'] not in existing_urls:
                new_deals.append(result)
                self.best_deals.append(result)
        
        return new_deals
    
    def _log_deal(self, deal: Dict[str, Any]):
        """Log details of a deal."""
        logger.info(
            f"🎯 DEAL: {deal['title'][:50]}... | "
            f"${deal['price']} | "
            f"Discount: {deal.get('discount_vs_avg_pct', 0):.1f}% | "
            f"Source: {deal['source']}"
        )
