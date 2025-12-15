# AI Prompts Library

This document contains a comprehensive library of AI prompts used throughout ArbFinder Suite for various tasks.

---

## Table of Contents

1. [Data Extraction Prompts](#data-extraction-prompts)
2. [Metadata Enrichment Prompts](#metadata-enrichment-prompts)
3. [Listing Creation Prompts](#listing-creation-prompts)
4. [Price Analysis Prompts](#price-analysis-prompts)
5. [Quality Control Prompts](#quality-control-prompts)
6. [Customer Service Prompts](#customer-service-prompts)
7. [Code Generation Prompts](#code-generation-prompts)

---

## Data Extraction Prompts

### Extract Product Information

```markdown
**Task:** Extract structured product information from the following text.

**Text:**
{raw_text}

**Required Fields:**
- Title (product name)
- Price (numeric value only)
- Condition (new, used, refurbished, etc.)
- Category (electronics, clothing, etc.)
- Brand (if mentioned)
- Model (if mentioned)

**Output Format:** JSON

**Example:**
```json
{
  "title": "Apple iPhone 12 Pro",
  "price": 799.99,
  "condition": "used",
  "category": "Electronics > Mobile Phones",
  "brand": "Apple",
  "model": "iPhone 12 Pro"
}
```

**Important:**
- Extract only factual information present in the text
- Use null for missing fields
- Normalize prices to USD
- Standardize condition values
```

### Parse Listing Description

```markdown
**Task:** Parse a product listing and extract key details.

**Listing:**
{listing_html}

**Extract:**
1. **Seller Information**
   - Seller name
   - Seller rating
   - Location

2. **Product Details**
   - Specifications
   - Features
   - Included items
   - Excluded items

3. **Condition Details**
   - Overall condition
   - Specific issues
   - Cosmetic damage
   - Functional issues

4. **Shipping Information**
   - Shipping cost
   - Shipping methods
   - Estimated delivery

**Format:** Structured JSON with clear sections
```

---

## Metadata Enrichment Prompts

### Category Classification

```markdown
**Task:** Classify this item into the most specific category.

**Item:**
Title: {title}
Description: {description}

**Category Hierarchy:**
Electronics > Computers > Laptops
Electronics > Computers > Desktops
Electronics > Computers > Tablets
Electronics > Audio > Headphones
Electronics > Audio > Speakers
Electronics > TV & Video > Televisions
Clothing > Men's > Shirts
Clothing > Women's > Dresses
...

**Instructions:**
1. Choose the most specific category that fits
2. If uncertain, provide the 3 most likely categories with confidence scores
3. Explain your reasoning

**Output Format:**
```json
{
  "primary_category": "Electronics > Computers > Laptops",
  "confidence": 0.95,
  "alternatives": [
    {"category": "Electronics > Computers > Tablets", "confidence": 0.3},
    {"category": "Electronics > Computers > Desktops", "confidence": 0.1}
  ],
  "reasoning": "Description mentions 'laptop', 'portable', and 'battery'"
}
```
```

### Extract Specifications

```markdown
**Task:** Extract technical specifications from the product description.

**Product:**
{title}

**Description:**
{description}

**Common Specification Types:**
- Processor/CPU
- Memory/RAM
- Storage
- Display size and resolution
- Battery life
- Connectivity (WiFi, Bluetooth, etc.)
- Operating system
- Dimensions
- Weight
- Color
- Material

**Instructions:**
1. Extract all specifications mentioned
2. Normalize units (e.g., "16 GB" not "16gb" or "16 gigabytes")
3. Separate specification name and value
4. Include only technical specs, not marketing language

**Output Format:**
```json
{
  "specifications": {
    "processor": "Intel Core i7-10750H",
    "ram": "16 GB",
    "storage": "512 GB SSD",
    "display": "15.6 inch FHD (1920x1080)",
    "graphics": "NVIDIA GTX 1660 Ti",
    "weight": "2.3 kg"
  }
}
```
```

### Brand and Model Identification

```markdown
**Task:** Identify the brand and exact model from this product listing.

**Title:** {title}
**Description:** {description}

**Guidelines:**
1. Extract the official brand name (not seller name)
2. Identify the complete model number/name
3. Distinguish between series and specific model
4. Note any variations (color, storage size, etc.)

**Output Format:**
```json
{
  "brand": "Apple",
  "model": "iPhone 12 Pro",
  "series": "iPhone 12",
  "variant": "256GB Space Gray",
  "model_number": "A2341",
  "confidence": 0.98
}
```

**Common Brands by Category:**
- Electronics: Apple, Samsung, Sony, LG, Dell, HP, Lenovo
- Audio: Bose, Sony, Beats, Sennheiser, Audio-Technica
- Gaming: PlayStation, Xbox, Nintendo, Razer, ASUS
```

---

## Listing Creation Prompts

### Generate Product Title

```markdown
**Task:** Create an SEO-optimized product title for this item.

**Product Information:**
{product_data}

**Platform:** {platform} (eBay, Mercari, Reverb, etc.)

**Requirements:**
1. Character limit: 80 characters
2. Include brand and model
3. Include key features (if space allows)
4. Include condition
5. Use title case
6. No promotional language
7. Use relevant keywords for searchability

**Bad Examples:**
- "GREAT DEAL! MUST SEE! Laptop!!!"
- "laptop for sale"
- "Apple"

**Good Examples:**
- "Apple MacBook Pro 15 inch 2019 - i7, 16GB RAM, 512GB SSD - Excellent"
- "Sony WH-1000XM4 Wireless Noise Cancelling Headphones - Black - New"
- "Nintendo Switch Console OLED Model White with Accessories - Like New"

**Generate 3 title options ranked by effectiveness.**
```

### Generate Product Description

```markdown
**Task:** Write a compelling product description.

**Product:**
{product_data}

**Platform:** {platform}

**Description Structure:**
1. **Opening Hook** (1-2 sentences)
   - Highlight main benefit or unique feature
   - Create interest

2. **Product Details** (1 paragraph)
   - Key specifications
   - Main features
   - Use cases

3. **Condition Description** (1 paragraph)
   - Overall condition
   - Any flaws or damage (be honest)
   - What's included
   - What's NOT included

4. **Shipping & Returns** (1 paragraph)
   - Shipping method and timing
   - Packaging details
   - Return policy

**Tone:**
- Professional but friendly
- Honest and transparent
- Enthusiastic but not salesy
- Clear and concise

**Length:** 200-400 words

**Format:** Use bullet points where appropriate for readability

**SEO Keywords to Include:** {keywords}
```

### Create Bullet Points

```markdown
**Task:** Create 5-7 bullet points highlighting key features and benefits.

**Product:** {product_data}

**Guidelines:**
1. Start each bullet with a benefit or feature
2. Keep each bullet to 1-2 lines
3. Use action words
4. Be specific (numbers, measurements, etc.)
5. Priority order (most important first)

**Examples:**

For Electronics:
• Ultra-Fast Performance: Intel i7 processor with 16GB RAM for seamless multitasking
• Crystal Clear Display: 15.6" Full HD (1920x1080) anti-glare screen
• All-Day Battery: Up to 10 hours of battery life on a single charge
• Lightweight & Portable: Only 4.2 lbs, perfect for travel and commuting
• Excellent Condition: Minimal wear, professionally tested and cleaned

For Audio:
• Industry-Leading Noise Cancellation: Block out distractions completely
• 30-Hour Battery Life: Keep listening for days without recharging
• Premium Sound Quality: Rich bass and crystal-clear highs
• Comfortable Design: Plush ear cushions for all-day wear
• Multi-Device Connectivity: Seamlessly switch between phone and laptop
```

---

## Price Analysis Prompts

### Market Analysis

```markdown
**Task:** Analyze the market for this item and provide pricing recommendations.

**Item:** {title}
**Category:** {category}
**Condition:** {condition}

**Comparable Sales:**
{comp_data}

**Analysis Required:**
1. **Market Overview**
   - Current supply/demand
   - Price trends (increasing, stable, declining)
   - Seasonal factors

2. **Price Recommendation**
   - Suggested listing price
   - Minimum acceptable price
   - Best offer threshold
   - Reasoning for recommendations

3. **Competitive Analysis**
   - How does this compare to similar items?
   - What makes this item more/less valuable?
   - Unique selling points

4. **Risk Assessment**
   - Time to sell estimate
   - Price volatility
   - Market saturation

**Output Format:**
```json
{
  "market_overview": {
    "demand": "high",
    "trend": "stable",
    "seasonality": "none"
  },
  "pricing": {
    "recommended_list": 299.99,
    "minimum_acceptable": 250.00,
    "best_offer_threshold": 275.00,
    "confidence": 0.87
  },
  "competitive_position": "above average",
  "estimated_days_to_sell": 7,
  "reasoning": "Based on 47 comparable sales..."
}
```
```

### Fee Calculation

```markdown
**Task:** Calculate total fees and net profit for this listing.

**Item Price:** {price}
**Platform:** {platform}
**Shipping Cost:** {shipping}
**Purchase Cost:** {cost}

**Fee Structure for {platform}:**
{fee_structure}

**Calculate:**
1. Platform fees (insertion, final value, etc.)
2. Payment processing fees
3. Shipping cost (if not passed to buyer)
4. Total costs
5. Net profit
6. Profit margin %
7. ROI %

**Output Format:**
```json
{
  "selling_price": 299.99,
  "costs": {
    "purchase_cost": 200.00,
    "platform_fees": 38.90,
    "payment_processing": 9.00,
    "shipping": 10.00,
    "total_costs": 257.90
  },
  "profit": {
    "gross_profit": 99.99,
    "net_profit": 42.09,
    "profit_margin": 14.03,
    "roi": 21.05
  }
}
```
```

---

## Quality Control Prompts

### Data Validation

```markdown
**Task:** Validate this product listing data for completeness and quality.

**Listing Data:**
{listing_data}

**Validation Checklist:**
1. **Required Fields**
   - [ ] Title present and adequate length (10-200 chars)
   - [ ] Price is valid number > 0
   - [ ] Category assigned
   - [ ] Condition specified
   - [ ] At least one image
   - [ ] Description present (min 50 words)

2. **Quality Checks**
   - [ ] Title is descriptive and searchable
   - [ ] Price is realistic (not obviously wrong)
   - [ ] Category is appropriate
   - [ ] Condition matches description
   - [ ] Images are clear and relevant
   - [ ] No prohibited content

3. **Data Consistency**
   - [ ] Title matches description
   - [ ] Specifications are consistent
   - [ ] Price matches condition
   - [ ] Currency is specified

**Report Issues:**
- Severity: critical, high, medium, low
- Field affected
- Issue description
- Suggested fix

**Output Format:**
```json
{
  "valid": false,
  "quality_score": 7.5,
  "issues": [
    {
      "severity": "high",
      "field": "title",
      "issue": "Title too short (8 characters)",
      "suggestion": "Add brand, model, and key feature"
    }
  ]
}
```
```

### Anomaly Detection

```markdown
**Task:** Analyze this listing for anomalies or suspicious patterns.

**Listing:** {listing_data}
**Context:** {market_data}

**Check For:**
1. **Price Anomalies**
   - Significantly higher/lower than market average
   - Price doesn't match condition
   - Suspiciously round numbers
   - Currency issues

2. **Content Anomalies**
   - Duplicate content from other listings
   - Inconsistencies in description
   - Missing common information
   - Generic or template language

3. **Pattern Anomalies**
   - Same seller, many similar items
   - Rapid price changes
   - Multiple identical listings
   - Bot-like behavior

**Risk Assessment:**
- Low: Minor issues, likely legitimate
- Medium: Notable issues, needs review
- High: Serious concerns, flag for manual review

**Output:**
```json
{
  "anomaly_detected": true,
  "risk_level": "medium",
  "anomalies": [
    {
      "type": "price",
      "description": "Price 40% below market average",
      "confidence": 0.85
    }
  ],
  "recommendation": "manual_review",
  "reasoning": "..."
}
```
```

---

## Customer Service Prompts

### Generate Response Template

```markdown
**Task:** Create a professional response to this customer inquiry.

**Customer Message:**
{customer_message}

**Context:**
- Product: {product_title}
- Order Status: {status}
- Customer History: {customer_info}

**Tone Guidelines:**
- Friendly and professional
- Empathetic to customer concerns
- Clear and concise
- Proactive (offer solutions)
- Brand voice: {brand_voice}

**Response Template:**

**Greeting:** Personalized greeting
**Acknowledgment:** Show you understand their concern
**Response:** Address their question/issue
**Solution:** Provide clear next steps
**Closing:** Friendly closing with offer to help further

**Include:**
- Relevant order/tracking information
- Timeline expectations
- Contact information if needed
```

---

## Code Generation Prompts

### Generate API Client

```markdown
**Task:** Generate a Python API client for the following API endpoint.

**Endpoint:** {endpoint_url}
**Method:** {http_method}
**Authentication:** {auth_type}

**Requirements:**
1. Type hints for all functions
2. Error handling with retries
3. Request/response logging
4. Async support
5. Comprehensive docstrings
6. Example usage

**Generate:**
- Client class
- Request/response models (Pydantic)
- Error classes
- Usage examples
- Unit tests
```

### Generate Database Migration

```markdown
**Task:** Generate a database migration for the following schema change.

**Current Schema:**
{current_schema}

**Desired Change:**
{change_description}

**Requirements:**
1. Both up and down migrations
2. Data preservation (if applicable)
3. Index creation
4. Constraint handling
5. Performance considerations

**Generate:**
- SQL migration file
- Rollback procedure
- Verification queries
```

---

## Prompt Templates

### General Template Structure

```markdown
**Context:** {provide relevant background}

**Task:** {clear, specific task description}

**Input:**
{structured input data}

**Requirements:**
{list specific requirements}

**Output Format:**
{specify desired format}

**Examples:**
{provide 1-3 examples}

**Constraints:**
{any limitations or rules}
```

---

## Best Practices

### Writing Effective Prompts

1. **Be Specific**
   - Clearly define the task
   - Specify output format
   - Provide examples

2. **Provide Context**
   - Background information
   - Related data
   - Use case

3. **Set Constraints**
   - Length limits
   - Format requirements
   - Quality standards

4. **Include Examples**
   - Good examples
   - Bad examples (what to avoid)
   - Edge cases

5. **Iterate and Refine**
   - Test prompts
   - Analyze outputs
   - Adjust as needed

### Common Pitfalls to Avoid

- ❌ Vague instructions
- ❌ No examples
- ❌ Unclear output format
- ❌ Too many tasks in one prompt
- ❌ No constraints or guidelines

---

Last Updated: 2024-12-15  
Version: 1.0
