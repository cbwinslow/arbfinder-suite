/**
 * Tests for ArbFinder API Client
 */

import MockAdapter from 'axios-mock-adapter';
import { ArbFinderClient, Listing, Statistics, Comp } from '../src/index';
describe('ArbFinderClient', () => {
  let client: ArbFinderClient;
  let mock: MockAdapter;

  beforeEach(() => {
    client = new ArbFinderClient({ baseURL: 'http://localhost:8080' });
    mock = new MockAdapter((client as any).client);
  });

  afterEach(() => {
    mock.restore();
  });

  describe('constructor', () => {
    it('should create client with default config', () => {
      const defaultClient = new ArbFinderClient();
      expect(defaultClient).toBeInstanceOf(ArbFinderClient);
    });

    it('should create client with custom config', () => {
      const customClient = new ArbFinderClient({
        baseURL: 'https://api.example.com',
        timeout: 5000,
        headers: { 'X-Custom': 'value' },
      });
      expect(customClient).toBeInstanceOf(ArbFinderClient);
    });
  });

  describe('getInfo', () => {
    it('should fetch API information', async () => {
      const mockData = { name: 'ArbFinder API', version: '1.0' };
      mock.onGet('/').reply(200, mockData);

      const data = await client.getInfo();
      expect(data).toEqual(mockData);
    });

    it('should handle errors', async () => {
      mock.onGet('/').networkError();

      await expect(client.getInfo()).rejects.toThrow();
    });
  });

  describe('getListings', () => {
    it('should fetch listings without parameters', async () => {
      const mockData = {
        data: [
          {
            source: 'test',
            url: 'https://example.com/item1',
            title: 'Test Item',
            price: 100,
            currency: 'USD',
            condition: 'New',
            ts: 1234567890,
          },
        ],
        total: 1,
        limit: 10,
        offset: 0,
      };
      mock.onGet('/api/listings').reply(200, mockData);

      const data = await client.getListings();
      expect(data).toEqual(mockData);
      expect(data.data).toHaveLength(1);
    });

    it('should fetch listings with pagination', async () => {
      const mockData = {
        data: [],
        total: 100,
        limit: 20,
        offset: 40,
      };
      mock.onGet('/api/listings').reply(200, mockData);

      const data = await client.getListings({ limit: 20, offset: 40 });
      expect(data.limit).toBe(20);
      expect(data.offset).toBe(40);
    });

    it('should fetch listings with filtering', async () => {
      const mockData = {
        data: [],
        total: 10,
        limit: 10,
        offset: 0,
      };
      mock.onGet('/api/listings').reply(200, mockData);

      const data = await client.getListings({ 
        source: 'shopgoodwill',
        order_by: 'price' 
      });
      expect(data).toEqual(mockData);
    });
  });

  describe('searchListings', () => {
    it('should search listings by query', async () => {
      const mockData: Listing[] = [
        {
          source: 'test',
          url: 'https://example.com/item1',
          title: 'RTX 3060 Graphics Card',
          price: 300,
          currency: 'USD',
          condition: 'Used',
          ts: 1234567890,
        },
      ];
      mock.onGet('/api/listings/search').reply(200, mockData);

      const data = await client.searchListings('RTX 3060');
      expect(data).toEqual(mockData);
      expect(data[0].title).toContain('RTX 3060');
    });

    it('should return empty array for no results', async () => {
      mock.onGet('/api/listings/search').reply(200, []);

      const data = await client.searchListings('nonexistent');
      expect(data).toEqual([]);
    });
  });

  describe('createListing', () => {
    it('should create a new listing', async () => {
      const newListing = {
        source: 'manual',
        url: 'https://example.com/new-item',
        title: 'New Test Item',
        price: 150,
        currency: 'USD',
        condition: 'New',
        ts: Date.now() / 1000,
      };
      mock.onPost('/api/listings').reply(201, newListing);

      const data = await client.createListing(newListing);
      expect(data).toEqual(newListing);
    });

    it('should handle validation errors', async () => {
      mock.onPost('/api/listings').reply(400, { error: 'Invalid data' });

      await expect(client.createListing({})).rejects.toThrow();
    });
  });

  describe('getStatistics', () => {
    it('should fetch database statistics', async () => {
      const mockStats: Statistics = {
        total_listings: 1000,
        unique_sources: 5,
        avg_price: 125.50,
        total_comps: 250,
        recent_listings: 50,
      };
      mock.onGet('/api/statistics').reply(200, mockStats);

      const data = await client.getStatistics();
      expect(data).toEqual(mockStats);
      expect(data.total_listings).toBe(1000);
    });
  });

  describe('getComps', () => {
    it('should fetch comparable prices', async () => {
      const mockComps: Comp[] = [
        {
          key_title: 'rtx 3060',
          avg_price: 350,
          median_price: 340,
          count: 50,
          ts: 1234567890,
        },
      ];
      mock.onGet('/api/comps').reply(200, mockComps);

      const data = await client.getComps();
      expect(data).toEqual(mockComps);
      expect(data[0].key_title).toBe('rtx 3060');
    });

    it('should fetch comps with pagination', async () => {
      mock.onGet('/api/comps').reply(200, []);

      const data = await client.getComps({ limit: 50, offset: 100 });
      expect(Array.isArray(data)).toBe(true);
    });
  });

  describe('searchComps', () => {
    it('should search comparable prices', async () => {
      const mockComps: Comp[] = [
        {
          key_title: 'ipad pro',
          avg_price: 800,
          median_price: 750,
          count: 100,
          ts: 1234567890,
        },
      ];
      mock.onGet('/api/comps/search').reply(200, mockComps);

      const data = await client.searchComps('iPad');
      expect(data).toEqual(mockComps);
    });
  });

  describe('createCheckoutSession', () => {
    it('should create Stripe checkout session', async () => {
      const mockResponse = { url: 'https://checkout.stripe.com/session/xyz' };
      mock.onPost('/api/stripe/create-checkout-session').reply(200, mockResponse);

      const data = await client.createCheckoutSession('Test Product', 99.99);
      expect(data).toEqual(mockResponse);
      expect(data.url).toContain('stripe.com');
    });

    it('should handle checkout errors', async () => {
      mock.onPost('/api/stripe/create-checkout-session').reply(500, { error: 'Stripe error' });

      await expect(client.createCheckoutSession('Item', 50)).rejects.toThrow();
    });
  });

  describe('request', () => {
    it('should make custom requests', async () => {
      const mockData = { custom: 'data' };
      mock.onGet('/custom/endpoint').reply(200, mockData);

      const data = await client.request({ method: 'GET', url: '/custom/endpoint' });
      expect(data).toEqual(mockData);
    });
  });

  describe('error handling', () => {
    it('should handle network errors', async () => {
      mock.onGet('/api/listings').networkError();

      await expect(client.getListings()).rejects.toThrow();
    });

    it('should handle timeout errors', async () => {
      mock.onGet('/api/listings').timeout();

      await expect(client.getListings()).rejects.toThrow();
    });

    it('should handle 404 errors', async () => {
      mock.onGet('/api/nonexistent').reply(404);

      await expect(client.request({ url: '/api/nonexistent' })).rejects.toThrow();
    });

    it('should handle 500 errors', async () => {
      mock.onGet('/api/listings').reply(500, { error: 'Internal server error' });

      await expect(client.getListings()).rejects.toThrow();
    });
  });
});
