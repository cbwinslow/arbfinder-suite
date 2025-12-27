# 🎯 ArbFinder Suite - Prompt Templates

## Overview
Collection of reusable prompt templates for AI agents, LLMs, and various automation tasks in the ArbFinder Suite.

---

## Table of Contents
1. [Data Extraction Prompts](#data-extraction-prompts)
2. [Content Generation Prompts](#content-generation-prompts)
3. [Analysis Prompts](#analysis-prompts)
4. [Code Generation Prompts](#code-generation-prompts)
5. [Agent System Prompts](#agent-system-prompts)

---

## Data Extraction Prompts

### Extract Product Information
```
Extract structured product information from the following listing text:

{listing_text}

Return a JSON object with the following fields:
- brand: The brand name (string or null)
- model: The model number/name (string or null)
- condition: The item condition (string from: new, excellent, good, fair, poor, or null)
- color: The color (string or null)
- size: The size/dimensions (string or null)
- year: The year/model year (integer or null)
- specifications: Key specifications as key-value pairs (object)

Only include fields with high confidence. If a field is unclear, set it to null.
Return only valid JSON, no additional text.
```

### Parse Price Information
```
Parse price information from this text:

{price_text}

Extract:
- amount: The numerical price value (float)
- currency: Currency code (USD, EUR, GBP, etc.)
- original_price: If there's a strikethrough/original price (float or null)
- discount_percentage: If a discount is mentioned (float or null)

Return as JSON object.
```

### Identify Product Category
```
Categorize this product into the appropriate e-commerce category:

Title: {title}
Description: {description}

Return the most specific category path using this format:
Category > Subcategory > Sub-subcategory

Examples:
- Electronics > Computers > Laptops
- Clothing > Men's > Shirts > T-Shirts
- Home & Garden > Furniture > Living Room > Sofas

Return only the category path, nothing else.
```

---

## Content Generation Prompts

### Generate Product Title
```
Create an optimized product title for e-commerce listing:

Product Details:
- Brand: {brand}
- Model: {model}
- Condition: {condition}
- Key Features: {features}

Requirements:
- Maximum 80 characters
- Include brand and model prominently
- Highlight key feature or USP
- Clear condition statement
- SEO-friendly
- No promotional language (no "SALE", "DEAL", etc.)

Generate 3 title options ranked by effectiveness.
```

### Generate Product Description
```
Write a compelling product description for:

Title: {title}
Condition: {condition}
Specifications: {specs}
Target Audience: {audience}

Requirements:
- 150-300 words
- Professional tone
- Highlight key benefits
- Include specifications naturally
- Address common concerns
- SEO-optimized
- No false claims

Format with:
1. Opening hook (1-2 sentences)
2. Key features (bullet points)
3. Specifications
4. Closing statement
```

### Generate Bullet Points
```
Create 5 compelling bullet points for this product:

{product_info}

Each bullet should:
- Start with a benefit or feature
- Be concise (max 15 words)
- Use action words
- Focus on value to buyer
- Be accurate and honest

Format: • Bullet point text
```

### Generate Tags/Keywords
```
Generate SEO tags and keywords for:

Product: {product_name}
Category: {category}
Description: {description}

Generate:
- 10 primary keywords (most relevant)
- 5 long-tail keywords (3-4 word phrases)
- 5 related search terms

Focus on:
- Search volume
- Buyer intent
- Relevance
- Competition level

Return as JSON with arrays for each type.
```

---

## Analysis Prompts

### Analyze Market Value
```
Analyze the market value for this product:

Product: {product_name}
Current Listing Price: {price}
Comparable Prices: {comp_prices}
Condition: {condition}
Market Data: {market_data}

Provide:
1. Fair Market Value estimate
2. Price recommendation (aggressive/moderate/conservative)
3. Confidence level (0-100%)
4. Key factors influencing value
5. Market trend (increasing/stable/decreasing)

Return as structured JSON.
```

### Assess Arbitrage Opportunity
```
Evaluate this arbitrage opportunity:

Buy Price: {buy_price}
Sell Price Estimate: {sell_price}
Fees: {fees}%
Shipping: {shipping_cost}
Competition: {competition_level}
Demand: {demand_level}

Calculate:
1. Gross profit
2. Net profit (after fees and shipping)
3. ROI percentage
4. Risk assessment (low/medium/high)
5. Recommendation (strong buy/buy/maybe/pass)
6. Reasoning

Format as detailed analysis with numbers.
```

### Identify Similar Products
```
Find similar products to:

Product: {product_description}
Key Features: {features}
Price Range: {price_range}

Search for products that are:
- Same or similar category
- Comparable condition
- Similar features
- Within ±30% price range

Return top 5 matches with:
- Title
- Price
- Similarity score (0-100%)
- Key similarities
- Key differences
```

---

## Code Generation Prompts

### Generate API Endpoint
```
Create a FastAPI endpoint for:

Function: {function_description}
Method: {http_method}
Path: {url_path}
Request Body: {request_schema}
Response: {response_schema}

Requirements:
- Include type hints
- Add pydantic models
- Handle errors gracefully
- Add docstring
- Include example usage
- Follow project conventions

Generate complete, production-ready code.
```

### Generate Database Query
```
Create an efficient SQL query for:

Goal: {query_goal}
Tables: {table_names}
Filters: {filter_conditions}
Sorting: {sort_criteria}
Pagination: {pagination_params}

Requirements:
- Use proper indexes
- Optimize for performance
- Include JOINs if needed
- Add comments
- Follow SQL style guide
- Prevent SQL injection

Generate the query with explanation.
```

### Generate Test Cases
```
Generate pytest test cases for this function:

{function_code}

Create tests for:
1. Happy path (normal use case)
2. Edge cases (boundaries)
3. Error cases (invalid inputs)
4. Integration scenarios

Include:
- Setup/teardown if needed
- Mock external dependencies
- Clear assertions
- Descriptive test names
- Docstrings

Generate 5-7 comprehensive tests.
```

---

## Agent System Prompts

### Web Crawler Agent
```
You are a specialized Web Crawler Agent for e-commerce data extraction.

Your role:
- Extract product data from HTML/JavaScript-rendered pages
- Parse structured and unstructured content
- Handle various page layouts and formats
- Maintain data quality and consistency

Guidelines:
- Respect robots.txt and rate limits
- Extract only accurate, verifiable data
- Mark uncertain data with confidence scores
- Report errors and edge cases
- Preserve source attribution

Current task:
{task_description}

Target URL: {url}
Required fields: {fields}
Extraction rules: {rules}

Proceed with extraction.
```

### Data Validator Agent
```
You are a Data Validator Agent ensuring data quality.

Your role:
- Validate data against schema
- Check for consistency and accuracy
- Identify missing or incorrect values
- Flag anomalies and outliers
- Suggest corrections

Validation rules:
{validation_rules}

Data to validate:
{data}

Perform comprehensive validation and return:
1. Validation status (pass/fail)
2. List of errors/warnings
3. Suggested corrections
4. Data quality score (0-100)
```

### Metadata Enricher Agent
```
You are a Metadata Enricher Agent for data completion.

Your role:
- Fill in missing metadata fields
- Infer information from context
- Enhance data quality
- Add value without introducing errors

Current item:
{item_data}

Missing fields:
{missing_fields}

Enrichment sources:
- Item title and description
- Known patterns and rules
- Category-specific knowledge
- Historical data patterns

Enrich the data with high-confidence predictions.
Provide confidence scores for each enriched field.
```

### Price Specialist Agent
```
You are a Price Specialist Agent for pricing optimization.

Your role:
- Analyze market data
- Calculate optimal prices
- Assess profit potential
- Consider fees and costs
- Account for market conditions

Item details:
{item_details}

Cost basis: {cost}
Comparable prices: {comps}
Market conditions: {market}
Target margin: {margin}%

Calculate:
1. Recommended selling price
2. Expected profit
3. Price confidence level
4. Market positioning (aggressive/moderate/conservative)
5. Reasoning

Provide detailed pricing analysis.
```

### Listing Writer Agent
```
You are a Listing Writer Agent for content creation.

Your role:
- Write compelling product titles
- Create engaging descriptions
- Generate effective bullet points
- Optimize for SEO
- Maintain brand voice

Product information:
{product_info}

Target platform: {platform}
Target audience: {audience}
Tone: {tone}

Create:
1. Title (platform-specific length)
2. Description (150-300 words)
3. 5 bullet points
4. 10 SEO tags

Follow platform guidelines and best practices.
```

---

## Specialized Prompts

### Image Analysis
```
Analyze this product image and extract information:

Image URL: {image_url}

Identify:
- Product type
- Brand (if visible)
- Condition indicators (scratches, wear, etc.)
- Color
- Notable features
- Image quality score
- Suitability for listing (yes/no)

Return structured analysis with confidence scores.
```

### Competitive Analysis
```
Perform competitive analysis for:

Our Product: {our_product}
Our Price: {our_price}

Competitors:
{competitor_list}

Analyze:
1. Price positioning
2. Feature comparison
3. Unique selling points
4. Competitive advantages
5. Potential weaknesses
6. Market gap opportunities

Provide strategic recommendations.
```

### Trend Detection
```
Analyze pricing trends for this category:

Category: {category}
Time period: {period}
Historical data: {historical_data}

Detect:
1. Overall trend (up/down/stable)
2. Seasonal patterns
3. Price volatility
4. Anomalies
5. Future predictions

Provide trend analysis with confidence intervals.
```

---

## Utility Prompts

### Summarize Long Text
```
Summarize the following text concisely:

{long_text}

Create:
1. One-line summary (max 100 chars)
2. Short summary (2-3 sentences)
3. Key points (bullet list)
4. Main takeaway

Focus on most important information.
```

### Extract Entities
```
Extract named entities from this text:

{text}

Find:
- Brands
- Models
- Locations
- Organizations
- Dates
- Prices
- People

Return as structured JSON with entity type and confidence.
```

### Classify Sentiment
```
Classify the sentiment of this review/description:

{text}

Return:
- Overall sentiment (positive/neutral/negative)
- Sentiment score (-1 to +1)
- Key sentiment phrases
- Confidence level

Be objective and accurate.
```

---

## Debugging Prompts

### Explain Error
```
Explain this error in simple terms:

Error: {error_message}
Stack trace: {stack_trace}
Context: {context}

Provide:
1. What went wrong
2. Why it happened
3. How to fix it
4. How to prevent it

Use clear, non-technical language.
```

### Suggest Improvements
```
Review this code and suggest improvements:

{code}

Focus on:
- Performance
- Readability
- Security
- Best practices
- Error handling

Provide specific, actionable suggestions with examples.
```

---

## Prompt Best Practices

### Structure
1. **Clear Role**: Define who/what the AI is
2. **Context**: Provide necessary background
3. **Task**: Specific instruction
4. **Constraints**: Limitations and requirements
5. **Format**: Expected output format
6. **Examples**: Show desired output

### Tips
- Be specific and concrete
- Use examples when possible
- Set clear expectations
- Define output format
- Include edge cases
- Specify tone and style
- Add confidence requirements
- Request reasoning when needed

### Variables
Use `{variable_name}` for dynamic content:
- `{product_name}` - Product name
- `{description}` - Product description
- `{price}` - Price value
- `{category}` - Category name
- `{condition}` - Item condition
- `{data}` - Generic data field

---

## Prompt Testing

### Testing Checklist
- [ ] Clear and unambiguous instructions
- [ ] Appropriate level of detail
- [ ] Handles edge cases
- [ ] Consistent output format
- [ ] Reasonable token usage
- [ ] Produces expected results
- [ ] Scalable to variations

### Iteration Process
1. **Draft**: Create initial prompt
2. **Test**: Try with sample data
3. **Analyze**: Review outputs
4. **Refine**: Adjust wording/structure
5. **Validate**: Test multiple scenarios
6. **Document**: Add to collection

---

## Prompt Variables Reference

### Common Variables
```json
{
  "product_name": "string",
  "brand": "string",
  "model": "string",
  "condition": "new|excellent|good|fair|poor",
  "price": "float",
  "currency": "string",
  "description": "string",
  "category": "string",
  "features": "array",
  "specifications": "object",
  "images": "array",
  "url": "string",
  "source": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

**Version**: 1.0  
**Last Updated**: 2024-12-15  
**Maintained By**: AI Team

**Note**: These prompts are templates. Replace variables with actual data before use. Test and refine prompts for your specific use case.
