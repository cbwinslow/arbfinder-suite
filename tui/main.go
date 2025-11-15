package main

import (
	"fmt"
	"os"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// Main model for the application
type model struct {
	currentPane int
	width       int
	height      int
	search      *SearchPane
	results     *ResultsPane
	stats       *StatsPane
	config      *ConfigPane
	db          *Database
}

// Initialize the model
func initialModel() model {
	db := NewDatabase()
	return model{
		currentPane: 0,
		search:      NewSearchPane(),
		results:     NewResultsPane(),
		stats:       NewStatsPane(),
		config:      NewConfigPane(),
		db:          db,
	}
}

// Init implements tea.Model
func (m model) Init() tea.Cmd {
	return nil
}

// Update implements tea.Model
func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		return m, nil

	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c", "q":
			return m, tea.Quit

		case "tab":
			m.currentPane = (m.currentPane + 1) % 4
			return m, nil

		case "shift+tab":
			m.currentPane = (m.currentPane - 1 + 4) % 4
			return m, nil
		}
	}

	// Update the current pane
	var cmd tea.Cmd
	switch m.currentPane {
	case 0:
		*m.search, cmd = m.search.Update(msg)
	case 1:
		*m.results, cmd = m.results.Update(msg)
	case 2:
		*m.stats, cmd = m.stats.Update(msg)
	case 3:
		*m.config, cmd = m.config.Update(msg)
	}

	return m, cmd
}

// View implements tea.Model
func (m model) View() string {
	if m.width == 0 {
		return "Initializing..."
	}

	// Define styles
	titleStyle := lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("#7D56F4")).
		Background(lipgloss.Color("#1a1a1a")).
		Padding(0, 1)

	activeTabStyle := lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("#FAFAFA")).
		Background(lipgloss.Color("#7D56F4")).
		Padding(0, 2)

	inactiveTabStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#888888")).
		Background(lipgloss.Color("#1a1a1a")).
		Padding(0, 2)

	// Build title
	title := titleStyle.Render("🔍 ArbFinder Suite - Interactive TUI")

	// Build tabs
	tabs := []string{"Search", "Results", "Stats", "Config"}
	tabsStr := ""
	for i, tab := range tabs {
		if i == m.currentPane {
			tabsStr += activeTabStyle.Render(tab)
		} else {
			tabsStr += inactiveTabStyle.Render(tab)
		}
		if i < len(tabs)-1 {
			tabsStr += " "
		}
	}

	// Build content based on current pane
	var content string
	contentHeight := m.height - 6 // Reserve space for title, tabs, and help

	switch m.currentPane {
	case 0:
		content = m.search.View(m.width, contentHeight)
	case 1:
		content = m.results.View(m.width, contentHeight)
	case 2:
		content = m.stats.View(m.width, contentHeight)
	case 3:
		content = m.config.View(m.width, contentHeight)
	}

	// Help text
	helpStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#626262")).
		Padding(0, 1)
	help := helpStyle.Render("Tab: Switch Pane • Ctrl+C/Q: Quit • Enter: Execute • ↑/↓: Navigate")

	// Combine all elements
	return lipgloss.JoinVertical(
		lipgloss.Left,
		title,
		tabsStr,
		"",
		content,
		"",
		help,
	)
}

func main() {
	p := tea.NewProgram(initialModel(), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error running program: %v\n", err)
		os.Exit(1)
	}
}
