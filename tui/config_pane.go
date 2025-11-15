package main

import (
	"fmt"
	"strings"

	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

type ConfigPane struct {
	configs       []SavedConfig
	selectedIdx   int
	newConfigName textinput.Model
	apiURL        textinput.Model
	focusIndex    int
	saving        bool
	loading       bool
	lastError     string
	lastSuccess   string
	db            *Database
}

func NewConfigPane() *ConfigPane {
	nameInput := textinput.New()
	nameInput.Placeholder = "config_name"
	nameInput.Width = 30

	apiInput := textinput.New()
	apiInput.Placeholder = "http://localhost:8080"
	apiInput.Width = 40

	return &ConfigPane{
		configs:       []SavedConfig{},
		newConfigName: nameInput,
		apiURL:        apiInput,
		focusIndex:    0,
	}
}

func (p *ConfigPane) Update(msg tea.Msg) (ConfigPane, tea.Cmd) {
	var cmd tea.Cmd

	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "up":
			if p.focusIndex > 0 {
				p.focusIndex--
				p.updateFocus()
			} else if len(p.configs) > 0 && p.selectedIdx > 0 {
				p.selectedIdx--
			}
			return *p, nil

		case "down":
			if p.focusIndex < 2 {
				p.focusIndex++
				p.updateFocus()
			} else if len(p.configs) > 0 && p.selectedIdx < len(p.configs)-1 {
				p.selectedIdx++
			}
			return *p, nil

		case "s":
			// Save current configuration
			if p.newConfigName.Value() != "" {
				p.saving = true
				// TODO: Save config
				p.lastSuccess = fmt.Sprintf("Configuration '%s' saved", p.newConfigName.Value())
				p.newConfigName.SetValue("")
			}
			return *p, nil

		case "l":
			// Load selected configuration
			if len(p.configs) > 0 && p.selectedIdx < len(p.configs) {
				// TODO: Load config
				p.lastSuccess = fmt.Sprintf("Configuration '%s' loaded", p.configs[p.selectedIdx].Name)
			}
			return *p, nil

		case "d":
			// Delete selected configuration
			if len(p.configs) > 0 && p.selectedIdx < len(p.configs) {
				// TODO: Delete config
				p.lastSuccess = "Configuration deleted"
			}
			return *p, nil

		case "r":
			// Refresh config list
			p.loading = true
			// TODO: Refresh
			return *p, nil
		}
	}

	if p.focusIndex == 0 {
		p.newConfigName, cmd = p.newConfigName.Update(msg)
	} else if p.focusIndex == 1 {
		p.apiURL, cmd = p.apiURL.Update(msg)
	}

	return *p, cmd
}

func (p *ConfigPane) updateFocus() {
	p.newConfigName.Blur()
	p.apiURL.Blur()

	if p.focusIndex == 0 {
		p.newConfigName.Focus()
	} else if p.focusIndex == 1 {
		p.apiURL.Focus()
	}
}

func (p *ConfigPane) View(width, height int) string {
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
		Foreground(lipgloss.Color("#FAFAFA")).
		Bold(true)

	itemStyle := lipgloss.NewStyle().
		Padding(0, 1)

	selectedItemStyle := itemStyle.Copy().
		Background(lipgloss.Color("#7D56F4")).
		Bold(true)

	infoStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#626262")).
		Italic(true)

	successStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#00FF00")).
		Bold(true)

	errorStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#FF0000")).
		Bold(true)

	// Title
	b.WriteString(titleStyle.Render("⚙️  Configuration Manager"))
	b.WriteString("\n\n")

	// New configuration section
	b.WriteString(sectionStyle.Render("📝 New Configuration"))
	b.WriteString("\n")
	
	b.WriteString(labelStyle.Render("Config Name:"))
	b.WriteString("\n")
	b.WriteString(p.newConfigName.View())
	b.WriteString("\n\n")

	b.WriteString(labelStyle.Render("API URL:"))
	b.WriteString("\n")
	b.WriteString(p.apiURL.View())
	b.WriteString("\n")
	b.WriteString(infoStyle.Render("Press 's' to save current configuration"))
	b.WriteString("\n")

	// Saved configurations
	b.WriteString("\n")
	b.WriteString(sectionStyle.Render(fmt.Sprintf("💾 Saved Configurations (%d)", len(p.configs))))
	b.WriteString("\n")

	if p.loading {
		statusStyle := lipgloss.NewStyle().
			Foreground(lipgloss.Color("#00FF00")).
			Bold(true)
		b.WriteString(statusStyle.Render("🔄 Loading..."))
		b.WriteString("\n")
	} else if len(p.configs) == 0 {
		b.WriteString(infoStyle.Render("No saved configurations yet"))
		b.WriteString("\n")
	} else {
		for i, config := range p.configs {
			line := fmt.Sprintf("%s (created: %s)",
				config.Name,
				config.CreatedAt.Format("2006-01-02 15:04"),
			)
			if i == p.selectedIdx && p.focusIndex == 2 {
				b.WriteString(selectedItemStyle.Render("▸ " + line))
			} else {
				b.WriteString(itemStyle.Render("  " + line))
			}
			b.WriteString("\n")
		}
	}

	// Instructions
	b.WriteString("\n")
	b.WriteString(infoStyle.Render("↑/↓: Navigate • s: Save • l: Load • d: Delete • r: Refresh • Tab: Switch pane"))

	// Status messages
	if p.lastSuccess != "" {
		b.WriteString("\n\n")
		b.WriteString(successStyle.Render("✓ " + p.lastSuccess))
	}

	if p.lastError != "" {
		b.WriteString("\n\n")
		b.WriteString(errorStyle.Render("✗ Error: " + p.lastError))
	}

	return b.String()
}

func (p *ConfigPane) LoadConfigs(db *Database) {
	if db != nil {
		configs, err := db.GetAllConfigs()
		if err == nil {
			p.configs = configs
		} else {
			p.lastError = err.Error()
		}
	}
	p.loading = false
}
