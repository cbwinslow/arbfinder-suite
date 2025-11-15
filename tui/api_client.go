package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"
)

type APIClient struct {
	baseURL    string
	httpClient *http.Client
}

type APIListing struct {
	ID        int                    `json:"id"`
	Source    string                 `json:"source"`
	URL       string                 `json:"url"`
	Title     string                 `json:"title"`
	Price     float64                `json:"price"`
	Currency  string                 `json:"currency"`
	Condition string                 `json:"condition"`
	Timestamp float64                `json:"ts"`
	Metadata  map[string]interface{} `json:"meta_json"`
}

type APIStatistics struct {
	TotalListings  int     `json:"total_listings"`
	UniqueSourcers int     `json:"unique_sources"`
	AvgPrice       float64 `json:"avg_price"`
	MinPrice       float64 `json:"min_price"`
	MaxPrice       float64 `json:"max_price"`
}

type APIResponse struct {
	Items []APIListing `json:"items"`
	Total int          `json:"total"`
	Limit int          `json:"limit"`
	Offset int         `json:"offset"`
}

type APIComp struct {
	KeyTitle    string  `json:"key_title"`
	AvgPrice    float64 `json:"avg_price"`
	MedianPrice float64 `json:"median_price"`
	Count       int     `json:"count"`
	Timestamp   float64 `json:"ts"`
}

// NewAPIClient creates a new API client
func NewAPIClient(baseURL string) *APIClient {
	if baseURL == "" {
		baseURL = "http://localhost:8080"
	}

	return &APIClient{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// GetListings retrieves listings from the API
func (c *APIClient) GetListings(limit, offset int, source, orderBy string) ([]APIListing, error) {
	params := url.Values{}
	params.Add("limit", fmt.Sprintf("%d", limit))
	params.Add("offset", fmt.Sprintf("%d", offset))
	if source != "" {
		params.Add("source", source)
	}
	if orderBy != "" {
		params.Add("order_by", orderBy)
	}

	url := fmt.Sprintf("%s/api/listings?%s", c.baseURL, params.Encode())
	resp, err := c.httpClient.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to get listings: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API error: %s - %s", resp.Status, string(body))
	}

	var apiResp APIResponse
	if err := json.NewDecoder(resp.Body).Decode(&apiResp); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return apiResp.Items, nil
}

// SearchListings searches for listings
func (c *APIClient) SearchListings(query string) ([]APIListing, error) {
	params := url.Values{}
	params.Add("q", query)

	url := fmt.Sprintf("%s/api/listings/search?%s", c.baseURL, params.Encode())
	resp, err := c.httpClient.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to search listings: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API error: %s - %s", resp.Status, string(body))
	}

	var apiResp APIResponse
	if err := json.NewDecoder(resp.Body).Decode(&apiResp); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return apiResp.Items, nil
}

// GetStatistics retrieves statistics from the API
func (c *APIClient) GetStatistics() (*APIStatistics, error) {
	url := fmt.Sprintf("%s/api/statistics", c.baseURL)
	resp, err := c.httpClient.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to get statistics: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API error: %s - %s", resp.Status, string(body))
	}

	var stats APIStatistics
	if err := json.NewDecoder(resp.Body).Decode(&stats); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &stats, nil
}

// GetComps retrieves comparable prices
func (c *APIClient) GetComps(query string) ([]APIComp, error) {
	params := url.Values{}
	if query != "" {
		params.Add("q", query)
		url := fmt.Sprintf("%s/api/comps/search?%s", c.baseURL, params.Encode())
		resp, err := c.httpClient.Get(url)
		if err != nil {
			return nil, fmt.Errorf("failed to get comps: %w", err)
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			body, _ := io.ReadAll(resp.Body)
			return nil, fmt.Errorf("API error: %s - %s", resp.Status, string(body))
		}

		var comps []APIComp
		if err := json.NewDecoder(resp.Body).Decode(&comps); err != nil {
			return nil, fmt.Errorf("failed to decode response: %w", err)
		}

		return comps, nil
	}

	url := fmt.Sprintf("%s/api/comps", c.baseURL)
	resp, err := c.httpClient.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to get comps: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API error: %s - %s", resp.Status, string(body))
	}

	var comps []APIComp
	if err := json.NewDecoder(resp.Body).Decode(&comps); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return comps, nil
}

// Ping checks if the API is reachable
func (c *APIClient) Ping() error {
	url := fmt.Sprintf("%s/", c.baseURL)
	resp, err := c.httpClient.Get(url)
	if err != nil {
		return fmt.Errorf("failed to ping API: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("API returned non-200 status: %s", resp.Status)
	}

	return nil
}
