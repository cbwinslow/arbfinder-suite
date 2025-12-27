# ArbFinder Suite Configuration Examples

## Analysis CLI Examples

This file contains example commands and configurations for the price analysis system.

### Basic Price Calculation

```bash
# Simple depreciation - 2 year old item in good condition
python3 backend/analysis_cli.py calculate \
  --base-price 500 \
  --age 2 \
  --condition good

# With completeness factor
python3 backend/analysis_cli.py calculate \
  --base-price 500 \
  --age 2 \
  --condition good \
  --completeness 85
```

### Vehicle Price Example

```bash
# 5 year old vehicle with multiple damage points
python3 backend/analysis_cli.py calculate \
  --base-price 25000 \
  --age 5 \
  --condition very_good \
  --damage aesthetic:passenger:minor \
  --damage dent:rear:moderate \
  --damage rust:bottom:minor \
  --supply 15 \
  --sales 8 \
  --completeness 100 \
  --output table
```

### Electronics Price Example

```bash
# 3 year old laptop with minor damage
python3 backend/analysis_cli.py calculate \
  --base-price 1200 \
  --age 3 \
  --condition good \
  --damage minor_scratch:top:minor \
  --category electronics \
  --completeness 90 \
  --supply 40 \
  --sales 20
```

### Seasonal Items

```bash
# Winter coat in summer (off-season)
python3 backend/analysis_cli.py calculate \
  --base-price 200 \
  --age 1 \
  --condition excellent \
  --category winter_gear \
  --completeness 100

# Back to school item in August (peak season)
python3 backend/analysis_cli.py calculate \
  --base-price 150 \
  --age 0.5 \
  --condition like_new \
  --category back_to_school \
  --completeness 100
```

### Collectibles (S-Curve Depreciation)

```bash
# Vintage item that may appreciate
python3 backend/analysis_cli.py depreciation \
  --base-price 500 \
  --age 7 \
  --model s_curve
```

### Batch Processing Examples

#### Input File Format (items.json)

```json
[
  {
    "title": "MacBook Pro 2020 16-inch",
    "base_price": 2400,
    "age_years": 3,
    "condition": "excellent",
    "damage_list": [
      {"type": "minor_scratch", "location": "bottom", "severity": "minor"}
    ],
    "category": "electronics",
    "completeness_pct": 95,
    "supply_count": 30,
    "recent_sales": 15
  },
  {
    "title": "Toyota Camry 2015",
    "base_price": 18000,
    "age_years": 8,
    "condition": "good",
    "damage_list": [
      {"type": "dent", "location": "passenger", "severity": "minor"},
      {"type": "aesthetic", "location": "rear", "severity": "minor"}
    ],
    "completeness_pct": 100,
    "supply_count": 50,
    "recent_sales": 10
  },
  {
    "title": "Designer Handbag",
    "base_price": 1500,
    "age_years": 2,
    "condition": "very_good",
    "damage_list": [],
    "completeness_pct": 100,
    "supply_count": 20,
    "recent_sales": 25
  }
]
```

#### Process Batch

```bash
# Calculate prices for all items
python3 backend/analysis_cli.py batch \
  --input items.json \
  --output analyzed_items.json \
  --operation price

# Generate metadata for all items
python3 backend/analysis_cli.py batch \
  --input items.json \
  --output enriched_items.json \
  --operation metadata

# Both price and metadata
python3 backend/analysis_cli.py batch \
  --input items.json \
  --output complete_analysis.json \
  --operation both
```

### Metadata Generation Examples

#### Input Item (item.json)

```json
{
  "title": "Samsung Galaxy S20 128GB Black Unlocked",
  "description": "Excellent condition smartphone with minor scratches on back. Includes original box, charger, and earbuds. Battery health at 92%. No cracks on screen. Fully functional, all features working perfectly.",
  "price": 450,
  "condition": "excellent",
  "source": "ebay",
  "category": "Electronics",
  "images": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ]
}
```

#### Generate Metadata

```bash
python3 backend/analysis_cli.py metadata \
  --file item.json \
  --output enriched.json
```

#### Expected Output (enriched.json)

```json
{
  "generated_at": "2024-01-15T10:30:00",
  "completeness_score": 87.5,
  "data_quality_score": 92.0,
  "enrichment_sources": ["text_extraction", "auto_tagging"],
  "specifications": {
    "brand": "samsung",
    "model": "galaxy s20",
    "size": "128gb",
    "color": "black"
  },
  "tags": [
    "electronics",
    "condition_excellent",
    "mid_range",
    "source_ebay"
  ]
}
```

## Pulumi Configuration Examples

### Development Environment

```bash
# Initialize stack
pulumi stack init dev

# Basic configuration
pulumi config set environment development
pulumi config set domain dev.arbfinder.example.com

# Database configuration
pulumi config set postgresql:host localhost
pulumi config set postgresql:port 5432
pulumi config set postgresql:username postgres
pulumi config set --secret postgresql:password dev-password
pulumi config set postgresql:database arbfinder_dev

# Application passwords
pulumi config set --secret db_app_password dev-app-password
pulumi config set --secret db_readonly_password dev-readonly-password

# Cloudflare (use test values for dev)
pulumi config set cloudflare:zone_id test-zone-id
pulumi config set cloudflare:account_id test-account-id

# Disable AWS for local dev
pulumi config set aws:enabled false
```

### Staging Environment

```bash
pulumi stack init staging

pulumi config set environment staging
pulumi config set domain staging.arbfinder.example.com

# Use RDS for staging
pulumi config set postgresql:host staging-db.rds.amazonaws.com
pulumi config set postgresql:port 5432
pulumi config set postgresql:username arbfinder_admin
pulumi config set --secret postgresql:password <strong-staging-password>
pulumi config set postgresql:database arbfinder

pulumi config set --secret db_app_password <staging-app-password>
pulumi config set --secret db_readonly_password <staging-readonly-password>

# Real Cloudflare for staging
pulumi config set cloudflare:zone_id <real-zone-id>
pulumi config set cloudflare:account_id <real-account-id>

# Enable AWS for staging
pulumi config set aws:enabled true
pulumi config set aws:region us-east-1
```

### Production Environment

```bash
pulumi stack init production

pulumi config set environment production
pulumi config set domain arbfinder.example.com

# Use RDS Multi-AZ for production
pulumi config set postgresql:host prod-db.rds.amazonaws.com
pulumi config set postgresql:port 5432
pulumi config set postgresql:username arbfinder_admin
pulumi config set --secret postgresql:password <strong-production-password>
pulumi config set postgresql:database arbfinder

pulumi config set --secret db_app_password <production-app-password>
pulumi config set --secret db_readonly_password <production-readonly-password>

# Production Cloudflare
pulumi config set cloudflare:zone_id <production-zone-id>
pulumi config set cloudflare:account_id <production-account-id>

# Enable all AWS resources
pulumi config set aws:enabled true
pulumi config set aws:region us-east-1
```

## Database Connection Examples

### psql Commands

```bash
# Connect as admin
psql postgresql://admin:password@host:5432/arbfinder

# Connect as app user
psql postgresql://arbfinder_app:password@host:5432/arbfinder

# Connect as readonly user
psql postgresql://arbfinder_readonly:password@host:5432/arbfinder

# Run migration
psql postgresql://admin:password@host:5432/arbfinder \
  -f database/migrations/001_initial_schema.sql
```

### Python Connection

```python
import psycopg2

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="arbfinder",
    user="arbfinder_app",
    password="password"
)

# Create cursor
cur = conn.cursor()

# Execute query
cur.execute("SELECT COUNT(*) FROM items WHERE status = 'active'")
count = cur.fetchone()[0]
print(f"Active items: {count}")

# Close
cur.close()
conn.close()
```

### SQLAlchemy Connection

```python
from sqlalchemy import create_engine

# Create engine
engine = create_engine(
    'postgresql://arbfinder_app:password@localhost:5432/arbfinder'
)

# Connect and query
with engine.connect() as conn:
    result = conn.execute("SELECT COUNT(*) FROM items")
    count = result.scalar()
    print(f"Total items: {count}")
```

## Integration Examples

### With Main ArbFinder CLI

```bash
# 1. Search for items using main CLI
arbfinder search "RTX 3080" --json rtx_items.json

# 2. Analyze prices
python3 backend/analysis_cli.py batch \
  --input rtx_items.json \
  --output rtx_analyzed.json \
  --operation price

# 3. View results
cat rtx_analyzed.json | jq '.[] | {
  title: .item.title,
  original: .item.price,
  adjusted: .price_analysis.final_price,
  discount: .price_analysis.total_adjustment_pct
}'
```

### API Integration

```python
from fastapi import FastAPI
from backend.analysis_cli import PriceAnalyzer
from decimal import Decimal

app = FastAPI()
analyzer = PriceAnalyzer()

@app.post("/api/calculate-price")
async def calculate_price(
    base_price: float,
    age_years: float,
    condition: str
):
    result = analyzer.calculate_comprehensive_price(
        base_price=Decimal(str(base_price)),
        age_years=Decimal(str(age_years)),
        condition=condition
    )
    return result
```

## Environment Variables

### Backend Configuration

```bash
# Database
export DATABASE_URL="postgresql://arbfinder_app:password@localhost:5432/arbfinder"
export DATABASE_READONLY_URL="postgresql://arbfinder_readonly:password@localhost:5432/arbfinder"

# API Keys
export STRIPE_SECRET_KEY="sk_test_..."
export CLOUDFLARE_API_TOKEN="..."
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."

# Application
export ENVIRONMENT="development"
export LOG_LEVEL="INFO"
export CORS_ORIGINS="http://localhost:3000,http://localhost:8080"
```

### Frontend Configuration (.env.local)

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8080
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_test_...
```

## Docker Compose Example

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: arbfinder
      POSTGRES_USER: arbfinder_app
      POSTGRES_PASSWORD: dev-password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/migrations:/docker-entrypoint-initdb.d

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: .
    environment:
      DATABASE_URL: postgresql://arbfinder_app:dev-password@postgres:5432/arbfinder
      REDIS_URL: redis://redis:6379
    ports:
      - "8080:8080"
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_BASE: http://localhost:8080
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

## Useful Queries

### Get Price Statistics

```sql
-- Average prices by condition
SELECT 
    condition,
    COUNT(*) as count,
    AVG(current_price) as avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY current_price) as median_price
FROM items
WHERE status = 'active'
GROUP BY condition
ORDER BY avg_price DESC;
```

### Find Items with High Depreciation

```sql
-- Items with >50% price drop
SELECT 
    title,
    base_price,
    current_price,
    (base_price - current_price) / base_price * 100 as depreciation_pct
FROM items
WHERE base_price > 0
AND (base_price - current_price) / base_price > 0.5
ORDER BY depreciation_pct DESC
LIMIT 20;
```

### Market Trends by Category

```sql
-- Price trends by category
SELECT * FROM v_market_trends
ORDER BY avg_price DESC;
```

## Monitoring Queries

### Check System Health

```sql
-- Database size
SELECT pg_size_pretty(pg_database_size('arbfinder'));

-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Performance Metrics

```bash
# API response times
curl -w "\nTime: %{time_total}s\n" http://localhost:8080/api/items

# Database connection test
time psql postgresql://arbfinder_app:password@localhost:5432/arbfinder -c "SELECT 1"
```
