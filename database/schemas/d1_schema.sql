-- ArbFinder Suite D1 Database Schema
-- Version: 2.1
-- Last Updated: 2024-12-17

-- Listings table
CREATE TABLE IF NOT EXISTS listings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  url TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  price REAL NOT NULL,
  currency TEXT DEFAULT 'USD',
  condition TEXT,
  ts REAL NOT NULL,
  meta_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_listings_source ON listings(source);
CREATE INDEX IF NOT EXISTS idx_listings_price ON listings(price);
CREATE INDEX IF NOT EXISTS idx_listings_ts ON listings(ts);
CREATE INDEX IF NOT EXISTS idx_listings_title ON listings(title);

-- Comparable prices table
CREATE TABLE IF NOT EXISTS comps (
  key_title TEXT PRIMARY KEY,
  avg_price REAL,
  median_price REAL,
  count INTEGER,
  ts REAL
);

-- Snipes table
CREATE TABLE IF NOT EXISTS snipes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  listing_url TEXT NOT NULL,
  listing_title TEXT,
  max_bid REAL NOT NULL,
  auction_end_time REAL NOT NULL,
  lead_time_seconds INTEGER DEFAULT 5,
  status TEXT DEFAULT 'scheduled',
  created_at REAL NOT NULL,
  executed_at REAL,
  result TEXT,
  metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_snipes_status ON snipes(status);
CREATE INDEX IF NOT EXISTS idx_snipes_auction_end ON snipes(auction_end_time);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  search_query TEXT NOT NULL,
  min_price REAL,
  max_price REAL,
  notification_method TEXT NOT NULL,
  notification_target TEXT NOT NULL,
  status TEXT DEFAULT 'active',
  created_at REAL NOT NULL,
  last_triggered_at REAL,
  trigger_count INTEGER DEFAULT 0,
  metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);

-- Alert matches table
CREATE TABLE IF NOT EXISTS alert_matches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  alert_id INTEGER NOT NULL,
  listing_id INTEGER,
  listing_url TEXT,
  listing_title TEXT,
  listing_price REAL,
  matched_at REAL NOT NULL,
  notification_sent BOOLEAN DEFAULT 0,
  FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_alert_matches_alert_id ON alert_matches(alert_id);

-- Crew runs table
CREATE TABLE IF NOT EXISTS crew_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  crew_type TEXT NOT NULL,
  targets TEXT,
  query TEXT,
  status TEXT DEFAULT 'queued',
  started_at REAL NOT NULL,
  completed_at REAL,
  duration_seconds REAL,
  items_processed INTEGER DEFAULT 0,
  items_created INTEGER DEFAULT 0,
  error_message TEXT,
  result_data TEXT
);

CREATE INDEX IF NOT EXISTS idx_crew_runs_status ON crew_runs(status);
CREATE INDEX IF NOT EXISTS idx_crew_runs_type ON crew_runs(crew_type);
