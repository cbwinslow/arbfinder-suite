package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

type Database struct {
	db *sql.DB
}

type SearchHistory struct {
	ID        int
	Query     string
	Timestamp time.Time
	Results   int
}

type SavedConfig struct {
	ID        int
	Name      string
	Config    string
	CreatedAt time.Time
}

type PriceHistory struct {
	ID        int
	ItemTitle string
	Price     float64
	Source    string
	Timestamp time.Time
	Metadata  string
}

type Listing struct {
	ID        int
	Source    string
	URL       string
	Title     string
	Price     float64
	Condition string
	Timestamp time.Time
	Metadata  string
}

// NewDatabase creates and initializes the database
func NewDatabase() *Database {
	homeDir, err := os.UserHomeDir()
	if err != nil {
		panic(err)
	}

	dbPath := filepath.Join(homeDir, ".arbfinder_tui.db")
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		panic(err)
	}

	// Create tables
	if err := createTables(db); err != nil {
		panic(err)
	}

	return &Database{db: db}
}

func createTables(db *sql.DB) error {
	queries := []string{
		`CREATE TABLE IF NOT EXISTS search_history (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			query TEXT NOT NULL,
			timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
			results INTEGER DEFAULT 0
		)`,
		`CREATE TABLE IF NOT EXISTS saved_configs (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT UNIQUE NOT NULL,
			config TEXT NOT NULL,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,
		`CREATE TABLE IF NOT EXISTS price_history (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			item_title TEXT NOT NULL,
			price REAL NOT NULL,
			source TEXT NOT NULL,
			timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
			metadata TEXT
		)`,
		`CREATE TABLE IF NOT EXISTS cached_listings (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			source TEXT NOT NULL,
			url TEXT UNIQUE NOT NULL,
			title TEXT NOT NULL,
			price REAL NOT NULL,
			condition TEXT,
			timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
			metadata TEXT
		)`,
		`CREATE INDEX IF NOT EXISTS idx_search_history_timestamp ON search_history(timestamp)`,
		`CREATE INDEX IF NOT EXISTS idx_price_history_item ON price_history(item_title, timestamp)`,
		`CREATE INDEX IF NOT EXISTS idx_cached_listings_title ON cached_listings(title)`,
	}

	for _, query := range queries {
		if _, err := db.Exec(query); err != nil {
			return fmt.Errorf("failed to create table: %w", err)
		}
	}

	return nil
}

// SaveSearchHistory saves a search query to history
func (d *Database) SaveSearchHistory(query string, results int) error {
	_, err := d.db.Exec(
		"INSERT INTO search_history (query, results) VALUES (?, ?)",
		query, results,
	)
	return err
}

// GetSearchHistory retrieves recent search history
func (d *Database) GetSearchHistory(limit int) ([]SearchHistory, error) {
	rows, err := d.db.Query(
		"SELECT id, query, timestamp, results FROM search_history ORDER BY timestamp DESC LIMIT ?",
		limit,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var history []SearchHistory
	for rows.Next() {
		var h SearchHistory
		if err := rows.Scan(&h.ID, &h.Query, &h.Timestamp, &h.Results); err != nil {
			return nil, err
		}
		history = append(history, h)
	}

	return history, nil
}

// SaveConfig saves a configuration with a name
func (d *Database) SaveConfig(name string, config map[string]interface{}) error {
	configJSON, err := json.Marshal(config)
	if err != nil {
		return err
	}

	_, err = d.db.Exec(
		"INSERT OR REPLACE INTO saved_configs (name, config) VALUES (?, ?)",
		name, string(configJSON),
	)
	return err
}

// LoadConfig loads a configuration by name
func (d *Database) LoadConfig(name string) (map[string]interface{}, error) {
	var configStr string
	err := d.db.QueryRow(
		"SELECT config FROM saved_configs WHERE name = ?",
		name,
	).Scan(&configStr)
	if err != nil {
		return nil, err
	}

	var config map[string]interface{}
	if err := json.Unmarshal([]byte(configStr), &config); err != nil {
		return nil, err
	}

	return config, nil
}

// GetAllConfigs retrieves all saved configurations
func (d *Database) GetAllConfigs() ([]SavedConfig, error) {
	rows, err := d.db.Query(
		"SELECT id, name, config, created_at FROM saved_configs ORDER BY created_at DESC",
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var configs []SavedConfig
	for rows.Next() {
		var c SavedConfig
		if err := rows.Scan(&c.ID, &c.Name, &c.Config, &c.CreatedAt); err != nil {
			return nil, err
		}
		configs = append(configs, c)
	}

	return configs, nil
}

// SavePriceHistory saves price information
func (d *Database) SavePriceHistory(title string, price float64, source string, metadata map[string]interface{}) error {
	metadataJSON, err := json.Marshal(metadata)
	if err != nil {
		return err
	}

	_, err = d.db.Exec(
		"INSERT INTO price_history (item_title, price, source, metadata) VALUES (?, ?, ?, ?)",
		title, price, source, string(metadataJSON),
	)
	return err
}

// GetPriceHistory retrieves price history for an item
func (d *Database) GetPriceHistory(title string, limit int) ([]PriceHistory, error) {
	rows, err := d.db.Query(
		"SELECT id, item_title, price, source, timestamp, metadata FROM price_history WHERE item_title LIKE ? ORDER BY timestamp DESC LIMIT ?",
		"%"+title+"%", limit,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var history []PriceHistory
	for rows.Next() {
		var h PriceHistory
		if err := rows.Scan(&h.ID, &h.ItemTitle, &h.Price, &h.Source, &h.Timestamp, &h.Metadata); err != nil {
			return nil, err
		}
		history = append(history, h)
	}

	return history, nil
}

// CacheListing saves a listing to the cache
func (d *Database) CacheListing(listing Listing) error {
	_, err := d.db.Exec(
		"INSERT OR REPLACE INTO cached_listings (source, url, title, price, condition, metadata) VALUES (?, ?, ?, ?, ?, ?)",
		listing.Source, listing.URL, listing.Title, listing.Price, listing.Condition, listing.Metadata,
	)
	return err
}

// GetCachedListings retrieves cached listings
func (d *Database) GetCachedListings(query string, limit int) ([]Listing, error) {
	rows, err := d.db.Query(
		"SELECT id, source, url, title, price, condition, timestamp, metadata FROM cached_listings WHERE title LIKE ? ORDER BY timestamp DESC LIMIT ?",
		"%"+query+"%", limit,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var listings []Listing
	for rows.Next() {
		var l Listing
		if err := rows.Scan(&l.ID, &l.Source, &l.URL, &l.Title, &l.Price, &l.Condition, &l.Timestamp, &l.Metadata); err != nil {
			return nil, err
		}
		listings = append(listings, l)
	}

	return listings, nil
}

// GetStats returns database statistics
func (d *Database) GetStats() (map[string]int, error) {
	stats := make(map[string]int)

	// Count search history
	var totalSearches int
	err := d.db.QueryRow("SELECT COUNT(*) FROM search_history").Scan(&totalSearches)
	if err != nil {
		return nil, err
	}
	stats["total_searches"] = totalSearches

	// Count saved configs
	var savedConfigs int
	err = d.db.QueryRow("SELECT COUNT(*) FROM saved_configs").Scan(&savedConfigs)
	if err != nil {
		return nil, err
	}
	stats["saved_configs"] = savedConfigs

	// Count price history entries
	var priceHistoryEntries int
	err = d.db.QueryRow("SELECT COUNT(*) FROM price_history").Scan(&priceHistoryEntries)
	if err != nil {
		return nil, err
	}
	stats["price_history_entries"] = priceHistoryEntries

	// Count cached listings
	var cachedListings int
	err = d.db.QueryRow("SELECT COUNT(*) FROM cached_listings").Scan(&cachedListings)
	if err != nil {
		return nil, err
	}
	stats["cached_listings"] = cachedListings

	return stats, nil
}

// Close closes the database connection
func (d *Database) Close() error {
	return d.db.Close()
}
