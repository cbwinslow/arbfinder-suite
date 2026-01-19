#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import sqlite3
import sys
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from rapidfuzz import fuzz

try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

APP_NAME = "ArbFinder"
DEFAULT_UA = f"{APP_NAME}/0.2 (+https://cloudcurio.cc)"
DEFAULT_DB_PATH = str(Path.home() / ".arb_finder.sqlite3")
DEFAULT_LOG_PATH = str(Path("/tmp") / "ArbFinder.log")
HTTP_TIMEOUT = 20.0
MAX_CONCURRENCY = 6
RETRY_BASE = 0.6
RETRY_MAX = 3
RATE_LIMIT_SECONDS = 1.0

_price_re = re.compile(r"([\$£€])\s*([0-9]+(?:[\.,][0-9]{2})?)")


@dataclass
class Listing:
    source: str
    url: str
    title: str
    price: float
    currency: str = "USD"
    condition: str = "unknown"
    timestamp: float = field(default_factory=lambda: time.time())
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Comp:
    key_title: str
    avg_price: float
    median_price: float
    count: int


logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.INFO)

if RICH_AVAILABLE:
    # Use Rich handler for better formatting
    ch = RichHandler(rich_tracebacks=True, markup=True)
    ch.setFormatter(logging.Formatter("%(message)s"))
else:
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

logger.addHandler(ch)

try:
    fh = logging.FileHandler(DEFAULT_LOG_PATH)
    fh.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s"))
    logger.addHandler(fh)
except Exception as e:
    logger.warning("File logger init failed: %s", e)


@contextmanager
def sqlite_conn(db_path: str):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def db_init(db_path: str) -> None:
    with sqlite_conn(db_path) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS listings (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              source TEXT, url TEXT UNIQUE, title TEXT, price REAL,
              currency TEXT, condition TEXT, ts REAL, meta_json TEXT
            );
            """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS comps (
              key_title TEXT PRIMARY KEY, avg_price REAL, median_price REAL,
              count INTEGER, ts REAL
            );
            """)
        conn.commit()


def db_upsert_listing(db_path: str, listing: Listing) -> None:
    with sqlite_conn(db_path) as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO listings (source,url,title,price,currency,condition,ts,meta_json)
            VALUES (?,?,?,?,?,?,?,?)
            ON CONFLICT(url) DO UPDATE SET
              title=excluded.title, price=excluded.price, currency=excluded.currency,
              condition=excluded.condition, ts=excluded.ts, meta_json=excluded.meta_json;
            """,
            (
                listing.source,
                listing.url,
                listing.title,
                listing.price,
                listing.currency,
                listing.condition,
                listing.timestamp,
                json.dumps(listing.meta) if listing.meta else "{}",
            ),
        )
        conn.commit()


def db_upsert_comp(db_path: str, comp: Comp) -> None:
    with sqlite_conn(db_path) as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO comps (key_title,avg_price,median_price,count,ts)
            VALUES (?,?,?,?,?)
            ON CONFLICT(key_title) DO UPDATE SET
              avg_price=excluded.avg_price, median_price=excluded.median_price,
              count=excluded.count, ts=excluded.ts;
            """,
            (comp.key_title, comp.avg_price, comp.median_price, comp.count, time.time()),
        )
        conn.commit()


class PoliteClient:
    def __init__(self, ua: str = DEFAULT_UA, timeout: float = HTTP_TIMEOUT):
        self._client = httpx.AsyncClient(
            headers={"User-Agent": ua}, timeout=timeout, follow_redirects=True
        )
        self._last: Dict[str, float] = {}
        import asyncio

        self._sem = asyncio.Semaphore(MAX_CONCURRENCY)

    async def get(self, url: str) -> httpx.Response:
        import asyncio

        host = httpx.URL(url).host or ""
        async with self._sem:
            now = time.time()
            wait = max(0.0, RATE_LIMIT_SECONDS - (now - self._last.get(host, 0)))
            if wait:
                await asyncio.sleep(wait)
            resp = None
            for attempt in range(1, RETRY_MAX + 1):
                try:
                    resp = await self._client.get(url)
                    self._last[host] = time.time()
                    if resp.status_code in (429, 503):
                        raise httpx.HTTPError(f"Rate limited: {resp.status_code}")
                    return resp
                except Exception as e:
                    backoff = RETRY_BASE * (2 ** (attempt - 1)) + 0.2
                    logger.warning(
                        "GET %s failed (%s). retry %d in %.1fs", url, e, attempt, backoff
                    )
                    await asyncio.sleep(backoff)
            return resp

    async def close(self):
        await self._client.aclose()


class Provider:
    name = "base"

    def __init__(self, client: PoliteClient):
        self.client = client

    async def search(self, query: str, limit: int = 40):
        raise NotImplementedError


class EbaySoldComps(Provider):
    name = "ebay_sold"

    @staticmethod
    def _url(query: str) -> str:
        q = httpx.QueryParams({"_nkw": query, "LH_Sold": 1, "LH_Complete": 1})
        return f"https://www.ebay.com/sch/i.html?{q}"

    async def search(self, query: str, limit: int = 120):
        html = (await self.client.get(self._url(query))).text
        items: List[Listing] = []
        for block in re.split(r"<li class=\\\"s-item[\\s\\S]*?>", html)[1:]:
            m_title = re.search(r"s-item__title\\\">(.*?)<", block)
            m_price = re.search(r"s-item__price\\\">(.*?)<", block)
            if not (m_title and m_price):
                continue
            title_raw = re.sub(r"<.*?>", "", m_title.group(1)).strip()
            m_price_text = re.sub(r"<.*?>", " ", m_price.group(1))
            price_parsed = _price_re.search(m_price_text.replace(",", ""))
            if not price_parsed:
                continue
            sym, amt = price_parsed.group(1), price_parsed.group(2)
            price = float(amt)
            currency = {"$": "USD", "£": "GBP", "€": "EUR"}.get(sym, "USD")
            m_url = re.search(r"href=\\\"(https?://www.ebay.com/itm/[^\"]+)\\\"", block)
            url_item = m_url.group(1) if m_url else self._url(query)
            items.append(
                Listing(self.name, url_item, title_raw, price, currency, "sold", meta={"q": query})
            )
            if len(items) >= limit:
                break
        return items


class ShopGoodwillLive(Provider):
    name = "shopgoodwill"

    @staticmethod
    def _url(query: str, page: int = 1) -> str:
        return f"https://shopgoodwill.com/search?st={httpx.utils.quote(query)}&pp=40&p={page}"

    async def search(self, query: str, limit: int = 60):
        items: List[Listing] = []
        page = 1
        while len(items) < limit and page <= 3:
            html = (await self.client.get(self._url(query, page))).text
            for card in html.split("product-card"):
                m_title = re.search(r"product-title[\\s\\S]*?>(.*?)<", card)
                m_url = re.search(r"href=\\\"(/item/[^\"]+)\\\"", card)
                m_price = re.search(r"Current Bid[\\s\\S]*?\\$([0-9]+(?:\\.[0-9]{2})?)", card)
                if not (m_title and m_url and m_price):
                    continue
                title = re.sub(r"<.*?>", "", m_title.group(1)).strip()
                url_item = httpx.URL("https://shopgoodwill.com").join(m_url.group(1)).human_repr()
                try:
                    price = float(m_price.group(1))
                except ValueError:
                    continue
                items.append(
                    Listing(
                        self.name,
                        url_item,
                        title,
                        price,
                        "USD",
                        "live",
                        meta={"q": query, "page": page},
                    )
                )
                if len(items) >= limit:
                    break
            page += 1
        return items


class GovDealsLive(Provider):
    name = "govdeals"

    @staticmethod
    def _url(query: str, page: int = 1) -> str:
        return f"https://www.govdeals.com/index.cfm?fa=Main.AdvSearchResultsNew&kWord={httpx.utils.quote(query)}&whichForm=vehicle&SearchPg=Main&kCatID=0&rowCount=50&startRow={50*(page-1)+1}"

    async def search(self, query: str, limit: int = 60):
        items: List[Listing] = []
        page = 1
        while len(items) < limit and page <= 2:
            html = (await self.client.get(self._url(query, page))).text
            for block in re.split(r"<div class=\\\"auction-card[\\s\\S]*?>", html)[1:]:
                m_title = re.search(r"item-title[\\s\\S]*?>(.*?)<", block)
                m_url = re.search(
                    r"href=\\\"(/index\\\\.cfm\\?fa=Main\\\\.Item&itemid[^\"]+)\\\"", block
                )
                m_price = re.search(r"Current Bid:\\s*\\$([0-9]+(?:\\.[0-9]{2})?)", block)
                if not (m_title and m_url and m_price):
                    continue
                title = re.sub(r"<.*?>", "", m_title.group(1)).strip()
                url_item = httpx.URL("https://www.govdeals.com").join(m_url.group(1)).human_repr()
                try:
                    price = float(m_price.group(1))
                except ValueError:
                    continue
                items.append(
                    Listing(
                        self.name,
                        url_item,
                        title,
                        price,
                        "USD",
                        "live",
                        meta={"q": query, "page": page},
                    )
                )
                if len(items) >= limit:
                    break
            page += 1
        return items


class GovernmentSurplusLive(Provider):
    name = "governmentsurplus"

    @staticmethod
    def _url(query: str, page: int = 1) -> str:
        return f"https://www.governmentauctions.org/search_results.asp?Search={httpx.utils.quote(query)}&page={page}"

    async def search(self, query: str, limit: int = 40):
        items: List[Listing] = []
        page = 1
        while len(items) < limit and page <= 2:
            html = (await self.client.get(self._url(query, page))).text
            for block in re.split(r"<div class=\\\"result-card[\\s\\S]*?>", html)[1:]:
                m_title = re.search(r"<h3[\\s\\S]*?>(.*?)<", block)
                m_url = re.search(r"href=\\\"(https?://[^\"]+)\\\"", block)
                m_price = re.search(r"\\$([0-9]+(?:\\.[0-9]{2})?)", block)
                if not (m_title and m_url and m_price):
                    continue
                title = re.sub(r"<.*?>", "", m_title.group(1)).strip()
                url_item = m_url.group(1)
                price = float(m_price.group(1))
                items.append(
                    Listing(
                        self.name,
                        url_item,
                        title,
                        price,
                        "USD",
                        "live",
                        meta={"q": query, "page": page},
                    )
                )
                if len(items) >= limit:
                    break
            page += 1
        return items


class ManualImport(Provider):
    name = "manual"

    def __init__(self, client: PoliteClient, path: Optional[str] = None):
        super().__init__(client)
        self.path = path

    async def search(self, query: str, limit: int = 1000):
        if not self.path:
            return []
        items: List[Listing] = []
        p = Path(self.path)
        if p.suffix.lower() == ".csv":
            import csv

            with open(p, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    try:
                        items.append(
                            Listing(
                                self.name,
                                row.get("url", ""),
                                row.get("title", ""),
                                float(row.get("price", 0)),
                                row.get("currency", "USD"),
                                row.get("condition", "live"),
                            )
                        )
                    except Exception:
                        pass
        elif p.suffix.lower() == ".json":
            data = json.loads(p.read_text(encoding="utf-8"))
            for obj in data:
                try:
                    items.append(
                        Listing(
                            self.name,
                            obj.get("url", ""),
                            obj.get("title", ""),
                            float(obj.get("price", 0)),
                            obj.get("currency", "USD"),
                            obj.get("condition", "live"),
                        )
                    )
                except Exception:
                    pass
        return items[:limit]


try:
    from crawl4ai import WebCrawler  # type: ignore

    CRAWL4AI_AVAILABLE = True
except Exception:
    CRAWL4AI_AVAILABLE = False


class Crawl4AIProvider(Provider):
    name = "crawl4ai"

    async def search(self, query: str, limit: int = 40):
        if not CRAWL4AI_AVAILABLE:
            logger.warning("crawl4ai not installed; skipping")
            return []
        return []


def compute_comps(listings: List[Listing], sim_threshold: int = 86) -> Dict[str, Comp]:
    if not listings:
        return {}
    bins: Dict[str, List[float]] = defaultdict(list)
    exemplars: List[str] = []
    for lst in listings:
        nt = re.sub(r"\s+", " ", lst.title).strip().lower()
        chosen = None
        for key in exemplars:
            if fuzz.token_set_ratio(nt, key) >= sim_threshold:
                chosen = key
                break
        if not chosen:
            chosen = nt
            exemplars.append(nt)
        bins[chosen].append(lst.price)
    comps: Dict[str, Comp] = {}
    for key, prices in bins.items():
        prices.sort()
        n = len(prices)
        avg = sum(prices) / n
        median = prices[n // 2] if n % 2 == 1 else (prices[n // 2 - 1] + prices[n // 2]) / 2
        comps[key] = Comp(key, avg, median, n)
    return comps


def match_comps_to_live(
    live: List[Listing], comps: Dict[str, Comp], sim_threshold: int = 86
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    comp_keys = list(comps.keys())
    for lst in live:
        nt = re.sub(r"\s+", " ", lst.title).strip().lower()
        best_key, best_score = None, -1
        for key in comp_keys:
            s = fuzz.token_set_ratio(nt, key)
            if s > best_score:
                best_key, best_score = key, s
        comp = comps.get(best_key) if best_key and best_score >= sim_threshold else None
        row = {
            "source": lst.source,
            "title": lst.title,
            "url": lst.url,
            "price": lst.price,
            "currency": lst.currency,
            "best_match_key": best_key,
            "similarity": best_score,
            "avg_price": getattr(comp, "avg_price", None),
            "median_price": getattr(comp, "median_price", None),
            "comp_count": getattr(comp, "count", 0),
        }
        if comp and comp.avg_price:
            row["discount_vs_avg_pct"] = round(100.0 * (1 - lst.price / comp.avg_price), 2)
            row["discount_vs_median_pct"] = round(100.0 * (1 - lst.price / comp.median_price), 2)
        else:
            row["discount_vs_avg_pct"] = None
            row["discount_vs_median_pct"] = None
        rows.append(row)
    return rows


def export_csv(rows: List[Dict[str, Any]], path: str) -> None:
    if not rows:
        return
    import csv

    keys = sorted({k for r in rows for k in r.keys()})
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def export_json(rows: List[Dict[str, Any]], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


async def run_arbfinder(args: argparse.Namespace) -> List[Dict[str, Any]]:
    # Import TUI module if available
    tui_module = None
    if RICH_AVAILABLE and args.interactive:
        try:
            from . import tui as tui_module
        except ImportError:
            try:
                import tui as tui_module
            except ImportError:
                logger.warning("TUI module not available, continuing without interactive mode")

    # Handle interactive mode
    if tui_module and args.interactive:
        tui_module.show_welcome()
        user_input = await tui_module.interactive_mode()
        args.query = user_input["query"]
        args.providers = user_input["providers"]
        args.threshold_pct = user_input["threshold_pct"]

    db_init(args.db)
    client = PoliteClient()

    providers: Dict[str, Provider] = {
        "ebay_sold": EbaySoldComps(client),
        "shopgoodwill": ShopGoodwillLive(client),
        "govdeals": GovDealsLive(client),
        "governmentsurplus": GovernmentSurplusLive(client),
    }

    if args.manual_path:
        providers["manual"] = ManualImport(client, args.manual_path)
    if args.use_crawl4ai:
        providers["crawl4ai"] = Crawl4AIProvider(client)

    # Progress tracking
    if RICH_AVAILABLE and not args.quiet:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=Console(),
        )
        progress.start()
        task1 = progress.add_task("[cyan]Fetching eBay sold comps...", total=args.comp_limit)
    else:
        progress = None
        task1 = None

    logger.info("Searching eBay sold listings for: %s", args.query)
    sold = await providers["ebay_sold"].search(args.query, limit=args.comp_limit)

    if progress:
        progress.update(task1, completed=len(sold))

    logger.info("Found %d sold listings", len(sold))
    for lst in sold:
        db_upsert_listing(args.db, lst)

    comps = compute_comps(sold, sim_threshold=args.sim_threshold)
    logger.info("Computed %d comparable groups", len(comps))
    for comp in comps.values():
        db_upsert_comp(args.db, comp)

    wanted = [
        p.strip()
        for p in (args.providers or "shopgoodwill,govdeals,governmentsurplus").split(",")
        if p.strip() in providers
    ]
    live: List[Listing] = []

    if progress:
        task2 = progress.add_task(f"[green]Searching {len(wanted)} providers...", total=len(wanted))

    for i, name in enumerate(wanted):
        try:
            logger.info("Searching provider: %s", name)
            res = await providers[name].search(args.query, limit=args.live_limit)
            logger.info("Provider %s returned %d results", name, len(res))
            for lst in res:
                db_upsert_listing(args.db, lst)
            live.extend(res)
            if progress:
                progress.update(task2, completed=i + 1)
        except Exception as e:
            logger.warning("Provider %s failed: %s", name, e)

    if progress:
        progress.stop()

    rows = match_comps_to_live(live, comps, sim_threshold=args.sim_threshold)

    if args.threshold_pct is not None:
        rows = [r for r in rows if (r.get("discount_vs_avg_pct") or -999) >= args.threshold_pct]

    rows.sort(key=lambda r: (r.get("discount_vs_avg_pct") or -999), reverse=True)

    logger.info("Found %d opportunities after filtering", len(rows))

    # Display results with TUI if available
    if tui_module and not args.quiet:
        table = tui_module.create_listings_table(rows[:20])  # Show top 20
        Console().print(table)

        stats = {
            "Total Listings Found": len(live),
            "Opportunities": len(rows),
            "Providers Searched": len(wanted),
            "Comparable Groups": len(comps),
        }
        tui_module.show_summary(stats)

    if args.csv:
        export_csv(rows, args.csv)
        logger.info("Exported to CSV: %s", args.csv)

    if args.json:
        export_json(rows, args.json)
        logger.info("Exported to JSON: %s", args.json)

    await client.close()
    return rows


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog=APP_NAME, description="Find arbitrage deals vs eBay sold comps"
    )
    p.add_argument(
        "query", nargs="?", default="", help="Search query, e.g., 'RTX 3060' or 'Boss DS-1'"
    )
    p.add_argument(
        "--db", default=DEFAULT_DB_PATH, help="Database path (default: ~/.arb_finder.sqlite3)"
    )
    p.add_argument(
        "--live-limit", type=int, default=80, help="Max live listings per provider (default: 80)"
    )
    p.add_argument(
        "--comp-limit", type=int, default=150, help="Max sold comps to fetch (default: 150)"
    )
    p.add_argument(
        "--sim-threshold", type=int, default=86, help="Similarity threshold 0-100 (default: 86)"
    )
    p.add_argument(
        "--threshold-pct", type=float, default=20.0, help="Min discount percentage (default: 20.0)"
    )
    p.add_argument(
        "--providers", help="Comma list: shopgoodwill,govdeals,governmentsurplus,manual,crawl4ai"
    )
    p.add_argument(
        "--manual-path", help="CSV/JSON for ManualImport provider (e.g., FB Marketplace export)"
    )
    p.add_argument(
        "--use-crawl4ai", action="store_true", help="Enable crawl4ai provider if installed"
    )
    p.add_argument("--csv", help="Export CSV path")
    p.add_argument("--json", help="Export JSON path")
    p.add_argument("-i", "--interactive", action="store_true", help="Run in interactive TUI mode")
    p.add_argument("-q", "--quiet", action="store_true", help="Suppress progress output")
    p.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    p.add_argument(
        "-w", "--watch", action="store_true", help="Enable watch mode (continuous monitoring)"
    )
    p.add_argument(
        "--watch-interval",
        type=int,
        default=3600,
        help="Watch mode interval in seconds (default: 3600)",
    )
    p.add_argument("--config", help="Path to config file (default: ~/.arbfinder_config.json)")
    p.add_argument(
        "--save-config", action="store_true", help="Save current arguments to config file"
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    # Load config if requested
    if args.config or args.save_config:
        try:
            from . import config as config_module
        except ImportError:
            try:
                import config as config_module
            except ImportError:
                logger.warning("Config module not available")
                config_module = None

        if config_module:
            if args.save_config:
                # Save current args to config
                config_dict = {
                    "query": args.query,
                    "db_path": args.db,
                    "live_limit": args.live_limit,
                    "comp_limit": args.comp_limit,
                    "sim_threshold": args.sim_threshold,
                    "threshold_pct": args.threshold_pct,
                    "providers": args.providers or "",
                    "watch_interval": args.watch_interval,
                }
                if config_module.save_config(config_dict, args.config):
                    logger.info("Configuration saved successfully")
                return 0

            # Load config and merge with args
            loaded_config = config_module.load_config(args.config)
            if not args.query and loaded_config.get("query"):
                args.query = loaded_config["query"]
            if args.db == DEFAULT_DB_PATH and loaded_config.get("db_path"):
                args.db = loaded_config["db_path"]

    # Handle verbose mode
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Handle interactive mode without query
    if args.interactive or not args.query:
        args.interactive = True

    # Handle watch mode
    if args.watch:
        try:
            from . import watch as watch_module
        except ImportError:
            try:
                import watch as watch_module
            except ImportError:
                logger.error("Watch module not available")
                return 1

        logger.info(f"Starting watch mode with {args.watch_interval}s interval")

        async def watch_runner():
            watch = watch_module.WatchMode(
                interval=args.watch_interval, notify_threshold=args.threshold_pct
            )

            async def search_wrapper():
                results = await run_arbfinder(args)
                return results

            await watch.run(search_wrapper)
            return 0

        try:
            return asyncio.run(watch_runner())
        except KeyboardInterrupt:
            logger.info("Watch mode interrupted by user")
            return 2

    try:
        asyncio.run(run_arbfinder(args))
        return 0
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 2
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
