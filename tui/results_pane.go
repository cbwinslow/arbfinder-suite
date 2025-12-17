package main

import (
	"fmt"
	"strings"
	"time"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

type ResultsPane struct {
	results      []APIListing
	selectedIdx  int
	offset       int
	pageSize     int
	loading      bool
	lastError    string
	apiClient    *APIClient
}

func NewResultsPane() *ResultsPane {
	return &ResultsPane{
		results:   []APIListing{},
		pageSize:  10,
		apiClient: NewAPIClient(""),
	}
}

func (p *ResultsPane) Update(msg tea.Msg) (ResultsPane, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "up", "k":
			if p.selectedIdx > 0 {
				p.selectedIdx--
				if p.selectedIdx < p.offset {
					p.offset = p.selectedIdx
				}
			}
			return *p, nil

		case "down", "j":
			if p.selectedIdx < len(p.results)-1 {
				p.selectedIdx++
				if p.selectedIdx >= p.offset+p.pageSize {
					p.offset = p.selectedIdx - p.pageSize + 1
				}
			}
			return *p, nil

		case "r":
			// Refresh results - reload from API
			p.loading = true
			p.lastError = ""
			// Reload listings from API
			go func() {
				listings, err := p.apiClient.GetListings(100, 0)
				if err != nil {
					p.lastError = err.Error()
				} else {
					p.SetResults(listings)
				}
				p.loading = false
			}()
			return *p, nil

		case "enter":
			// View details of selected listing
			if len(p.results) > 0 && p.selectedIdx < len(p.results) {
				selected := p.results[p.selectedIdx]
				// In a real implementation, this could open the URL in browser
				// or show a detailed view. For now, just acknowledge the action.
				p.lastError = fmt.Sprintf("Viewing: %s", selected.Title)
			}
			return *p, nil
		}
	}

	return *p, nil
}

func (p *ResultsPane) View(width, height int) string {
	var b strings.Builder

	titleStyle := lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("#7D56F4")).
		MarginBottom(1)

	headerStyle := lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("#FAFAFA")).
		Background(lipgloss.Color("#3a3a3a")).
		Padding(0, 1)

	itemStyle := lipgloss.NewStyle().
		Padding(0, 1)

	selectedItemStyle := itemStyle.Copy().
		Background(lipgloss.Color("#7D56F4")).
		Bold(true)

	infoStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#626262")).
		Italic(true)

	// Title
	b.WriteString(titleStyle.Render(fmt.Sprintf("📊 Results (%d listings)", len(p.results))))
	b.WriteString("\n\n")

	if p.loading {
		statusStyle := lipgloss.NewStyle().
			Foreground(lipgloss.Color("#00FF00")).
			Bold(true)
		b.WriteString(statusStyle.Render("🔄 Loading..."))
		b.WriteString("\n")
	} else if len(p.results) == 0 {
		emptyStyle := lipgloss.NewStyle().
			Foreground(lipgloss.Color("#888888")).
			Italic(true)
		b.WriteString(emptyStyle.Render("No results yet. Perform a search to see listings."))
		b.WriteString("\n")
	} else {
		// Header
		header := fmt.Sprintf("%-20s %-40s %10s %12s", "Source", "Title", "Price", "Age")
		b.WriteString(headerStyle.Render(header))
		b.WriteString("\n")

		// Display results (paginated)
		end := p.offset + p.pageSize
		if end > len(p.results) {
			end = len(p.results)
		}

		for i := p.offset; i < end; i++ {
			result := p.results[i]
			title := result.Title
			if len(title) > 40 {
				title = title[:37] + "..."
			}

			age := formatAge(result.Timestamp)
			line := fmt.Sprintf("%-20s %-40s $%8.2f %12s",
				result.Source,
				title,
				result.Price,
				age,
			)

			if i == p.selectedIdx {
				b.WriteString(selectedItemStyle.Render("▸ " + line))
			} else {
				b.WriteString(itemStyle.Render("  " + line))
			}
			b.WriteString("\n")
		}

		// Pagination info
		b.WriteString("\n")
		pageInfo := fmt.Sprintf("Showing %d-%d of %d", p.offset+1, end, len(p.results))
		b.WriteString(infoStyle.Render(pageInfo))
	}

	// Instructions
	b.WriteString("\n\n")
	b.WriteString(infoStyle.Render("↑/↓ or j/k: Navigate • Enter: View details • r: Refresh • Tab: Switch pane"))

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

func formatAge(timestamp float64) string {
	if timestamp == 0 {
		return "unknown"
	}

	t := time.Unix(int64(timestamp), 0)
	duration := time.Since(t)

	if duration.Hours() < 1 {
		return fmt.Sprintf("%dm ago", int(duration.Minutes()))
	} else if duration.Hours() < 24 {
		return fmt.Sprintf("%dh ago", int(duration.Hours()))
	} else {
		return fmt.Sprintf("%dd ago", int(duration.Hours()/24))
	}
}

func (p *ResultsPane) SetResults(results []APIListing) {
	p.results = results
	p.selectedIdx = 0
	p.offset = 0
	p.loading = false
}
