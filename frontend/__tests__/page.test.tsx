/**
 * Tests for the main page component
 */

import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import Home from '../app/page'

// Mock fetch
global.fetch = jest.fn()

describe('Home Page', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear()
  })

  it('renders the main heading', () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: async () => ([]),
      ok: true,
    })

    render(<Home />)
    
    const heading = screen.getByText('ArbFinder Suite')
    expect(heading).toBeInTheDocument()
  })

  it('renders the search section', () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: async () => ([]),
      ok: true,
    })

    render(<Home />)
    
    const searchHeading = screen.getByText(/Search & Filter/i)
    expect(searchHeading).toBeInTheDocument()
  })

  it('renders the add listing section', () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: async () => ([]),
      ok: true,
    })

    render(<Home />)
    
    const addListingHeading = screen.getByText(/Add Listing/i)
    expect(addListingHeading).toBeInTheDocument()
  })

  it('displays search input', () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: async () => ([]),
      ok: true,
    })

    render(<Home />)
    
    const searchInput = screen.getByPlaceholderText(/Search listings/i)
    expect(searchInput).toBeInTheDocument()
  })

  it('displays sort dropdown', () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: async () => ([]),
      ok: true,
    })

    render(<Home />)
    
    const sortLabel = screen.getByText(/Sort By/i)
    expect(sortLabel).toBeInTheDocument()
  })

  it('displays filter dropdown', () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: async () => ([]),
      ok: true,
    })

    render(<Home />)
    
    const filterLabel = screen.getByText(/Filter by Source/i)
    expect(filterLabel).toBeInTheDocument()
  })

  it('renders link to comps page', () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: async () => ([]),
      ok: true,
    })

    render(<Home />)
    
    const compsLink = screen.getByText(/View Comps/i)
    expect(compsLink).toBeInTheDocument()
  })

  it('shows loading state initially', async () => {
    (fetch as jest.Mock).mockImplementation(() => 
      new Promise((resolve) => {
        setTimeout(() => resolve({
          json: async () => ({ data: [] }),
          ok: true,
        }), 100)
      })
    )

    render(<Home />)
    
    // Check that loading indicator appears
    await waitFor(() => {
      const loadingText = screen.queryByText(/Loading/i)
      expect(loadingText).toBeInTheDocument()
    })
  })

  it('displays no listings message when empty', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: async () => ({ data: [] }),
      ok: true,
    })

    render(<Home />)
    
    await waitFor(() => {
      const noListingsText = screen.queryByText(/No listings found/i)
      expect(noListingsText).toBeInTheDocument()
    })
  })
})
