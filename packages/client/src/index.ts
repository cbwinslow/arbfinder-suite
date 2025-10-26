/**
 * ArbFinder API Client
 * 
 * TypeScript/JavaScript client for interacting with the ArbFinder API.
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

/**
 * Listing interface matching the API response
 */
export interface Listing {
  source: string;
  url: string;
  title: string;
  price: number;
  currency: string;
  condition: string;
  ts: number;
  meta?: Record<string, any>;
}

/**
 * Comparable price information
 */
export interface Comp {
  key_title: string;
  avg_price: number;
  median_price: number;
  count: number;
  ts: number;
}

/**
 * Statistics response from API
 */
export interface Statistics {
  total_listings: number;
  unique_sources: number;
  avg_price: number;
  total_comps: number;
  [key: string]: any;
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
  limit?: number;
  offset?: number;
  order_by?: 'ts' | 'price' | 'title';
  source?: string;
}

/**
 * Search parameters
 */
export interface SearchParams {
  q: string;
}

/**
 * API response with pagination
 */
export interface ListingsResponse {
  data: Listing[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * Client configuration options
 */
export interface ArbFinderClientConfig {
  baseURL?: string;
  timeout?: number;
  headers?: Record<string, string>;
}

/**
 * ArbFinder API Client
 */
export class ArbFinderClient {
  private client: AxiosInstance;

  /**
   * Create a new ArbFinder API client
   * 
   * @param config - Client configuration
   */
  constructor(config: ArbFinderClientConfig = {}) {
    const { 
      baseURL = 'http://localhost:8080',
      timeout = 30000,
      headers = {}
    } = config;

    this.client = axios.create({
      baseURL,
      timeout,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
    });
  }

  /**
   * Get API information
   */
  async getInfo(): Promise<any> {
    const response = await this.client.get('/');
    return response.data;
  }

  /**
   * Get listings with pagination and filtering
   * 
   * @param params - Pagination parameters
   */
  async getListings(params: PaginationParams = {}): Promise<ListingsResponse> {
    const response = await this.client.get('/api/listings', { params });
    return response.data;
  }

  /**
   * Search listings by query
   * 
   * @param query - Search query string
   */
  async searchListings(query: string): Promise<Listing[]> {
    const response = await this.client.get('/api/listings/search', {
      params: { q: query },
    });
    return response.data;
  }

  /**
   * Create a new listing
   * 
   * @param listing - Listing data to create
   */
  async createListing(listing: Partial<Listing>): Promise<Listing> {
    const response = await this.client.post('/api/listings', listing);
    return response.data;
  }

  /**
   * Get database statistics
   */
  async getStatistics(): Promise<Statistics> {
    const response = await this.client.get('/api/statistics');
    return response.data;
  }

  /**
   * Get comparable prices
   * 
   * @param params - Pagination parameters
   */
  async getComps(params: PaginationParams = {}): Promise<Comp[]> {
    const response = await this.client.get('/api/comps', { params });
    return response.data;
  }

  /**
   * Search comparable prices
   * 
   * @param query - Search query string
   */
  async searchComps(query: string): Promise<Comp[]> {
    const response = await this.client.get('/api/comps/search', {
      params: { q: query },
    });
    return response.data;
  }

  /**
   * Create Stripe checkout session
   * 
   * @param title - Product title
   * @param price - Product price
   */
  async createCheckoutSession(title: string, price: number): Promise<{ url: string }> {
    const response = await this.client.post('/api/stripe/create-checkout-session', null, {
      params: { title, price: price.toString() },
    });
    return response.data;
  }

  /**
   * Make a custom request to the API
   * 
   * @param config - Axios request configuration
   */
  async request<T = any>(config: AxiosRequestConfig): Promise<T> {
    const response = await this.client.request<T>(config);
    return response.data;
  }
}

/**
 * Default export
 */
export default ArbFinderClient;
