# 🤖 ArbFinder Suite - Model-Specific Prompts

## Overview
This document contains optimized prompts tailored for specific AI models used in ArbFinder Suite, including OpenAI GPT models, OpenRouter models, and specialized task models.

---

## Table of Contents
1. [GPT-4 Prompts](#gpt-4-prompts)
2. [GPT-3.5 Turbo Prompts](#gpt-35-turbo-prompts)
3. [Claude Prompts](#claude-prompts)
4. [Open Source Model Prompts](#open-source-model-prompts)
5. [Code-Specific Models](#code-specific-models)
6. [Vision Models](#vision-models)

---

## GPT-4 Prompts

### Complex Analysis Tasks
GPT-4 excels at reasoning and complex analysis.

#### Market Analysis (GPT-4)
```yaml
model: gpt-4
temperature: 0.3
max_tokens: 2000
system: |
  You are an expert market analyst with deep knowledge of e-commerce, 
  pricing strategies, and market dynamics. You provide data-driven insights 
  with quantitative analysis and actionable recommendations.

user: |
  Analyze this product's market position:
  
  Product: {product_name}
  Current Price: ${price}
  Category: {category}
  Comparable Prices: {comp_prices_list}
  Sales Velocity: {sales_velocity}
  Competition Level: {competition}
  
  Provide:
  1. Market positioning analysis (2-3 paragraphs)
  2. Price elasticity assessment
  3. Competitive advantage identification
  4. Optimal pricing strategy
  5. 30-day demand forecast
  6. Risk factors
  
  Support your analysis with quantitative reasoning.
```

#### Complex Data Extraction (GPT-4)
```yaml
model: gpt-4
temperature: 0.1
max_tokens: 1500
system: |
  You are a data extraction specialist. Extract structured information 
  from unstructured text with high accuracy. When uncertain, indicate 
  confidence levels.

user: |
  Extract comprehensive product information:
  
  {listing_text}
  
  Return JSON:
  {
    "product": {
      "brand": "string",
      "model": "string",
      "variant": "string",
      "condition": "new|excellent|good|fair|poor",
      "year": "integer|null"
    },
    "specifications": {
      // all technical specs as key-value
    },
    "features": ["array", "of", "features"],
    "included_items": ["array"],
    "defects": ["array"],
    "metadata": {
      "confidence_score": 0.0-1.0,
      "extraction_notes": "string"
    }
  }
```

---

## GPT-3.5 Turbo Prompts

### High-Volume Tasks
GPT-3.5 Turbo is cost-effective for simpler, high-volume tasks.

#### Product Title Generation (GPT-3.5)
```yaml
model: gpt-3.5-turbo
temperature: 0.7
max_tokens: 100
system: |
  You write concise, SEO-optimized product titles for e-commerce.
  Max 80 characters. Format: Brand Model - Condition - Key Feature

user: |
  Create title:
  Brand: {brand}
  Model: {model}
  Condition: {condition}
  Key Feature: {feature}
  
  Examples:
  - Apple iPhone 12 Pro - Excellent - 256GB Unlocked
  - Sony WH-1000XM4 - Like New - Noise Canceling
  - Nintendo Switch - Good - Complete in Box
  
  Generate title (max 80 chars):
```

#### Quick Categorization (GPT-3.5)
```yaml
model: gpt-3.5-turbo
temperature: 0.2
max_tokens: 50
system: |
  You categorize products into e-commerce categories.
  Format: Category > Subcategory > Type

user: |
  Categorize: {product_name}
  
  Return only category path, no explanation:
```

#### Bullet Point Generation (GPT-3.5)
```yaml
model: gpt-3.5-turbo
temperature: 0.6
max_tokens: 200
system: |
  You write compelling product bullet points. Each bullet:
  - Starts with benefit or feature
  - Max 15 words
  - Action-oriented
  - Buyer-focused

user: |
  Product: {product_info}
  
  Generate 5 bullet points:
  • 
  • 
  • 
  • 
  • 
```

---

## Claude Prompts

### Detailed Content Creation
Claude excels at long-form, detailed content.

#### Comprehensive Description (Claude)
```yaml
model: claude-3-opus
temperature: 0.7
max_tokens: 1000
system: |
  You are a professional product copywriter with expertise in e-commerce 
  content. You write engaging, informative descriptions that convert browsers 
  into buyers.

user: |
  Write a comprehensive product description:
  
  Product: {product_name}
  Category: {category}
  Condition: {condition}
  Key Features: {features}
  Target Audience: {audience}
  
  Structure:
  1. Opening hook (2 sentences)
  2. Main features paragraph (3-4 sentences)
  3. Technical specifications (formatted list)
  4. Condition details (if used)
  5. Closing with CTA
  
  Tone: Professional yet approachable
  Length: 250-300 words
  Focus: Benefits over features
```

#### Detailed Analysis (Claude)
```yaml
model: claude-3-opus
temperature: 0.3
max_tokens: 2000
system: |
  You are a thorough analyst who provides detailed, well-structured analysis 
  with clear reasoning and specific recommendations.

user: |
  Provide detailed analysis:
  
  Context: {context}
  Data: {data}
  Question: {question}
  
  Structure your response:
  ## Executive Summary
  [2-3 sentence overview]
  
  ## Detailed Analysis
  [Comprehensive analysis with subsections]
  
  ## Key Findings
  [Numbered list of findings]
  
  ## Recommendations
  [Specific, actionable recommendations]
  
  ## Risk Assessment
  [Potential risks and mitigation]
```

---

## Open Source Model Prompts

### Llama 2 / Mistral Prompts
Optimized for open-source models with limited context.

#### Simple Classification (Llama 2)
```yaml
model: llama-2-13b
temperature: 0.1
max_tokens: 50
prompt: |
  Classify this product condition. Respond with ONLY ONE WORD from this list:
  NEW, EXCELLENT, GOOD, FAIR, POOR
  
  Description: {description}
  
  Condition:
```

#### Entity Extraction (Mistral)
```yaml
model: mistral-7b
temperature: 0.2
max_tokens: 200
prompt: |
  Extract information from this product title:
  
  "{title}"
  
  Brand:
  Model:
  Key Features:
  
  Instructions: Extract only if clearly stated. Use "Unknown" if not found.
```

---

## Code-Specific Models

### CodeLlama Prompts

#### Code Generation (CodeLlama)
```yaml
model: codellama-34b
temperature: 0.2
max_tokens: 1000
system: |
  You are an expert Python programmer. Write clean, efficient, well-documented code 
  following best practices.

user: |
  Write a Python function:
  
  Function: {function_description}
  Inputs: {inputs}
  Outputs: {outputs}
  Constraints: {constraints}
  
  Requirements:
  - Type hints
  - Docstring (Google style)
  - Error handling
  - Unit test example
  
  Generate the code:
```

### GPT-3.5 Code (Code Completion)
```yaml
model: gpt-3.5-turbo
temperature: 0.1
max_tokens: 500
system: |
  You complete code snippets efficiently and correctly.
  Follow the existing code style and conventions.

user: |
  Complete this function:
  
  ```python
  {incomplete_code}
  ```
  
  Complete the implementation:
```

---

## Vision Models

### GPT-4 Vision Prompts

#### Product Image Analysis
```yaml
model: gpt-4-vision-preview
temperature: 0.3
max_tokens: 500
messages:
  - role: system
    content: |
      You analyze product images to extract useful information for e-commerce 
      listings. Focus on condition, features, and quality.
      
  - role: user
    content:
      - type: image_url
        image_url: {image_url}
      - type: text
        text: |
          Analyze this product image and provide:
          
          1. Product Type: [Identify the product]
          2. Visible Condition: [Assess condition from image]
          3. Key Features: [List visible features]
          4. Defects/Damage: [Note any visible issues]
          5. Brand/Model: [If visible in image]
          6. Image Quality: [Rate 1-10 for listing use]
          7. Recommendations: [Suggestions for better photos]
          
          Be specific and objective.
```

#### Quality Check
```yaml
model: gpt-4-vision-preview
temperature: 0.2
max_tokens: 300
messages:
  - role: system
    content: |
      You verify if product images meet e-commerce listing standards.
      
  - role: user
    content:
      - type: image_url
        image_url: {image_url}
      - type: text
        text: |
          Check if this image meets listing standards:
          
          Requirements:
          - Clear, well-lit product photo
          - Product is primary focus
          - Minimal background distractions
          - Adequate resolution
          - No watermarks (except allowed branding)
          - Shows product condition accurately
          
          Return:
          - PASS or FAIL
          - Issues found (if any)
          - Suggestions for improvement
```

---

## Embedding Models

### OpenAI Embeddings
For similarity search and semantic matching.

#### Generate Product Embedding
```yaml
model: text-embedding-ada-002
input: |
  {product_title}
  {product_description}
  {category}
  {key_features}
```

#### Usage in Code
```python
import openai

def get_product_embedding(product_data: dict) -> list:
    """Generate embedding for product."""
    text = f"""
    {product_data['title']}
    {product_data['description']}
    Category: {product_data['category']}
    Features: {', '.join(product_data['features'])}
    """
    
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text.strip()
    )
    
    return response['data'][0]['embedding']
```

---

## Function Calling

### GPT-4 Function Calling

#### Price Analysis Function
```yaml
model: gpt-4
temperature: 0.3
functions:
  - name: calculate_pricing
    description: Calculate optimal pricing based on market data
    parameters:
      type: object
      properties:
        base_price:
          type: number
          description: Cost basis or purchase price
        comparable_prices:
          type: array
          items:
            type: number
          description: Array of comparable selling prices
        condition:
          type: string
          enum: [new, excellent, good, fair, poor]
        target_margin:
          type: number
          description: Desired profit margin as percentage
      required: [base_price, comparable_prices, condition]

messages:
  - role: user
    content: |
      Calculate optimal price:
      I bought this item for $100
      Similar items sell for: $150, $175, $160, $155
      Condition: excellent
      Want 25% margin minimum
```

#### Product Search Function
```yaml
model: gpt-4
temperature: 0.2
functions:
  - name: search_products
    description: Search product database
    parameters:
      type: object
      properties:
        query:
          type: string
          description: Search query
        category:
          type: string
          description: Filter by category
        price_min:
          type: number
        price_max:
          type: number
        condition:
          type: string
          enum: [new, excellent, good, fair, poor]
        sort_by:
          type: string
          enum: [price, date, relevance]
      required: [query]

messages:
  - role: user
    content: Find used MacBook Pro laptops under $1000
```

---

## Model Selection Guide

### Task → Model Mapping

#### Complex Reasoning
**Use**: GPT-4, Claude Opus
- Market analysis
- Strategic planning
- Complex extraction
- Multi-step reasoning

#### Content Creation
**Use**: GPT-4, Claude Opus, GPT-3.5
- Product descriptions
- Marketing copy
- Blog posts
- Email templates

#### Simple Classification
**Use**: GPT-3.5, Mistral, Llama 2
- Categorization
- Sentiment analysis
- Basic extraction
- Yes/no decisions

#### Code Tasks
**Use**: GPT-4, CodeLlama, GPT-3.5
- Code generation
- Bug fixing
- Code review
- Documentation

#### Image Analysis
**Use**: GPT-4 Vision
- Product condition assessment
- Quality checks
- Feature identification
- Compliance verification

#### Embeddings
**Use**: text-embedding-ada-002, text-embedding-3-small
- Similarity search
- Semantic matching
- Clustering
- Recommendations

---

## Cost Optimization

### Strategies by Model

#### GPT-4 ($0.03/1K tokens)
**Use for**:
- High-value decisions
- Complex analysis
- Critical accuracy needs
- Low-volume tasks

**Optimize**:
- Concise prompts
- Specific output format
- Lower max_tokens
- Cache results

#### GPT-3.5 Turbo ($0.002/1K tokens)
**Use for**:
- High-volume tasks
- Simple extraction
- Basic generation
- Real-time applications

**Optimize**:
- Batch processing
- Template responses
- Shorter prompts
- Aggressive caching

#### Claude ($0.015/1K tokens)
**Use for**:
- Long-form content
- Detailed analysis
- Creative writing
- Cost-effective alternative to GPT-4

**Optimize**:
- Larger context windows
- Fewer API calls
- Batch similar tasks

---

## Prompt Engineering Tips

### By Model Characteristics

#### GPT-4
- Can handle complex, multi-step instructions
- Excels with reasoning tasks
- Benefits from detailed system prompts
- Understands nuance and context

#### GPT-3.5
- Needs more explicit instructions
- Works best with examples
- Keep prompts focused
- Use structured output formats

#### Claude
- Excels at long-form content
- Prefers natural language
- Good at following formatting rules
- Strong ethical guidelines

#### Open Source (Llama, Mistral)
- Keep prompts simple and direct
- Use examples liberally
- Specify format explicitly
- Lower expectations for reasoning

---

## Testing Template

```python
import openai

def test_prompt_variants():
    """Test different prompt variants for same task."""
    
    prompts = {
        "v1_detailed": "...",
        "v2_concise": "...",
        "v3_with_examples": "..."
    }
    
    results = {}
    
    for name, prompt in prompts.items():
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        results[name] = {
            "response": response.choices[0].message.content,
            "tokens": response.usage.total_tokens,
            "cost": calculate_cost(response.usage.total_tokens)
        }
    
    return results
```

---

## Version History

| Date | Model | Changes |
|------|-------|---------|
| 2024-12-15 | GPT-4 | Initial prompts for analysis tasks |
| 2024-12-15 | GPT-3.5 | High-volume task prompts |
| 2024-12-15 | Claude | Long-form content prompts |
| 2024-12-15 | Vision | Image analysis prompts |

---

**Last Updated**: 2024-12-15  
**Maintained By**: AI Team

**Note**: Test prompts with your specific use cases. Monitor costs and quality. Iterate based on results.
