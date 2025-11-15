package main

import (
	"fmt"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

type StatsPane struct {
	dbStats     map[string]int
	apiStats    *APIStatistics
	priceHist   []PriceHistory
	loading     bool
	lastError   string
	apiClient   *APIClient
	db          *Database
}

func NewStatsPane() *StatsPane {
	return &StatsPane{
		dbStats:   make(map[string]int),
		apiClient: NewAPIClient(""),
	}
}

func (p *StatsPane) Update(msg tea.Msg) (StatsPane, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "r":
			// Refresh statistics
			p.loading = true
			// TODO: Implement refresh
			return *p, nil
		}
	}

	return *p, nil
}

func (p *StatsPane) View(width, height int) string {
	var b strings.Builder

	titleStyle := lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("#7D56F4")).
		MarginBottom(1)

	sectionStyle := lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("#FAFAFA")).
		MarginTop(1).
		MarginBottom(1)

	labelStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#00D7FF"))

	valueStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#FAFAFA")).
		Bold(true)

	infoStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#626262")).
		Italic(true)

	// Title
	b.WriteString(titleStyle.Render("📈 Statistics & Analytics"))
	b.WriteString("\n\n")

	if p.loading {
		statusStyle := lipgloss.NewStyle().
			Foreground(lipgloss.Color("#00FF00")).
			Bold(true)
		b.WriteString(statusStyle.Render("🔄 Loading statistics..."))
		b.WriteString("\n")
	} else {
		// Database statistics
		b.WriteString(sectionStyle.Render("💾 Local Database"))
		b.WriteString("\n")
		
		if len(p.dbStats) > 0 {
			b.WriteString(fmt.Sprintf("%s %s\n",
				labelStyle.Render("Total Searches:"),
				valueStyle.Render(fmt.Sprintf("%d", p.dbStats["total_searches"])),
			))
			b.WriteString(fmt.Sprintf("%s %s\n",
				labelStyle.Render("Saved Configs:"),
				valueStyle.Render(fmt.Sprintf("%d", p.dbStats["saved_configs"])),
			))
			b.WriteString(fmt.Sprintf("%s %s\n",
				labelStyle.Render("Price History:"),
				valueStyle.Render(fmt.Sprintf("%d", p.dbStats["price_history_entries"])),
			))
			b.WriteString(fmt.Sprintf("%s %s\n",
				labelStyle.Render("Cached Listings:"),
				valueStyle.Render(fmt.Sprintf("%d", p.dbStats["cached_listings"])),
			))
		} else {
			b.WriteString(infoStyle.Render("No local data yet"))
			b.WriteString("\n")
		}

		// API statistics
		b.WriteString("\n")
		b.WriteString(sectionStyle.Render("🌐 API Statistics"))
		b.WriteString("\n")
		
		if p.apiStats != nil {
			b.WriteString(fmt.Sprintf("%s %s\n",
				labelStyle.Render("Total Listings:"),
				valueStyle.Render(fmt.Sprintf("%d", p.apiStats.TotalListings)),
			))
			b.WriteString(fmt.Sprintf("%s %s\n",
				labelStyle.Render("Average Price:"),
				valueStyle.Render(fmt.Sprintf("$%.2f", p.apiStats.AvgPrice)),
			))
			b.WriteString(fmt.Sprintf("%s %s\n",
				labelStyle.Render("Price Range:"),
				valueStyle.Render(fmt.Sprintf("$%.2f - $%.2f", p.apiStats.MinPrice, p.apiStats.MaxPrice)),
			))
		} else {
			b.WriteString(infoStyle.Render("API not connected"))
			b.WriteString("\n")
		}

		// Price analysis
		b.WriteString("\n")
		b.WriteString(sectionStyle.Render("💰 Price Analysis"))
		b.WriteString("\n")
		
		if len(p.priceHist) > 0 {
			// Calculate average price from history
			var total float64
			for _, ph := range p.priceHist {
				total += ph.Price
			}
			avg := total / float64(len(p.priceHist))
			
			b.WriteString(fmt.Sprintf("%s %s\n",
				labelStyle.Render("Tracked Items:"),
				valueStyle.Render(fmt.Sprintf("%d", len(p.priceHist))),
			))
			b.WriteString(fmt.Sprintf("%s %s\n",
				labelStyle.Render("Avg Tracked Price:"),
				valueStyle.Render(fmt.Sprintf("$%.2f", avg)),
			))
		} else {
			b.WriteString(infoStyle.Render("No price history yet"))
			b.WriteString("\n")
		}
	}

	// Instructions
	b.WriteString("\n\n")
	b.WriteString(infoStyle.Render("r: Refresh • Tab: Switch pane"))

	// Error
	if p.lastError != "" {
		errorStyle := lipgloss.NewStyle().
			Foreground(lipgloss.Color("#FF0000")).
			Bold(true)
		b.WriteString("\n\n")
		b.WriteString(errorStyle.Render(fmt.Sprintf("✗ Error: %s", p.lastError)))
	}

	return b.String()
}

func (p *StatsPane) LoadStats(db *Database) {
	if db != nil {
		stats, err := db.GetStats()
		if err == nil {
			p.dbStats = stats
		} else {
			p.lastError = err.Error()
		}

		// Load recent price history
		priceHist, err := db.GetPriceHistory("", 100)
		if err == nil {
			p.priceHist = priceHist
		}
	}

	// Load API stats
	apiStats, err := p.apiClient.GetStatistics()
	if err == nil {
		p.apiStats = apiStats
	}

	p.loading = false
}
