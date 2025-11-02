# Advanced Price Analysis CLI

Comprehensive command-line tool for calculating price adjustments, managing metadata, and performing batch operations.

## Features

- **Price Calculation**: Multi-factor price adjustments (age, condition, damage, market, seasonal)
- **Depreciation Models**: Linear, exponential, and S-curve depreciation
- **Damage Assessment**: Location and severity-based price impacts
- **Metadata Generation**: Automated metadata enrichment
- **Batch Processing**: Process thousands of items efficiently

## Installation

```bash
# Install dependencies
pip install rich  # Optional, for enhanced output

# Make executable
chmod +x backend/analysis_cli.py

# Create alias (optional)
echo "alias arbf-analysis='python3 backend/analysis_cli.py'" >> ~/.bashrc
source ~/.bashrc
```

## Commands

### 1. Calculate Comprehensive Price

Calculate final price with all adjustments applied.

```bash
python3 backend/analysis_cli.py calculate \
  --base-price 500 \
  --age 2.5 \
  --condition excellent \
  --damage aesthetic:passenger:minor \
  --damage dent:front:moderate \
  --supply 30 \
  --sales 15 \
  --category electronics \
  --completeness 90 \
  --output table
```

**Parameters:**
- `--base-price`: Original price (required)
- `--age`: Age in years (default: 0)
- `--condition`: Item condition (default: good)
  - Options: new, like_new, excellent, very_good, good, fair, poor
- `--damage`: Damage specification (can be used multiple times)
  - Format: `type:location:severity`
  - Types: minor_scratch, dent, aesthetic, structural, rust, crack, discoloration
  - Locations: front, passenger, rear, driver, top, bottom, side
  - Severity: minor, moderate, major, severe
- `--supply`: Market supply count (default: 50)
- `--sales`: Recent sales count (default: 10)
- `--category`: Item category for seasonal adjustment
  - Options: winter_gear, summer_gear, back_to_school, holiday_items
- `--completeness`: Percentage complete (default: 100)
- `--output`: Output format (table or json)

**Example Output:**

```
Price Adjustments
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Type            ┃ Factor  ┃ Amount  ┃ Description                       ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ age_depreciation│ 0.5946  │ $202.70 │ 2.5 years old                     │
│ condition       │ 0.8500  │ $44.68  │ Condition: excellent              │
│ damage          │ 0.9703  │ $7.51   │ minor aesthetic on passenger      │
│ market          │ 1.0000  │ $0.00   │ Supply: 30, Recent sales: 15      │
│ completeness    │ 0.9000  │ $24.56  │ 90% complete                      │
└─────────────────┴─────────┴─────────┴───────────────────────────────────┘

╭─────── Price Summary ───────╮
│                             │
│ Base Price:     $500.00     │
│ Final Price:    $220.55     │
│ Total Adj:      $279.45 (55.9%)│
│                             │
╰─────────────────────────────╯
```

### 2. Calculate Depreciation

Calculate depreciation using specific models.

```bash
# Linear depreciation
python3 backend/analysis_cli.py depreciation \
  --base-price 1000 \
  --age 3 \
  --model linear \
  --rate 0.15

# Exponential depreciation
python3 backend/analysis_cli.py depreciation \
  --base-price 1000 \
  --age 3 \
  --model exponential \
  --half-life 2.5

# S-curve depreciation (for collectibles)
python3 backend/analysis_cli.py depreciation \
  --base-price 1000 \
  --age 7 \
  --model s_curve
```

**Models:**

1. **Linear**: Constant percentage per year
   - Formula: `price = base * (1 - age * rate)`
   - Best for: Furniture, appliances

2. **Exponential**: Accelerating decay
   - Formula: `price = base * 0.5^(age/half_life)`
   - Best for: Electronics, technology

3. **S-Curve**: Initial drop then stabilization
   - Formula: Complex piecewise function
   - Best for: Collectibles, antiques

### 3. Damage Assessment

Calculate price impact of specific damage.

```bash
python3 backend/analysis_cli.py damage \
  --base-price 800 \
  --type dent \
  --location passenger \
  --severity moderate
```

**Example Output:**

```
Base Price: $800.00
Damage: moderate dent on passenger
Adjusted Price: $744.00
Price Reduction: $56.00 (-7.0%)

Breakdown:
  Damage multiplier: 0.70
  Location multiplier: 1.00
  Severity multiplier: 1.00
```

### 4. Metadata Generation

Generate enhanced metadata for an item.

```bash
# From JSON file
python3 backend/analysis_cli.py metadata \
  --file item_data.json \
  --output enriched_metadata.json

# Output to stdout
python3 backend/analysis_cli.py metadata \
  --file item_data.json
```

**Input Format (item_data.json):**

```json
{
  "title": "Samsung Galaxy S20 128GB Black Unlocked",
  "description": "Excellent condition smartphone with minor scratches...",
  "price": 450,
  "condition": "excellent",
  "source": "ebay",
  "category": "Electronics",
  "images": ["url1", "url2"]
}
```

**Generated Metadata:**

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

### 5. Batch Processing

Process multiple items at once.

```bash
python3 backend/analysis_cli.py batch \
  --input items.json \
  --output results.json \
  --operation both
```

**Operations:**
- `price`: Calculate prices only
- `metadata`: Generate metadata only
- `both`: Both price and metadata

**Input Format (items.json):**

```json
[
  {
    "title": "Item 1",
    "base_price": 100,
    "age_years": 1,
    "condition": "good",
    "damage_list": [
      {"type": "aesthetic", "location": "side", "severity": "minor"}
    ],
    "category": "electronics",
    "completeness_pct": 100
  },
  {
    "title": "Item 2",
    "base_price": 200,
    "age_years": 0.5,
    "condition": "excellent",
    "damage_list": [],
    "completeness_pct": 95
  }
]
```

## Price Adjustment Examples

### Example 1: New Electronics

```bash
python3 backend/analysis_cli.py calculate \
  --base-price 800 \
  --age 0 \
  --condition new \
  --completeness 100 \
  --output json
```

Result: $800 (no adjustments)

### Example 2: Used Laptop

```bash
python3 backend/analysis_cli.py calculate \
  --base-price 1200 \
  --age 2 \
  --condition good \
  --damage minor_scratch:top:minor \
  --completeness 85 \
  --category electronics
```

Result: ~$450 (depreciation + condition + damage + completeness)

### Example 3: Vehicle with Damage

```bash
python3 backend/analysis_cli.py calculate \
  --base-price 25000 \
  --age 5 \
  --condition very_good \
  --damage aesthetic:passenger:minor \
  --damage dent:rear:moderate \
  --damage rust:bottom:minor \
  --completeness 100
```

Result: ~$8,900 (age depreciation + multiple damages)

### Example 4: Seasonal Item

```bash
# Winter coat in summer
python3 backend/analysis_cli.py calculate \
  --base-price 200 \
  --age 1 \
  --condition excellent \
  --category winter_gear \
  --completeness 100
```

Result: Lower price due to off-season (June-August: -20%)

## Integration with Main CLI

The analysis CLI can be integrated with the main ArbFinder CLI:

```bash
# Use main CLI to fetch items
arbfinder search "RTX 3060" --json items.json

# Process with analysis CLI
python3 backend/analysis_cli.py batch \
  --input items.json \
  --output analyzed.json \
  --operation price

# View results
cat analyzed.json | jq '.[] | {title: .item.title, final_price: .price_analysis.final_price}'
```

## Advanced Usage

### Custom Depreciation Rate

For items with faster depreciation:

```bash
python3 backend/analysis_cli.py depreciation \
  --base-price 500 \
  --age 1.5 \
  --model exponential \
  --half-life 1.0  # Loses 50% value every year
```

### Multiple Damages

Add multiple damage entries to account for cumulative impact:

```bash
python3 backend/analysis_cli.py calculate \
  --base-price 1000 \
  --damage aesthetic:front:minor \
  --damage aesthetic:rear:minor \
  --damage dent:passenger:moderate \
  --damage rust:bottom:minor
```

### Market Conditions

Adjust for supply and demand:

```bash
# High demand, low supply (price increases)
python3 backend/analysis_cli.py calculate \
  --base-price 500 \
  --supply 10 \
  --sales 50

# Low demand, high supply (price decreases)
python3 backend/analysis_cli.py calculate \
  --base-price 500 \
  --supply 100 \
  --sales 5
```

## Output Formats

### Table Output (Default)

Rich, formatted tables with color coding (requires `rich` library).

### JSON Output

Machine-readable format for integration:

```bash
python3 backend/analysis_cli.py calculate \
  --base-price 500 \
  --age 2 \
  --condition good \
  --output json > result.json
```

## Performance

- **Single calculation**: < 10ms
- **Batch processing**: ~500 items/second
- **Metadata generation**: ~100 items/second

## Troubleshooting

### Missing `rich` Library

If `rich` is not installed, the CLI falls back to plain text output:

```bash
pip install rich
```

### Invalid Damage Format

Ensure damage is specified as `type:location:severity`:

```bash
# ✗ Wrong
--damage "dent"

# ✓ Correct
--damage dent:passenger:moderate
```

### Large Batch Files

For very large batch files (>10,000 items), consider:
- Processing in chunks
- Using multiprocessing
- Saving intermediate results

## API Integration

The price calculation engine can be called from Python:

```python
from backend.analysis_cli import PriceAnalyzer
from decimal import Decimal

analyzer = PriceAnalyzer()

result = analyzer.calculate_comprehensive_price(
    base_price=Decimal('500'),
    age_years=Decimal('2'),
    condition='good',
    damage_list=[
        {'type': 'dent', 'location': 'passenger', 'severity': 'minor'}
    ],
    supply_count=30,
    recent_sales=15
)

print(f"Final price: ${result['final_price']:.2f}")
```

## See Also

- [Research Report](../docs/RESEARCH_REPORT.md) - Methodology details
- [Database Schema](../database/migrations/001_initial_schema.sql) - Data storage
- [Enterprise Roadmap](../docs/ENTERPRISE_ROADMAP.md) - Future features
