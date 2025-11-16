package main

// SearchMsg is sent when a search is initiated
type SearchMsg struct {
	Query     string
	Provider  string
	Threshold float64
}

// SearchResultMsg is sent when search results are available
type SearchResultMsg struct {
	Results []APIListing
	Error   error
}

// StatsLoadedMsg is sent when statistics are loaded
type StatsLoadedMsg struct {
	DBStats  map[string]int
	APIStats *APIStatistics
	Error    error
}

// ConfigLoadedMsg is sent when configurations are loaded
type ConfigLoadedMsg struct {
	Configs []SavedConfig
	Error   error
}

// ConfigSavedMsg is sent when a configuration is saved
type ConfigSavedMsg struct {
	Name  string
	Error error
}

// StatusMsg is a general status message
type StatusMsg struct {
	Message string
	IsError bool
}
