# Model-Specific Prompts for ArbFinder Suite

Different AI models have different strengths and optimal prompting strategies. This guide provides model-specific prompt variations for common tasks in ArbFinder Suite development.

---

## Table of Contents

1. [Model Characteristics](#model-characteristics)
2. [GPT-4 Prompts](#gpt-4-prompts)
3. [Claude Prompts](#claude-prompts)
4. [Llama Prompts](#llama-prompts)
5. [Gemini Prompts](#gemini-prompts)
6. [Mistral Prompts](#mistral-prompts)
7. [Task-Specific Recommendations](#task-specific-recommendations)

---

## Model Characteristics

### GPT-4 (OpenAI)

**Strengths**:
- Code generation and completion
- Complex reasoning
- Following detailed instructions
- Multi-language support

**Weaknesses**:
- Can be verbose
- May hallucinate specific APIs
- Expensive for high volume

**Best For**:
- Complex code generation
- Architecture design
- Code explanation
- Creative content

### Claude 3.5 Sonnet (Anthropic)

**Strengths**:
- Excellent reasoning
- Long context window (200K)
- Safety-conscious
- Good at following instructions precisely

**Weaknesses**:
- Occasionally overly cautious
- Slower than some alternatives
- More expensive

**Best For**:
- Code review
- Security analysis
- Complex refactoring
- Long-form documentation

### Llama 3.1 8B (Meta)

**Strengths**:
- Fast inference
- Good quality for size
- Free via OpenRouter
- Efficient for simple tasks

**Weaknesses**:
- Less capable than GPT-4/Claude
- May struggle with complex reasoning
- Smaller context window

**Best For**:
- Data extraction
- Classification
- Simple code generation
- High-volume tasks (free!)

### Gemini Pro (Google)

**Strengths**:
- Multimodal (text + images)
- Large context window
- Good at structured output
- Free tier available

**Weaknesses**:
- Availability can vary by region
- Less mature than GPT-4
- API changes frequently

**Best For**:
- Image analysis
- Multi-step reasoning
- Search/retrieval tasks
- Experimentation

### Mistral 7B (Mistral AI)

**Strengths**:
- Very fast
- Good quality for size
- Free options available
- European-focused

**Weaknesses**:
- Smaller context
- Less capable than larger models
- Newer, less tested

**Best For**:
- Quick tasks
- Structured output
- Cost-sensitive workloads
- Speed-critical applications

---

## GPT-4 Prompts

### Code Generation (GPT-4)

GPT-4 excels at code generation. Be specific and provide context:

```
You are an expert Python developer working on ArbFinder Suite, a price arbitrage finder.

Task: Create a FastAPI endpoint to search listings with full-text search.

Context:
- We use FastAPI with Pydantic models
- Database: D1 (SQLite-compatible)
- See backend/api/routes/listings.py for patterns

Requirements:
1. Endpoint: GET /api/listings/search
2. Query params: q (search query), limit, offset
3. Full-text search on title and description
4. Return paginated results with total count
5. Include proper error handling
6. Type hints for all parameters
7. Docstring with usage example

Provide complete, production-ready code with comments.
```

### Architecture (GPT-4)

GPT-4 is great for high-level design. Ask for multiple options:

```
Design 3 different approaches for implementing real-time price monitoring in ArbFinder Suite.

Context:
- Platform: Cloudflare Workers + D1 + R2
- Need to check 1000+ listings every hour
- Budget: Minimize costs
- Stack: Python backend, TypeScript Workers

For each approach, provide:
1. Architecture diagram (ASCII)
2. Pros and cons
3. Cost estimate
4. Scalability considerations
5. Code complexity

Then recommend which approach to use and why.
```

---

## Claude Prompts

### Code Review (Claude)

Claude excels at thoughtful, thorough reviews:

```
<role>
You are a senior software engineer reviewing code for security, performance, and maintainability.
</role>

<context>
Project: ArbFinder Suite (price arbitrage finder)
Stack: Python/FastAPI, Next.js, Cloudflare
Conventions: .github/copilot-instructions.md
</context>

<task>
Review this code for:
1. Security vulnerabilities (SQL injection, XSS, etc.)
2. Performance issues (N+1 queries, missing indexes)
3. Error handling completeness
4. Code style adherence to project conventions
5. Potential bugs

For each issue found:
- Severity: Critical/High/Medium/Low
- Explanation of the problem
- Specific code fix
- Why this fix is better
</task>

<code>
[PASTE CODE HERE]
</code>

<output>
Provide a structured review with issues grouped by severity.
</output>
```

### Refactoring (Claude)

Claude is excellent at careful refactoring:

```
<task>Refactor this function to improve readability and maintainability while preserving exact functionality</task>

<original_code>
[PASTE CODE]
</original_code>

<requirements>
- Extract repeated logic into helper functions
- Reduce nesting (max 2 levels)
- Add type hints if missing
- Improve variable names
- Add docstrings
- Maintain 100% backward compatibility
</requirements>

<thinking>
First, analyze the code:
1. What does it do?
2. What are the main issues?
3. What refactorings would help?
</thinking>

<refactored_code>
[Provide refactored code with inline comments explaining changes]
</refactored_code>

<explanation>
Explain each major change and why it improves the code.
</explanation>
```

---

## Llama Prompts

### Data Extraction (Llama 3.1)

Llama is great for structured extraction. Use clear formatting:

```
Extract product information from this listing title and return as JSON.

Title: "Dell Latitude 5420 14\" Laptop Intel i5-1145G7 16GB RAM 256GB SSD Windows 11 Pro"

Extract:
- brand: string
- model: string
- screen_size: number (in inches)
- processor: string
- ram: number (in GB)
- storage: number (in GB)
- storage_type: string (HDD/SSD)
- os: string

Return ONLY valid JSON, no explanations.

Example output format:
{
  "brand": "Dell",
  "model": "Latitude 5420",
  ...
}

Now extract from this title:
[ACTUAL TITLE]
```

### Classification (Llama 3.1)

Llama handles classification well with clear categories:

```
Classify this product into ONE category.

Categories:
1. electronics
2. clothing
3. home
4. sports
5. books
6. toys
7. other

Product: [PRODUCT_DESCRIPTION]

Return ONLY the category name, no explanations.

If unclear, return: other

Category:
```

---

## Gemini Prompts

### Image Analysis (Gemini Pro Vision)

Gemini excels at multimodal tasks:

```
Analyze this product image and extract information.

Image: [IMAGE_URL or base64]

Extract:
1. Product type (laptop, phone, clothing, etc.)
2. Brand (if visible in image)
3. Condition assessment (new, like-new, good, fair, poor)
4. Notable features visible in image
5. Any defects or damage visible
6. Estimated age/wear

Return as structured JSON:
{
  "product_type": "...",
  "brand": "..." or null,
  "condition": "...",
  "features": ["...", "..."],
  "defects": ["...", "..."],
  "notes": "..."
}
```

### Multi-Step Reasoning (Gemini Pro)

Gemini handles multi-step tasks well with chain-of-thought:

```
Determine the fair market value for this product using a step-by-step approach.

Product:
[PRODUCT_DETAILS]

Comparable Sales:
[LIST OF COMPS]

Steps:
1. Analyze the product condition
2. Filter comps to similar items
3. Calculate average price
4. Adjust for condition differences
5. Adjust for market trends
6. Consider seasonality
7. Provide price range

For each step, show your reasoning.

Final Output:
{
  "estimated_value": {
    "low": number,
    "mid": number,
    "high": number
  },
  "confidence": "high" | "medium" | "low",
  "reasoning": "explanation"
}
```

---

## Mistral Prompts

### Quick Summaries (Mistral 7B)

Mistral is very fast - use for quick tasks:

```
Summarize this product listing in 2-3 sentences.

Listing:
[PASTE LISTING]

Summary should include:
- Product type and brand
- Key specs
- Condition and price

Keep it concise and factual.
```

### Structured Output (Mistral)

Mistral is good at following format instructions:

```
[INST]
Convert this product description into a structured format.

Description:
[DESCRIPTION]

Output format (JSON):
{
  "title": "short title with brand and model",
  "condition": "new|like-new|good|fair|poor",
  "category": "category name",
  "price": number,
  "features": ["feature1", "feature2"]
}

Return ONLY the JSON, nothing else.
[/INST]
```

---

## Task-Specific Recommendations

### Data Extraction from Listings

**Best Model**: Llama 3.1 8B (free, fast, good enough)  
**Alternative**: Mistral 7B (if Llama unavailable)  
**Premium**: GPT-4 Turbo (for complex extractions)

**Prompt Pattern**:
```
Extract [FIELDS] from this listing.
Return as JSON.
Format: {exact JSON structure}
No explanations.

Listing: [DATA]
```

### SEO-Optimized Title Generation

**Best Model**: GPT-4 (creative, understands SEO)  
**Alternative**: Claude 3.5 (also excellent for copywriting)  
**Budget**: Llama 3.1 70B (good balance)

**Prompt Pattern**:
```
Generate SEO-optimized title for [PLATFORM].

Product: [DETAILS]
Platform character limit: [LIMIT]
Include: brand, model, key specs, condition
Keywords to include: [KEYWORDS]

Generate 3 variations, then pick the best.
```

### Code Generation

**Best Model**: GPT-4 (best at code)  
**Alternative**: Claude 3.5 (great for careful, thoughtful code)  
**Budget**: GPT-3.5 Turbo (still quite good)

**Prompt Pattern**:
```
Generate [LANGUAGE] code for [TASK].

Requirements: [LIST]
Patterns to follow: [REFERENCE]
Type safety: strict
Error handling: comprehensive

Provide production-ready code with tests.
```

### Security Review

**Best Model**: Claude 3.5 (thorough, safety-conscious)  
**Alternative**: GPT-4 (also excellent)  
**Budget**: Use both, compare results

**Prompt Pattern**:
```
Security review of this code.
Look for: [VULNERABILITY TYPES]
Severity levels: Critical/High/Medium/Low
Provide: issue, severity, fix, explanation

Code: [CODE]
```

### Market Analysis

**Best Model**: Claude 3.5 (excellent reasoning)  
**Alternative**: GPT-4 (also strong)  
**Budget**: Gemini Pro (good for analysis)

**Prompt Pattern**:
```
Analyze market trends for [PRODUCT CATEGORY].

Data: [COMPARABLE SALES]

Provide:
1. Price trend (rising/stable/falling)
2. Market velocity (days to sell)
3. Pricing recommendation
4. Risk assessment
5. Best time to list

Use data-driven reasoning.
```

### Documentation Writing

**Best Model**: GPT-4 (clear, comprehensive)  
**Alternative**: Claude 3.5 (thoughtful, well-structured)  
**Budget**: GPT-3.5 Turbo (still good)

**Prompt Pattern**:
```
Write documentation for [FEATURE].

Audience: [WHO]
Tone: [STYLE]
Include: overview, usage, examples, troubleshooting
Format: Markdown

Reference: [EXISTING DOCS]
```

---

## Cost-Performance Trade-offs

### High Volume Tasks (1000+ calls/day)

Use free models:
- Llama 3.1 8B
- Mistral 7B
- Gemma 2 9B

Trade-off: Slightly lower quality, significant cost savings

### Critical Tasks (accuracy is paramount)

Use premium models:
- GPT-4 (best overall)
- Claude 3.5 Sonnet (best reasoning)

Trade-off: Higher cost, best quality

### Medium Volume (100-1000 calls/day)

Mix strategies:
- Use free models with validation
- Fallback to premium on validation failure
- Use premium for final processing

---

## Hybrid Approaches

### Two-Phase Processing

```python
# Phase 1: Fast extraction with free model
basic_data = await llama_extract(listing)

# Phase 2: Enhancement with premium model (if needed)
if basic_data.confidence < 0.8:
    enhanced_data = await gpt4_extract(listing)
    return enhanced_data
return basic_data
```

### Ensemble Validation

```python
# Get results from multiple models
results = await asyncio.gather(
    llama_classify(text),
    mistral_classify(text),
    gemini_classify(text)
)

# Use majority vote or confidence-weighted average
final_result = ensemble_vote(results)
```

### Cost-Aware Routing

```python
def select_model(task_complexity: str, budget_level: str) -> str:
    """Route to appropriate model based on complexity and budget."""
    
    if task_complexity == "simple":
        return "meta-llama/llama-3.1-8b-instruct:free"
    
    if budget_level == "low":
        return "mistralai/mistral-7b-instruct:free"
    
    if task_complexity == "complex":
        return "openai/gpt-4-turbo" if budget_level == "high" else "anthropic/claude-3.5-sonnet"
    
    return "meta-llama/llama-3.1-70b-instruct"  # Default: good balance
```

---

## Testing Different Models

### A/B Testing Template

```python
import random

async def ab_test_models(input_data, model_a, model_b, split=0.5):
    """A/B test two models."""
    
    # Random assignment
    use_model_a = random.random() < split
    model = model_a if use_model_a else model_b
    
    # Execute
    start_time = time.time()
    result = await execute_model(model, input_data)
    duration = time.time() - start_time
    
    # Log for analysis
    log_ab_test({
        "model": model,
        "duration": duration,
        "result_quality": assess_quality(result),
        "cost": estimate_cost(model, input_data)
    })
    
    return result
```

---

## Best Practices

1. **Start with Free Models**: Use Llama/Mistral for development and testing
2. **Measure Quality**: Track metrics to justify premium models
3. **Use Caching**: Cache responses to reduce costs
4. **Batch When Possible**: Process multiple items in one call
5. **Monitor Costs**: Set up alerts for unexpected spikes
6. **Fallback Chain**: Always have backup models configured
7. **Validate Outputs**: Don't blindly trust any model
8. **Iterate on Prompts**: Test variations to find what works best

---

**Last Updated**: 2025-12-15  
**Maintained By**: AI Team  
**See Also**: [PROMPTS.md](PROMPTS.md) for general prompts
