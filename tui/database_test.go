package main

import (
	"os"
	"testing"
	"time"
)

func TestDatabaseCreation(t *testing.T) {
	// Create a temporary database
	tmpDB := "/tmp/test_arbfinder.db"
	defer os.Remove(tmpDB)

	// Override the database path for testing
	os.Setenv("HOME", "/tmp")
	
	db := NewDatabase()
	if db == nil {
		t.Fatal("Failed to create database")
	}
	defer db.Close()

	// Test GetStats
	stats, err := db.GetStats()
	if err != nil {
		t.Fatalf("Failed to get stats: %v", err)
	}

	if stats["total_searches"] != 0 {
		t.Errorf("Expected 0 searches, got %d", stats["total_searches"])
	}
}

func TestSearchHistory(t *testing.T) {
	os.Setenv("HOME", "/tmp")
	db := NewDatabase()
	defer db.Close()
	defer os.Remove("/tmp/.arbfinder_tui.db")

	// Save a search
	err := db.SaveSearchHistory("test query", 5)
	if err != nil {
		t.Fatalf("Failed to save search history: %v", err)
	}

	// Retrieve search history
	history, err := db.GetSearchHistory(10)
	if err != nil {
		t.Fatalf("Failed to get search history: %v", err)
	}

	if len(history) != 1 {
		t.Errorf("Expected 1 history entry, got %d", len(history))
	}

	if history[0].Query != "test query" {
		t.Errorf("Expected query 'test query', got '%s'", history[0].Query)
	}

	if history[0].Results != 5 {
		t.Errorf("Expected 5 results, got %d", history[0].Results)
	}
}

func TestConfigManagement(t *testing.T) {
	os.Setenv("HOME", "/tmp")
	db := NewDatabase()
	defer db.Close()
	defer os.Remove("/tmp/.arbfinder_tui.db")

	// Save a config
	config := map[string]interface{}{
		"api_url":      "http://localhost:8080",
		"threshold":    25.0,
		"providers":    []string{"shopgoodwill", "govdeals"},
	}

	err := db.SaveConfig("test_config", config)
	if err != nil {
		t.Fatalf("Failed to save config: %v", err)
	}

	// Load the config
	loadedConfig, err := db.LoadConfig("test_config")
	if err != nil {
		t.Fatalf("Failed to load config: %v", err)
	}

	if loadedConfig["api_url"] != "http://localhost:8080" {
		t.Errorf("Expected api_url 'http://localhost:8080', got '%v'", loadedConfig["api_url"])
	}

	// Get all configs
	configs, err := db.GetAllConfigs()
	if err != nil {
		t.Fatalf("Failed to get all configs: %v", err)
	}

	if len(configs) != 1 {
		t.Errorf("Expected 1 config, got %d", len(configs))
	}

	if configs[0].Name != "test_config" {
		t.Errorf("Expected config name 'test_config', got '%s'", configs[0].Name)
	}
}

func TestPriceHistory(t *testing.T) {
	os.Setenv("HOME", "/tmp")
	db := NewDatabase()
	defer db.Close()
	defer os.Remove("/tmp/.arbfinder_tui.db")

	// Save price history
	metadata := map[string]interface{}{
		"condition": "used",
		"seller":    "test_seller",
	}

	err := db.SavePriceHistory("RTX 3060", 299.99, "shopgoodwill", metadata)
	if err != nil {
		t.Fatalf("Failed to save price history: %v", err)
	}

	// Retrieve price history
	history, err := db.GetPriceHistory("RTX", 10)
	if err != nil {
		t.Fatalf("Failed to get price history: %v", err)
	}

	if len(history) != 1 {
		t.Errorf("Expected 1 history entry, got %d", len(history))
	}

	if history[0].ItemTitle != "RTX 3060" {
		t.Errorf("Expected item title 'RTX 3060', got '%s'", history[0].ItemTitle)
	}

	if history[0].Price != 299.99 {
		t.Errorf("Expected price 299.99, got %f", history[0].Price)
	}
}

func TestCachedListings(t *testing.T) {
	os.Setenv("HOME", "/tmp")
	db := NewDatabase()
	defer db.Close()
	defer os.Remove("/tmp/.arbfinder_tui.db")

	// Cache a listing
	listing := Listing{
		Source:    "shopgoodwill",
		URL:       "https://example.com/listing/123",
		Title:     "RTX 3060 Graphics Card",
		Price:     299.99,
		Condition: "used",
		Timestamp: time.Now(),
		Metadata:  `{"seller": "test"}`,
	}

	err := db.CacheListing(listing)
	if err != nil {
		t.Fatalf("Failed to cache listing: %v", err)
	}

	// Retrieve cached listings
	listings, err := db.GetCachedListings("RTX", 10)
	if err != nil {
		t.Fatalf("Failed to get cached listings: %v", err)
	}

	if len(listings) != 1 {
		t.Errorf("Expected 1 listing, got %d", len(listings))
	}

	if listings[0].Title != "RTX 3060 Graphics Card" {
		t.Errorf("Expected title 'RTX 3060 Graphics Card', got '%s'", listings[0].Title)
	}

	if listings[0].Price != 299.99 {
		t.Errorf("Expected price 299.99, got %f", listings[0].Price)
	}
}
