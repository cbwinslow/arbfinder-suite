# ArbFinder Suite - AI Prompts Library

**Version**: 2.0  
**Last Updated**: 2025-12-15  
**Purpose**: Reusable prompts for AI agents and LLM operations  

---

## Table of Contents

1. [Content Generation Prompts](#content-generation-prompts)
2. [Data Extraction Prompts](#data-extraction-prompts)
3. [Analysis Prompts](#analysis-prompts)
4. [Code Generation Prompts](#code-generation-prompts)
5. [Agent System Prompts](#agent-system-prompts)
6. [Quality Assurance Prompts](#quality-assurance-prompts)
7. [Optimization Prompts](#optimization-prompts)

---

## Content Generation Prompts

### 1. Product Title Generation

**Purpose**: Generate SEO-optimized product titles

```
Generate an SEO-optimized product title for the following item:

Raw Title: {original_title}
Category: {category}
Brand: {brand}
Condition: {condition}
Key Features: {features}

Requirements:
- Maximum 80 characters
- Include brand name at the start
- Include specific model/version
- Include key specifications
- Mention condition if not new
- Use power words (Excellent, Fast, Premium, etc.)
- Avoid special characters except hyphens and spaces
- Format for {platform} (eBay/Mercari/Poshmark)

Output only the optimized title, no explanation.

Example:
Input: "used ipad works good"
Output: "Apple iPad Pro 11" 2021 128GB WiFi Excellent Condition + Accessories"
```

**Variables**:
- `{original_title}`: Raw title from source
- `{category}`: Product category
- `{brand}`: Brand name
- `{condition}`: Item condition
- `{features}`: List of key features
- `{platform}`: Target marketplace

---

### 2. Product Description Generation

**Purpose**: Create compelling product descriptions

```
Write a compelling product description for an online marketplace listing.

Product Details:
- Title: {title}
- Brand: {brand}
- Category: {category}
- Condition: {condition}
- Features: {features}
- Price: {price}

Requirements:
- Professional but friendly tone
- 3-5 short paragraphs
- Start with key selling points
- Include detailed condition notes
- Mention what's included
- Add shipping and return info
- Use bullet points for specifications
- Optimize for search keywords: {keywords}
- Target audience: {target_audience}

Structure:
1. Opening paragraph highlighting main benefits
2. Detailed product specifications
3. Condition and quality notes
4. What's included in the package
5. Shipping and returns policy

Output the description only, no meta-commentary.
```

**Variables**:
- `{title}`: Product title
- `{brand}`: Brand name
- `{category}`: Product category
- `{condition}`: Item condition
- `{features}`: Key features list
- `{price}`: Listing price
- `{keywords}`: SEO keywords
- `{target_audience}`: Target buyer persona

---

### 3. Feature Bullet Points

**Purpose**: Extract and format key features

```
Extract and format the key features as concise bullet points.

Product Information:
{product_text}

Requirements:
- 5-10 bullet points
- Each bullet point 5-15 words
- Start with the most important features
- Include specific measurements/specs
- Use action-oriented language
- Format: "✓ Feature description"
- Focus on benefits, not just specifications
- Avoid redundancy

Output format:
✓ Feature 1
✓ Feature 2
✓ Feature 3
...

Example:
✓ Apple M1 chip for lightning-fast performance
✓ 11-inch Liquid Retina display with ProMotion
✓ 128GB storage for apps, photos, and videos
✓ All-day battery life up to 10 hours
✓ Face ID for secure authentication
```

**Variables**:
- `{product_text}`: Full product information text

---

## Data Extraction Prompts

### 4. Price Extraction

**Purpose**: Extract price information from text

```
Extract the price information from the following text.

Text: {text}

Extract and return a JSON object with:
- price: numeric value (float)
- currency: currency code (USD, EUR, etc.)
- original_text: the exact price text found
- confidence: confidence score 0-1

Handle these formats:
- "$299.99"
- "299.99 USD"
- "Price: $299"
- "299 dollars"
- "€250"
- "£199.99"

If multiple prices found, return the main/listing price.
If no price found, return null for price and 0.0 for confidence.

Output only valid JSON, no explanation.

Example output:
{
  "price": 299.99,
  "currency": "USD",
  "original_text": "$299.99",
  "confidence": 0.95
}
```

**Variables**:
- `{text}`: Text containing price information

---

### 5. Metadata Extraction

**Purpose**: Extract structured metadata from unstructured text

```
Extract structured metadata from this product listing.

Listing Text:
{listing_text}

Extract the following fields (return null if not found):
- brand: Brand name
- model: Model number/name
- year: Year of manufacture/release
- condition: Condition (New, Like New, Excellent, Good, Fair, Poor)
- category: Product category
- color: Color/finish
- size: Size/dimensions
- material: Material composition
- features: List of key features
- defects: Any mentioned defects or issues

Return as JSON with confidence scores for each field.

Example output:
{
  "brand": {"value": "Apple", "confidence": 0.99},
  "model": {"value": "iPad Pro 11-inch", "confidence": 0.95},
  "year": {"value": 2021, "confidence": 0.90},
  "condition": {"value": "Excellent", "confidence": 0.85},
  "color": {"value": "Space Gray", "confidence": 0.80}
}
```

**Variables**:
- `{listing_text}`: Product listing text

---

### 6. Category Classification

**Purpose**: Classify products into categories

```
Classify this product into the most appropriate category.

Product: {title}
Description: {description}

Available Categories (with subcategories):
- Electronics > Computers > Laptops
- Electronics > Computers > Tablets
- Electronics > Computers > Desktops
- Electronics > Audio > Headphones
- Electronics > Audio > Speakers
- Electronics > Phones > Smartphones
- Electronics > Cameras > DSLR
- Electronics > Cameras > Mirrorless
- Collectibles > Toys > Action Figures
- Collectibles > Trading Cards > Sports
- Collectibles > Trading Cards > Gaming
- Fashion > Clothing > Shoes
- Fashion > Accessories > Watches
- Home & Garden > Furniture > Chairs
- Home & Garden > Kitchen > Appliances
- Sports > Equipment > Fitness
- Sports > Outdoor > Camping

Return:
1. Primary category path (e.g., "Electronics > Computers > Tablets")
2. Confidence score (0-1)
3. Alternative categories if confidence < 0.9

Output as JSON only.

Example:
{
  "category": "Electronics > Computers > Tablets",
  "confidence": 0.95,
  "alternatives": []
}
```

**Variables**:
- `{title}`: Product title
- `{description}`: Product description

---

## Analysis Prompts

### 7. Market Trend Analysis

**Purpose**: Analyze market trends from price data

```
Analyze the market trend for this product based on historical sales data.

Product: {product_name}
Recent Sales (last 90 days):
{sales_data}

Format: [{"date": "YYYY-MM-DD", "price": 299.99, "condition": "Good"}, ...]

Provide analysis including:
1. Overall trend (Increasing, Decreasing, Stable)
2. Average price by condition
3. Price volatility (High, Medium, Low)
4. Seasonal patterns (if detectable)
5. Market saturation (Oversupplied, Balanced, High Demand)
6. Recommended list price with reasoning
7. Confidence level in recommendations

Output as structured JSON with clear explanations.

Example output:
{
  "trend": "Stable",
  "avg_prices": {
    "Excellent": 450.00,
    "Good": 380.00,
    "Fair": 300.00
  },
  "volatility": "Low",
  "seasonal": "No clear pattern detected",
  "saturation": "Balanced",
  "recommended_price": 425.00,
  "reasoning": "Price has been stable around $400-450 for excellent condition...",
  "confidence": 0.85
}
```

**Variables**:
- `{product_name}`: Product name
- `{sales_data}`: JSON array of historical sales

---

### 8. Profit Opportunity Assessment

**Purpose**: Assess profit potential of a listing

```
Assess the profit opportunity for this listing.

Listing Details:
- Current Price: ${current_price}
- Comparable Sales Average: ${comp_average}
- Comparable Sales Median: ${comp_median}
- Condition: {condition}
- Category: {category}

Fee Structure:
- Marketplace Fee: {marketplace_fee}%
- Payment Processing: 2.9% + $0.30
- Shipping Cost Estimate: ${shipping_cost}

Calculate and provide:
1. Potential resale price (realistic estimate)
2. Total costs (acquisition + fees + shipping)
3. Gross profit
4. Net profit margin %
5. Risk assessment (Low, Medium, High)
6. Recommendation (Strong Buy, Buy, Maybe, Pass)
7. Key factors in decision
8. Suggested actions

Output as JSON with detailed breakdown.
```

**Variables**:
- `{current_price}`: Current listing price
- `{comp_average}`: Average comparable price
- `{comp_median}`: Median comparable price
- `{condition}`: Item condition
- `{category}`: Product category
- `{marketplace_fee}`: Marketplace fee percentage
- `{shipping_cost}`: Estimated shipping cost

---

### 9. Condition Assessment from Description

**Purpose**: Assess item condition from textual description

```
Assess the item condition based on this description and assign a standardized condition grade.

Description:
{description}

Image Analysis (if available):
{image_analysis}

Standardized Condition Grades:
- New: Brand new, unopened, with all original packaging
- Like New: Opened but unused, perfect condition, may lack original box
- Excellent: Minimal signs of use, no visible flaws, fully functional
- Good: Light wear from normal use, minor cosmetic issues, fully functional
- Fair: Moderate wear, visible cosmetic damage, fully functional
- Poor: Heavy wear, significant damage, may have functionality issues
- For Parts: Not working or severely damaged

Output JSON with:
- condition: Assigned condition grade
- confidence: Confidence score (0-1)
- positive_factors: List of positive condition indicators
- negative_factors: List of issues or concerns
- recommendation: Whether description accurately reflects stated condition
- notes: Additional observations

Example output:
{
  "condition": "Excellent",
  "confidence": 0.88,
  "positive_factors": [
    "Described as minimal signs of use",
    "Screen stated as pristine",
    "All functions working perfectly"
  ],
  "negative_factors": [
    "Minor scuff on back mentioned",
    "Battery health not specified"
  ],
  "recommendation": "Condition matches 'Excellent' grade",
  "notes": "Request battery health info for complete assessment"
}
```

**Variables**:
- `{description}`: Item description text
- `{image_analysis}`: Optional image analysis results

---

## Code Generation Prompts

### 10. API Client Code Generation

**Purpose**: Generate API client code

```
Generate a Python async API client for the following endpoint.

API Specification:
- Base URL: {base_url}
- Endpoint: {endpoint}
- Method: {method}
- Authentication: {auth_type}
- Request Parameters: {parameters}
- Response Format: {response_format}

Requirements:
- Use httpx for async HTTP
- Include type hints
- Add error handling
- Implement retry logic (3 attempts)
- Add request timeout (30s)
- Include docstrings
- Follow PEP 8 style

Generate complete, production-ready code.
```

**Variables**:
- `{base_url}`: API base URL
- `{endpoint}`: Specific endpoint path
- `{method}`: HTTP method
- `{auth_type}`: Authentication type
- `{parameters}`: Request parameters
- `{response_format}`: Expected response format

---

### 11. Test Case Generation

**Purpose**: Generate pytest test cases

```
Generate comprehensive pytest test cases for this function.

Function:
```python
{function_code}
```

Generate tests for:
- Happy path with valid inputs
- Edge cases (empty, null, boundary values)
- Invalid input handling
- Error conditions
- Async behavior (if applicable)
- Mock external dependencies

Follow pytest conventions:
- Use fixtures for setup
- Use parametrize for multiple inputs
- Use appropriate assertions
- Add descriptive test names
- Include docstrings

Generate 5-10 test cases covering all scenarios.
```

**Variables**:
- `{function_code}`: Function to test

---

## Agent System Prompts

### 12. Market Researcher Agent

**Purpose**: System prompt for market research agent

```
You are a Market Researcher Agent specializing in e-commerce price analysis.

Role:
Analyze market data to provide accurate pricing recommendations for resale opportunities.

Responsibilities:
1. Collect comparable sales data from eBay sold listings
2. Calculate statistical metrics (average, median, percentiles)
3. Analyze price trends over time
4. Identify seasonal patterns
5. Assess market saturation
6. Provide confidence-scored recommendations

Tools Available:
- ebay_search_tool: Search eBay sold listings
- statistics_calculator: Calculate price statistics
- trend_analyzer: Analyze time-series data
- comparable_cache: Cache for reducing API calls

Guidelines:
- Use at least 30 comparable sales for reliable analysis
- Weight recent sales more heavily (last 30 days)
- Adjust for condition differences
- Consider shipping costs in analysis
- Flag outliers (>2 standard deviations)
- Provide confidence scores with all recommendations
- Cite data sources in analysis

Response Format:
Always return structured JSON with:
- comparable_count: Number of data points
- avg_price: Average sold price
- median_price: Median sold price
- trend: Price trend assessment
- confidence: Confidence score (0-1)
- recommendation: Pricing recommendation
- reasoning: Explanation of analysis

Be thorough but concise. Prioritize accuracy over speed.
```

---

### 13. Listing Writer Agent

**Purpose**: System prompt for content generation agent

```
You are a Listing Specialist Agent expert in e-commerce copywriting.

Role:
Create compelling, SEO-optimized product listings that convert browsers to buyers.

Responsibilities:
1. Generate attention-grabbing titles
2. Write persuasive product descriptions
3. Extract and highlight key features
4. Include accurate condition notes
5. Optimize for marketplace search algorithms
6. Adapt content for different platforms

Guidelines:
- Use active voice and action verbs
- Lead with benefits, not just features
- Include specific measurements and specs
- Be honest about condition and defects
- Use proper grammar and punctuation
- Optimize for relevant keywords
- Match platform character limits
- Create urgency without being pushy

Platform-Specific Rules:
eBay:
- Title: 80 characters max
- Emphasize free shipping if applicable
- Include item specifics

Mercari:
- Title: 40 characters max
- Casual, friendly tone
- Mobile-first formatting

Poshmark:
- Focus on fashion/lifestyle aspects
- Use hashtags effectively
- Emphasize brand authenticity

Always maintain professional standards while adapting to platform culture.
```

---

### 14. Data Validator Agent

**Purpose**: System prompt for data validation agent

```
You are a Data Validation Agent responsible for ensuring data quality.

Role:
Validate and clean incoming data to maintain high data quality standards.

Responsibilities:
1. Check data completeness (all required fields present)
2. Validate data types and formats
3. Normalize data (standardize formats)
4. Detect and flag duplicates
5. Identify anomalies and outliers
6. Clean and standardize text fields

Validation Rules:
- Title: 10-200 characters, no special chars
- Price: Numeric, positive, reasonable range ($0.01-$1M)
- URL: Valid HTTP/HTTPS format, accessible
- Condition: Must match standard conditions
- Images: Valid URLs, accessible, appropriate format
- Date: Valid timestamp, not in future

Quality Scores:
- Complete: All required fields present (30%)
- Accurate: Data passes validation rules (40%)
- Consistent: Matches expected patterns (20%)
- Unique: Not a duplicate (10%)

Actions:
- Accept: Quality score >= 85%
- Clean and Accept: Quality score 70-84%
- Flag for Review: Quality score 50-69%
- Reject: Quality score < 50%

Always log validation results with:
- validation_status: accept/flag/reject
- quality_score: 0-100
- issues: List of problems found
- cleaned_data: Normalized version

Be strict but fair. When in doubt, flag for human review.
```

---

## Quality Assurance Prompts

### 15. Code Review Prompt

**Purpose**: Review code for quality and issues

```
Perform a comprehensive code review of the following code.

Code:
```python
{code}
```

Review Criteria:
1. Code Style: PEP 8 compliance, naming conventions
2. Functionality: Logic correctness, edge case handling
3. Performance: Efficiency, unnecessary operations
4. Security: Input validation, SQL injection, secrets
5. Error Handling: Appropriate exception handling
6. Testing: Testability, test coverage potential
7. Documentation: Docstrings, comments, clarity
8. Maintainability: Readability, modularity

Provide:
- Overall assessment (Excellent/Good/Needs Work/Poor)
- Specific issues found with severity (Critical/High/Medium/Low)
- Suggested improvements with code examples
- Positive aspects worth highlighting

Format as structured report with actionable feedback.
```

**Variables**:
- `{code}`: Code to review

---

### 16. Security Audit Prompt

**Purpose**: Audit code for security vulnerabilities

```
Perform a security audit of this code, checking for OWASP Top 10 vulnerabilities.

Code:
{code}

Check for:
1. Injection flaws (SQL, NoSQL, OS command)
2. Broken authentication
3. Sensitive data exposure
4. XML external entities (XXE)
5. Broken access control
6. Security misconfiguration
7. Cross-site scripting (XSS)
8. Insecure deserialization
9. Using components with known vulnerabilities
10. Insufficient logging and monitoring

For each finding, provide:
- Vulnerability type
- Severity (Critical/High/Medium/Low)
- Location in code
- Exploitation scenario
- Remediation steps with code example

If no issues found, confirm clean audit status.
```

**Variables**:
- `{code}`: Code to audit

---

## Optimization Prompts

### 17. Performance Optimization

**Purpose**: Suggest performance improvements

```
Analyze this code for performance bottlenecks and suggest optimizations.

Code:
{code}

Current Performance:
- Execution time: {execution_time}
- Memory usage: {memory_usage}
- Database queries: {query_count}
- API calls: {api_call_count}

Look for:
1. Inefficient loops or iterations
2. Redundant database queries (N+1 problem)
3. Missing caching opportunities
4. Unnecessary data loading
5. Synchronous operations that could be async
6. Memory leaks or excessive memory use
7. Missing indexes for database queries
8. Inefficient algorithms (wrong complexity class)

Provide:
- Identified bottlenecks
- Optimization suggestions with code examples
- Expected performance improvement
- Trade-offs or risks of suggested changes
- Priority ranking of optimizations

Target: 50% reduction in execution time, 30% reduction in memory.
```

**Variables**:
- `{code}`: Code to optimize
- `{execution_time}`: Current execution time
- `{memory_usage}`: Current memory usage
- `{query_count}`: Number of database queries
- `{api_call_count}`: Number of external API calls

---

### 18. Cost Optimization for AI Operations

**Purpose**: Optimize AI/LLM usage costs

```
Analyze this AI/LLM operation and suggest cost optimizations.

Current Setup:
- Model: {model}
- Average tokens per request: {avg_tokens}
- Requests per day: {requests_per_day}
- Current cost per request: ${cost_per_request}
- Monthly cost: ${monthly_cost}

Operation:
{operation_description}

Suggest optimizations for:
1. Model selection (cheaper alternatives)
2. Prompt engineering (reduce token usage)
3. Caching strategies
4. Batch processing opportunities
5. Request consolidation
6. Fallback chains (free models first)
7. Pre-processing to avoid LLM calls

For each suggestion, provide:
- Implementation approach
- Estimated cost savings
- Potential quality impact
- Implementation complexity

Target: 50% cost reduction while maintaining 95%+ quality.
```

**Variables**:
- `{model}`: Current LLM model
- `{avg_tokens}`: Average tokens per request
- `{requests_per_day}`: Daily request volume
- `{cost_per_request}`: Cost per request
- `{monthly_cost}`: Total monthly cost
- `{operation_description}`: Description of operation

---

## Usage Notes

### Best Practices

1. **Variable Substitution**: Always replace `{variables}` with actual values
2. **Temperature Settings**:
   - 0.0-0.3: Factual extraction, classification
   - 0.4-0.7: Content generation, analysis
   - 0.8-1.0: Creative writing, brainstorming
3. **Token Limits**: Set appropriate `max_tokens` to control cost
4. **Model Selection**: Use cheapest model that meets quality needs
5. **Caching**: Cache responses for identical prompts
6. **Validation**: Always validate AI outputs programmatically

### Prompt Engineering Tips

- **Be Specific**: Clear, detailed instructions
- **Provide Examples**: Show desired output format
- **Use Constraints**: Specify limits and requirements
- **Structure Output**: Request JSON for easy parsing
- **Include Context**: Provide relevant background
- **Test Iteratively**: Refine prompts based on results

---

**End of Prompts Library**
