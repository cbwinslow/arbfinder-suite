package main

import (
	"fmt"
	"strings"

	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

type SearchPane struct {
	queryInput     textinput.Model
	providerSelect int
	thresholdInput textinput.Model
	focusIndex     int
	providers      []string
	searching      bool
	lastQuery      string
	lastError      string
}

func NewSearchPane() *SearchPane {
	queryInput := textinput.New()
	queryInput.Placeholder = "Enter search query (e.g., 'RTX 3060')"
	queryInput.Focus()
	queryInput.Width = 50

	thresholdInput := textinput.New()
	thresholdInput.Placeholder = "20.0"
	thresholdInput.Width = 10

	return &SearchPane{
		queryInput:     queryInput,
		thresholdInput: thresholdInput,
		providers:      []string{"shopgoodwill", "govdeals", "governmentsurplus", "manual"},
		providerSelect: 0,
		focusIndex:     0,
	}
}

func (p *SearchPane) Update(msg tea.Msg) (SearchPane, tea.Cmd) {
	var cmd tea.Cmd

	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "enter":
			if p.focusIndex == 0 && p.queryInput.Value() != "" {
				p.lastQuery = p.queryInput.Value()
				p.searching = true
				p.lastError = ""
				// Search will be triggered by the main model
				// which checks for p.searching and p.lastQuery
				return *p, nil
			}
			return *p, nil

		case "up":
			if p.focusIndex > 0 {
				p.focusIndex--
				p.updateFocus()
			}
			return *p, nil

		case "down":
			if p.focusIndex < 2 {
				p.focusIndex++
				p.updateFocus()
			}
			return *p, nil

		case "left":
			if p.focusIndex == 1 && p.providerSelect > 0 {
				p.providerSelect--
			}
			return *p, nil

		case "right":
			if p.focusIndex == 1 && p.providerSelect < len(p.providers)-1 {
				p.providerSelect++
			}
			return *p, nil
		}
	}

	if p.focusIndex == 0 {
		p.queryInput, cmd = p.queryInput.Update(msg)
	} else if p.focusIndex == 2 {
		p.thresholdInput, cmd = p.thresholdInput.Update(msg)
	}

	return *p, cmd
}

func (p *SearchPane) updateFocus() {
	p.queryInput.Blur()
	p.thresholdInput.Blur()

	if p.focusIndex == 0 {
		p.queryInput.Focus()
	} else if p.focusIndex == 2 {
		p.thresholdInput.Focus()
	}
}

func (p *SearchPane) View(width, height int) string {
	var b strings.Builder

	titleStyle := lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("#7D56F4")).
		MarginBottom(1)

	labelStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#FAFAFA")).
		Bold(true)

	infoStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#626262")).
		Italic(true)

	errorStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#FF0000")).
		Bold(true)

	// Title
	b.WriteString(titleStyle.Render("🔍 Search for Arbitrage Opportunities"))
	b.WriteString("\n\n")

	// Query input
	b.WriteString(labelStyle.Render("Search Query:"))
	b.WriteString("\n")
	b.WriteString(p.queryInput.View())
	b.WriteString("\n\n")

	// Provider selection
	b.WriteString(labelStyle.Render("Provider:"))
	b.WriteString("\n")
	
	providerStyle := lipgloss.NewStyle().
		Padding(0, 1).
		Margin(0, 1, 0, 0)

	selectedProviderStyle := providerStyle.Copy().
		Bold(true).
		Foreground(lipgloss.Color("#FAFAFA")).
		Background(lipgloss.Color("#7D56F4"))

	for i, provider := range p.providers {
		if i == p.providerSelect && p.focusIndex == 1 {
			b.WriteString(selectedProviderStyle.Render(provider))
		} else {
			b.WriteString(providerStyle.Render(provider))
		}
	}
	b.WriteString("\n")
	b.WriteString(infoStyle.Render("Use ←/→ to select provider"))
	b.WriteString("\n\n")

	// Threshold input
	b.WriteString(labelStyle.Render("Minimum Discount Threshold (%):"))
	b.WriteString("\n")
	b.WriteString(p.thresholdInput.View())
	b.WriteString("\n\n")

	// Instructions
	b.WriteString(infoStyle.Render("↑/↓: Navigate fields • Enter: Search • Tab: Switch pane"))
	b.WriteString("\n\n")

	// Status
	if p.searching {
		statusStyle := lipgloss.NewStyle().
			Foreground(lipgloss.Color("#00FF00")).
			Bold(true)
		b.WriteString(statusStyle.Render("🔄 Searching..."))
	} else if p.lastQuery != "" {
		statusStyle := lipgloss.NewStyle().
			Foreground(lipgloss.Color("#00FF00"))
		b.WriteString(statusStyle.Render(fmt.Sprintf("✓ Last search: %s", p.lastQuery)))
	}

	// Error
	if p.lastError != "" {
		b.WriteString("\n")
		b.WriteString(errorStyle.Render(fmt.Sprintf("✗ Error: %s", p.lastError)))
	}

	return b.String()
}
