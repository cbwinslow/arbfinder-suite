# @arbfinder/client

TypeScript/JavaScript client for the ArbFinder API.

## Installation

```bash
npm install @arbfinder/client
```

## Usage

```typescript
import { ArbFinderClient } from '@arbfinder/client';

// Create a client instance
const client = new ArbFinderClient({
  baseURL: 'http://localhost:8080',
  timeout: 30000,
});

// Get listings
const listings = await client.getListings({
  limit: 10,
  offset: 0,
  order_by: 'ts',
});

// Search listings
const results = await client.searchListings('RTX 3060');

// Get statistics
const stats = await client.getStatistics();

// Get comparable prices
const comps = await client.getComps();

// Search comps
const compResults = await client.searchComps('iPad');
```

## API

### Constructor

```typescript
new ArbFinderClient(config?: ArbFinderClientConfig)
```

**Config Options:**
- `baseURL` - API base URL (default: `http://localhost:8080`)
- `timeout` - Request timeout in milliseconds (default: `30000`)
- `headers` - Custom headers to include in requests

### Methods

#### `getInfo()`
Get API information.

#### `getListings(params?)`
Get listings with pagination and filtering.

**Parameters:**
- `limit` - Number of results per page
- `offset` - Offset for pagination
- `order_by` - Sort field ('ts', 'price', or 'title')
- `source` - Filter by source

#### `searchListings(query)`
Search listings by query string.

#### `createListing(listing)`
Create a new listing.

#### `getStatistics()`
Get database statistics.

#### `getComps(params?)`
Get comparable prices with pagination.

#### `searchComps(query)`
Search comparable prices by query.

#### `createCheckoutSession(title, price)`
Create a Stripe checkout session.

## Types

All TypeScript types are exported:
- `Listing`
- `Comp`
- `Statistics`
- `ListingsResponse`
- `PaginationParams`
- `SearchParams`
- `ArbFinderClientConfig`

## License

MIT
