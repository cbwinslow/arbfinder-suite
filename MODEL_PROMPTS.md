# Model-Specific Prompts

This document contains prompts optimized for specific AI models available through OpenRouter.

---

## Overview

Different AI models have different strengths, weaknesses, and optimal prompt formats. This guide provides model-specific prompt templates optimized for the free models available through OpenRouter.

---

## Free Models on OpenRouter

### Available Free Models (as of December 2024)

1. **GPT-3.5-Turbo** - General purpose, fast
2. **Claude-3-Haiku** - Fast, efficient, good reasoning
3. **Mixtral-8x7B** - Open source, multilingual
4. **Mistral-7B** - Fast, instruction-following
5. **Llama-3-8B** - Open source, versatile

---

## GPT-3.5-Turbo Prompts

### Characteristics
- Fast response times
- Good for straightforward tasks
- Handles JSON well
- Context window: 16K tokens
- Best for: data extraction, classification, simple generation

### Optimized System Prompt

```json
{
  "model": "openrouter/openai/gpt-3.5-turbo",
  "messages": [
    {
      "role": "system",
      "content": "You are a precise data extraction assistant. Respond ONLY with valid JSON. Do not include markdown formatting, explanations, or any text outside the JSON structure."
    },
    {
      "role": "user",
      "content": "{user_prompt}"
    }
  ],
  "temperature": 0.3,
  "max_tokens": 2000
}
```

### Data Extraction (GPT-3.5-Turbo)

```markdown
Extract product information from this listing.

LISTING:
{listing_text}

REQUIRED FIELDS:
- title: string (product name)
- price: number (numeric only)
- condition: string (new|used|refurbished)
- category: string
- brand: string or null

OUTPUT: Valid JSON only, no other text

EXAMPLE OUTPUT:
{"title":"iPhone 12","price":599.99,"condition":"used","category":"Electronics","brand":"Apple"}
```

### Title Generation (GPT-3.5-Turbo)

```markdown
Generate a product title. Requirements:
- 60-80 characters
- Include: brand, model, key feature
- Title case
- No emojis or symbols

PRODUCT INFO:
{product_json}

PLATFORM: {platform}

OUTPUT: Title only, no explanation
```

---

## Claude-3-Haiku Prompts

### Characteristics
- Excellent reasoning
- Good with context
- Strong instruction following
- Context window: 200K tokens
- Best for: analysis, reasoning, complex tasks

### Optimized System Prompt

```json
{
  "model": "openrouter/anthropic/claude-3-haiku",
  "messages": [
    {
      "role": "system",
      "content": "You are an expert analyst. Provide detailed, thoughtful analysis. Structure your responses clearly with headings and bullet points."
    },
    {
      "role": "user",
      "content": "{user_prompt}"
    }
  ],
  "temperature": 0.5,
  "max_tokens": 4000
}
```

### Market Analysis (Claude-3-Haiku)

```markdown
Analyze the market for this product and provide pricing recommendations.

## Product Information
Title: {title}
Category: {category}
Condition: {condition}
Current Listings: {current_listings}

## Comparable Sales
{comp_data}

## Analysis Required

1. **Market Overview**
   - Supply and demand assessment
   - Price trend analysis
   - Seasonal factors

2. **Pricing Strategy**
   - Recommended list price with justification
   - Minimum acceptable price
   - Best offer threshold

3. **Competitive Positioning**
   - How this item compares
   - Unique selling points
   - Potential concerns

4. **Risk Assessment**
   - Estimated time to sell
   - Market volatility
   - Confidence level

Please provide a structured analysis with clear recommendations and reasoning.
```

### Listing Description (Claude-3-Haiku)

```markdown
Write a compelling product listing description.

## Product Details
{product_json}

## Requirements
- Length: 200-300 words
- Tone: Professional but friendly
- Structure:
  1. Opening hook (1-2 sentences)
  2. Key features and benefits (1 paragraph)
  3. Condition and details (1 paragraph)
  4. Shipping info (1 paragraph)
- Include SEO keywords: {keywords}
- Be honest about any flaws
- Format with bullet points for key features

## Platform
{platform}

Please write the description following this structure.
```

---

## Mixtral-8x7B Prompts

### Characteristics
- Open source, multilingual
- Good instruction following
- Strong reasoning capabilities
- Context window: 32K tokens
- Best for: complex reasoning, multi-step tasks

### Optimized System Prompt

```json
{
  "model": "openrouter/mistralai/mixtral-8x7b-instruct",
  "messages": [
    {
      "role": "system",
      "content": "<s>[INST] You are a helpful AI assistant specialized in e-commerce and product data. Provide accurate, structured responses. [/INST]</s>"
    },
    {
      "role": "user",
      "content": "[INST] {user_prompt} [/INST]"
    }
  ],
  "temperature": 0.4,
  "max_tokens": 3000
}
```

### Metadata Enrichment (Mixtral-8x7B)

```markdown
[INST] 
Analyze this product and fill in missing metadata.

PRODUCT TITLE:
{title}

PRODUCT DESCRIPTION:
{description}

TASK:
Extract or infer the following metadata:
1. Category (choose most specific from hierarchy)
2. Brand (official brand name)
3. Model (specific model name/number)
4. Key specifications (as a structured object)
5. Condition estimate (if not specified)
6. Relevant tags (5-10 keywords)

CATEGORY HIERARCHY:
{category_list}

OUTPUT:
Provide a JSON object with the fields above. Include a "confidence" score (0-1) for each inferred field.
[/INST]
```

### Multi-Step Reasoning (Mixtral-8x7B)

```markdown
[INST]
Perform a multi-step analysis to determine if this is a good arbitrage opportunity.

STEP 1: Data Validation
- Verify the listing data is complete and accurate
- Flag any suspicious or anomalous values
- Check for data quality issues

STEP 2: Market Research
- Find comparable items and their prices
- Analyze market trends
- Consider seasonal factors

STEP 3: Cost Calculation
- Calculate all fees and costs
- Determine break-even price
- Estimate net profit

STEP 4: Risk Assessment
- Evaluate demand and competition
- Consider time to sell
- Identify potential issues

STEP 5: Final Recommendation
- Provide buy/no-buy recommendation
- Justify the decision with data
- Suggest optimal pricing if buying

LISTING DATA:
{listing_json}

Please work through each step systematically and provide a comprehensive analysis.
[/INST]
```

---

## Mistral-7B Prompts

### Characteristics
- Fast and efficient
- Good instruction following
- Compact model
- Context window: 8K tokens
- Best for: quick tasks, classification, simple generation

### Optimized System Prompt

```json
{
  "model": "openrouter/mistralai/mistral-7b-instruct",
  "messages": [
    {
      "role": "system",
      "content": "<s>[INST] You are a concise AI assistant. Provide direct, accurate answers without unnecessary elaboration. [/INST]</s>"
    },
    {
      "role": "user",
      "content": "[INST] {user_prompt} [/INST]"
    }
  ],
  "temperature": 0.3,
  "max_tokens": 1000
}
```

### Quick Classification (Mistral-7B)

```markdown
[INST]
Classify this product into ONE category.

PRODUCT: {title}

CATEGORIES:
- Electronics > Computers
- Electronics > Audio
- Electronics > Video
- Clothing > Men's
- Clothing > Women's
- Home & Garden
- Sports & Outdoors
- Collectibles
- Other

OUTPUT: Category only, no explanation
[/INST]
```

### Simple Title Enhancement (Mistral-7B)

```markdown
[INST]
Improve this product title. Make it clear, searchable, and under 80 characters.

ORIGINAL: {original_title}

RULES:
- Include brand and model if present
- Remove unnecessary words
- Use title case
- No symbols or emojis

OUTPUT: Improved title only
[/INST]
```

---

## Llama-3-8B Prompts

### Characteristics
- Open source, Meta's model
- Versatile, general purpose
- Good reasoning
- Context window: 8K tokens
- Best for: general tasks, conversation

### Optimized System Prompt

```json
{
  "model": "openrouter/meta-llama/llama-3-8b-instruct",
  "messages": [
    {
      "role": "system",
      "content": "You are a knowledgeable assistant helping with e-commerce product management. Provide helpful, accurate information."
    },
    {
      "role": "user",
      "content": "{user_prompt}"
    }
  ],
  "temperature": 0.5,
  "max_tokens": 2000
}
```

### Product Description (Llama-3-8B)

```markdown
Write a product description for:

**Product:** {title}
**Condition:** {condition}
**Price:** ${price}
**Category:** {category}

**Requirements:**
- 150-250 words
- Highlight key features
- Mention condition honestly
- Include specifications if known
- End with shipping/return info

**Tone:** Professional and friendly
```

### Comparison Analysis (Llama-3-8B)

```markdown
Compare these two similar products and recommend which is the better buy.

**Product A:**
{product_a_json}

**Product B:**
{product_b_json}

**Comparison Criteria:**
- Price value
- Condition
- Features
- Specifications
- Seller reputation
- Shipping cost/time

**Output:**
1. Side-by-side comparison
2. Pros and cons for each
3. Recommendation with reasoning
```

---

## Model Selection Guide

### Task-to-Model Mapping

| Task | Recommended Model | Alternative |
|------|------------------|-------------|
| Data Extraction | GPT-3.5-Turbo | Mistral-7B |
| Classification | Mistral-7B | GPT-3.5-Turbo |
| Market Analysis | Claude-3-Haiku | Mixtral-8x7B |
| Listing Generation | Claude-3-Haiku | Llama-3-8B |
| Metadata Enrichment | Mixtral-8x7B | Claude-3-Haiku |
| Quick Tasks | Mistral-7B | GPT-3.5-Turbo |
| Complex Reasoning | Claude-3-Haiku | Mixtral-8x7B |
| Multi-step Tasks | Mixtral-8x7B | Claude-3-Haiku |

### Performance Characteristics

```python
# Model comparison
MODELS = {
    "gpt-3.5-turbo": {
        "speed": "very fast",
        "cost": "free",
        "quality": "good",
        "context": "16K",
        "best_for": ["extraction", "classification"]
    },
    "claude-3-haiku": {
        "speed": "fast",
        "cost": "free",
        "quality": "excellent",
        "context": "200K",
        "best_for": ["analysis", "reasoning", "writing"]
    },
    "mixtral-8x7b": {
        "speed": "moderate",
        "cost": "free",
        "quality": "very good",
        "context": "32K",
        "best_for": ["reasoning", "multi-step"]
    },
    "mistral-7b": {
        "speed": "very fast",
        "cost": "free",
        "quality": "good",
        "context": "8K",
        "best_for": ["quick tasks", "classification"]
    },
    "llama-3-8b": {
        "speed": "fast",
        "cost": "free",
        "quality": "good",
        "context": "8K",
        "best_for": ["general purpose"]
    }
}
```

---

## Temperature Guidelines

### By Task Type

```python
TEMPERATURE_SETTINGS = {
    "data_extraction": 0.1,      # Very deterministic
    "classification": 0.2,        # Mostly deterministic
    "title_generation": 0.4,      # Some creativity
    "description_writing": 0.6,   # More creative
    "market_analysis": 0.3,       # Balanced
    "reasoning": 0.4,             # Balanced
    "code_generation": 0.2,       # Mostly deterministic
    "creative_writing": 0.8,      # Very creative
}
```

---

## Prompt Engineering Best Practices by Model

### GPT-3.5-Turbo
- ✅ Keep prompts concise
- ✅ Use clear structure
- ✅ Specify JSON output format exactly
- ✅ Provide examples
- ❌ Avoid very long context
- ❌ Don't expect deep reasoning

### Claude-3-Haiku
- ✅ Use markdown formatting
- ✅ Provide detailed context
- ✅ Ask for structured analysis
- ✅ Use headings and sections
- ❌ Don't be too brief
- ❌ Avoid ambiguity

### Mixtral-8x7B
- ✅ Use [INST] tags
- ✅ Break down complex tasks
- ✅ Provide clear steps
- ✅ Use examples
- ❌ Avoid very short prompts
- ❌ Don't skip context

### Mistral-7B
- ✅ Use [INST] tags
- ✅ Keep it simple and direct
- ✅ One task per prompt
- ✅ Specify output format
- ❌ Avoid complexity
- ❌ Don't exceed context window

### Llama-3-8B
- ✅ Clear, natural language
- ✅ Structured prompts
- ✅ Examples help
- ✅ Be specific
- ❌ Avoid jargon
- ❌ Don't be too verbose

---

## Example: Automated Model Selection

```python
from arbfinder.lib.openrouter import OpenRouterClient

def select_model_for_task(task_type: str, context_size: int) -> str:
    """Select the best free model for a given task"""
    
    if context_size > 100000:
        return "anthropic/claude-3-haiku"
    
    if task_type == "data_extraction":
        return "openai/gpt-3.5-turbo"
    elif task_type == "market_analysis":
        return "anthropic/claude-3-haiku"
    elif task_type == "classification":
        return "mistralai/mistral-7b-instruct"
    elif task_type == "reasoning":
        return "mistralai/mixtral-8x7b-instruct"
    elif task_type == "description_writing":
        return "anthropic/claude-3-haiku"
    else:
        return "meta-llama/llama-3-8b-instruct"

# Usage
client = OpenRouterClient()
model = select_model_for_task("market_analysis", 5000)
response = client.chat(
    model=model,
    messages=[...],
    temperature=0.4
)
```

---

## Testing Prompts

### A/B Testing Template

```python
# Compare prompt variations
prompts = {
    "version_a": "Extract product info: {text}",
    "version_b": "Analyze this product listing and extract...",
}

results = {}
for version, prompt in prompts.items():
    responses = []
    for sample in test_samples:
        response = model.generate(prompt.format(text=sample))
        responses.append(evaluate_response(response))
    results[version] = {
        "accuracy": calculate_accuracy(responses),
        "avg_tokens": calculate_avg_tokens(responses),
        "avg_time": calculate_avg_time(responses)
    }

best_version = max(results, key=lambda x: results[x]["accuracy"])
```

---

Last Updated: 2024-12-15  
Version: 1.0
