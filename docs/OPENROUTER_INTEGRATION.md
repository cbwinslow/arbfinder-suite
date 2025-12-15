# OpenRouter SDK Integration Guide
# ArbFinder Suite

**Version**: 1.0  
**Date**: 2025-12-15  
**Target**: Developers

---

## Table of Contents

1. [Overview](#overview)
2. [Why OpenRouter](#why-openrouter)
3. [Setup](#setup)
4. [Client Implementation](#client-implementation)
5. [Free Models](#free-models)
6. [Streaming Support](#streaming-support)
7. [Code Completion](#code-completion)
8. [Model Management](#model-management)
9. [Best Practices](#best-practices)
10. [Examples](#examples)

---

## Overview

OpenRouter provides unified access to multiple Large Language Model (LLM) providers through a single API. This integration allows ArbFinder Suite to leverage powerful AI capabilities while maintaining flexibility and cost efficiency.

### Key Features

- **Unified API**: Single interface for 50+ models
- **Free Models**: Access to free open-source models
- **Automatic Fallbacks**: Seamless fallback to alternative models
- **Cost Optimization**: Route to cheapest suitable model
- **Provider Agnostic**: Easy switching between providers
- **Built-in Monitoring**: Usage tracking and analytics

### Supported Providers

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3.5, Claude 3)
- Google (Gemini Pro, PaLM)
- Meta (Llama 3.1, Llama 3)
- Mistral AI (Mistral, Mixtral)
- Many more...

---

## Why OpenRouter

### Advantages

1. **Cost Efficiency**
   - Access free models for development
   - Automatic routing to cheapest suitable model
   - No commitment to single provider

2. **Flexibility**
   - Easy model switching
   - A/B testing different models
   - Gradual migration strategies

3. **Reliability**
   - Automatic fallbacks on provider outages
   - Built-in retry logic
   - High availability

4. **Simplicity**
   - Single API key for all providers
   - Consistent interface
   - Unified monitoring

### Use Cases in ArbFinder

| Task | Recommended Model | Reasoning |
|------|------------------|-----------|
| Data Extraction | Llama 3.1 8B (free) | Fast, structured output |
| Metadata Enrichment | Llama 3.1 8B (free) | Good at classification |
| Title Generation | GPT-4 | Creative, SEO-optimized |
| Market Analysis | Claude 3.5 | Strong reasoning |
| Code Completion | GPT-4 Turbo | Best code understanding |

---

## Setup

### Step 1: Get API Key

1. Sign up at [https://openrouter.ai](https://openrouter.ai)
2. Navigate to Keys section
3. Create new API key
4. Copy key (starts with `sk-or-v1-`)

### Step 2: Set Environment Variable

```bash
# Add to ~/.bashrc or ~/.zshrc
export OPENROUTER_API_KEY="sk-or-v1-..."
export OPENROUTER_APP_NAME="ArbFinder Suite"
export OPENROUTER_APP_URL="https://arbfinder.com"

# Reload shell
source ~/.bashrc
```

### Step 3: Install Dependencies

```bash
# Python
pip install httpx pydantic

# TypeScript
npm install openai  # OpenRouter uses OpenAI-compatible format
```

### Step 4: Verify Connection

```bash
# Test with curl
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "HTTP-Referer: $OPENROUTER_APP_URL" \
  -H "X-Title: $OPENROUTER_APP_NAME"
```

---

## Client Implementation

### Python Client

**File**: `backend/integrations/openrouter/client.py`

```python
"""
OpenRouter API client for ArbFinder Suite.
Provides unified access to multiple LLM providers.
"""

from typing import Optional, List, Dict, Any, AsyncIterator
import os
import json
import httpx
from pydantic import BaseModel


class Message(BaseModel):
    """Chat message."""
    role: str
    content: str


class CompletionRequest(BaseModel):
    """Completion request parameters."""
    model: str
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    stream: bool = False


class CompletionChoice(BaseModel):
    """Completion response choice."""
    message: Message
    finish_reason: str
    index: int


class Usage(BaseModel):
    """Token usage statistics."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class CompletionResponse(BaseModel):
    """Completion response."""
    id: str
    model: str
    choices: List[CompletionChoice]
    usage: Usage
    created: int


class OpenRouterClient:
    """
    OpenRouter API client.
    
    Provides methods for:
    - Chat completions
    - Streaming responses
    - Model listing
    - Usage tracking
    
    Example:
        client = OpenRouterClient()
        response = await client.complete(
            model="meta-llama/llama-3.1-8b-instruct:free",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
        app_name: Optional[str] = None,
        app_url: Optional[str] = None,
        timeout: int = 60
    ):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key (defaults to env var)
            base_url: API base URL
            app_name: Application name for attribution
            app_url: Application URL for attribution
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set")
        
        self.base_url = base_url
        self.app_name = app_name or os.getenv("OPENROUTER_APP_NAME", "ArbFinder Suite")
        self.app_url = app_url or os.getenv("OPENROUTER_APP_URL", "")
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": self.app_url,
                "X-Title": self.app_name,
                "Content-Type": "application/json"
            },
            timeout=timeout
        )
    
    async def complete(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> CompletionResponse:
        """
        Get chat completion.
        
        Args:
            model: Model identifier (e.g., "meta-llama/llama-3.1-8b-instruct:free")
            messages: List of messages [{"role": "user", "content": "..."}]
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            Completion response with message and usage
            
        Raises:
            httpx.HTTPError: On API errors
        """
        request_data = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        
        response = await self.client.post(
            "/chat/completions",
            json=request_data
        )
        response.raise_for_status()
        
        return CompletionResponse(**response.json())
    
    async def stream(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream chat completion.
        
        Args:
            model: Model identifier
            messages: List of messages
            **kwargs: Additional parameters
        
        Yields:
            Content chunks as they arrive
            
        Example:
            async for chunk in client.stream(model, messages):
                print(chunk, end="", flush=True)
        """
        request_data = {
            "model": model,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        
        async with self.client.stream(
            "POST",
            "/chat/completions",
            json=request_data
        ) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    
                    if data == "[DONE]":
                        break
                    
                    try:
                        chunk = json.loads(data)
                        content = chunk["choices"][0]["delta"].get("content")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models.
        
        Returns:
            List of model information dictionaries
        """
        response = await self.client.get("/models")
        response.raise_for_status()
        
        data = response.json()
        return data.get("data", [])
    
    async def get_free_models(self) -> List[Dict[str, Any]]:
        """
        Get list of free models.
        
        Returns:
            List of free model information
        """
        all_models = await self.list_models()
        return [
            model for model in all_models
            if model.get("pricing", {}).get("prompt") == "0"
            and model.get("pricing", {}).get("completion") == "0"
        ]
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Singleton instance
_client: Optional[OpenRouterClient] = None


def get_client() -> OpenRouterClient:
    """
    Get singleton OpenRouter client.
    
    Returns:
        Shared OpenRouter client instance
    """
    global _client
    if _client is None:
        _client = OpenRouterClient()
    return _client
```

### TypeScript Client

**File**: `backend/integrations/openrouter/client.ts`

```typescript
/**
 * OpenRouter API client for TypeScript/JavaScript
 */

interface Message {
  role: string;
  content: string;
}

interface CompletionRequest {
  model: string;
  messages: Message[];
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  stop?: string[];
  stream?: boolean;
}

interface CompletionResponse {
  id: string;
  model: string;
  choices: Array<{
    message: Message;
    finish_reason: string;
    index: number;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  created: number;
}

export class OpenRouterClient {
  private apiKey: string;
  private baseURL: string;
  private appName: string;
  private appURL: string;

  constructor(
    apiKey?: string,
    baseURL: string = 'https://openrouter.ai/api/v1',
    appName?: string,
    appURL?: string
  ) {
    this.apiKey = apiKey || process.env.OPENROUTER_API_KEY || '';
    if (!this.apiKey) {
      throw new Error('OPENROUTER_API_KEY not set');
    }

    this.baseURL = baseURL;
    this.appName = appName || process.env.OPENROUTER_APP_NAME || 'ArbFinder Suite';
    this.appURL = appURL || process.env.OPENROUTER_APP_URL || '';
  }

  async complete(
    model: string,
    messages: Message[],
    options: Partial<CompletionRequest> = {}
  ): Promise<CompletionResponse> {
    const response = await fetch(`${this.baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'HTTP-Referer': this.appURL,
        'X-Title': this.appName,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model,
        messages,
        ...options,
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenRouter API error: ${response.statusText}`);
    }

    return response.json();
  }

  async *stream(
    model: string,
    messages: Message[],
    options: Partial<CompletionRequest> = {}
  ): AsyncIterableIterator<string> {
    const response = await fetch(`${this.baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'HTTP-Referer': this.appURL,
        'X-Title': this.appName,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model,
        messages,
        stream: true,
        ...options,
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenRouter API error: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('Response body is not readable');
    }

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') return;

            try {
              const parsed = JSON.parse(data);
              const content = parsed.choices[0]?.delta?.content;
              if (content) {
                yield content;
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  async listModels(): Promise<any[]> {
    const response = await fetch(`${this.baseURL}/models`, {
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'HTTP-Referer': this.appURL,
        'X-Title': this.appName,
      },
    });

    if (!response.ok) {
      throw new Error(`OpenRouter API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data || [];
  }

  async getFreeModels(): Promise<any[]> {
    const allModels = await this.listModels();
    return allModels.filter(
      (model) =>
        model.pricing?.prompt === '0' && model.pricing?.completion === '0'
    );
  }
}

// Singleton instance
let client: OpenRouterClient | null = null;

export function getClient(): OpenRouterClient {
  if (!client) {
    client = new OpenRouterClient();
  }
  return client;
}
```

---

## Free Models

### Discovering Free Models

**Script**: `scripts/openrouter/list_free_models.py`

```python
#!/usr/bin/env python3
"""
List available free models from OpenRouter.
"""

import asyncio
import json
from typing import List, Dict, Any
from backend.integrations.openrouter import OpenRouterClient


async def fetch_free_models() -> List[Dict[str, Any]]:
    """Fetch list of free models."""
    async with OpenRouterClient() as client:
        models = await client.get_free_models()
        return models


def print_models(models: List[Dict[str, Any]]):
    """Print models in readable format."""
    print(f"\n{'='*80}")
    print(f"AVAILABLE FREE MODELS ({len(models)} found)")
    print(f"{'='*80}\n")
    
    for model in models:
        print(f"ID: {model['id']}")
        print(f"Name: {model.get('name', 'N/A')}")
        print(f"Context: {model.get('context_length', 'N/A')} tokens")
        print(f"Architecture: {model.get('architecture', {}).get('modality', 'N/A')}")
        print(f"Description: {model.get('description', 'N/A')[:100]}...")
        print(f"{'-'*80}\n")


async def save_models_json(models: List[Dict[str, Any]], filepath: str = "free_models.json"):
    """Save models to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(models, f, indent=2)
    print(f"Models saved to {filepath}")


async def main():
    """Main function."""
    print("Fetching free models from OpenRouter...")
    
    try:
        models = await fetch_free_models()
        print_models(models)
        await save_models_json(models)
        
        # Print recommended models
        print("\n" + "="*80)
        print("RECOMMENDED MODELS FOR ARBFINDER")
        print("="*80 + "\n")
        
        recommendations = {
            "General Purpose": "meta-llama/llama-3.1-8b-instruct:free",
            "Fast & Efficient": "mistralai/mistral-7b-instruct:free",
            "Multilingual": "qwen/qwen-2-7b-instruct:free",
            "Google Alternative": "google/gemma-2-9b-it:free"
        }
        
        for use_case, model_id in recommendations.items():
            print(f"{use_case}: {model_id}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
```

Run it:

```bash
python scripts/openrouter/list_free_models.py
```

### Recommended Free Models

| Model ID | Best For | Context | Speed |
|----------|----------|---------|-------|
| `meta-llama/llama-3.1-8b-instruct:free` | General use | 128K | Fast |
| `mistralai/mistral-7b-instruct:free` | Quick tasks | 32K | Very Fast |
| `google/gemma-2-9b-it:free` | Google ecosystem | 8K | Fast |
| `qwen/qwen-2-7b-instruct:free` | Multilingual | 32K | Fast |

---

## Streaming Support

### Python Streaming Example

```python
async def stream_metadata_enrichment(product_title: str):
    """Stream metadata enrichment."""
    client = get_client()
    
    prompt = f"""
    Extract structured metadata from this product title:
    "{product_title}"
    
    Return JSON with: brand, model, category, condition, specifications
    """
    
    print("Enriching metadata... ", end="", flush=True)
    
    full_response = ""
    async for chunk in client.stream(
        model="meta-llama/llama-3.1-8b-instruct:free",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500
    ):
        print(chunk, end="", flush=True)
        full_response += chunk
    
    print("\n")
    
    # Parse JSON response
    try:
        metadata = json.loads(full_response)
        return metadata
    except json.JSONDecodeError:
        # Extract JSON from markdown if wrapped
        import re
        json_match = re.search(r'```json\n(.*?)\n```', full_response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        raise
```

### TypeScript Streaming Example

```typescript
async function streamListingGeneration(productData: any) {
  const client = getClient();
  
  const prompt = `Generate SEO-optimized listing for:\n${JSON.stringify(productData, null, 2)}`;
  
  process.stdout.write('Generating listing... ');
  
  let fullResponse = '';
  for await (const chunk of client.stream(
    'openai/gpt-4-turbo',
    [{ role: 'user', content: prompt }],
    { temperature: 0.7, max_tokens: 1000 }
  )) {
    process.stdout.write(chunk);
    fullResponse += chunk;
  }
  
  console.log('\n');
  return fullResponse;
}
```

---

## Code Completion

### Implementation

**File**: `backend/integrations/openrouter/completion.py`

```python
"""Code completion using OpenRouter."""

from typing import Optional
from .client import get_client


async def complete_code(
    code_context: str,
    cursor_position: Optional[int] = None,
    language: str = "python",
    max_tokens: int = 100
) -> str:
    """
    Get code completion.
    
    Args:
        code_context: Code before cursor
        cursor_position: Position of cursor in code
        language: Programming language
        max_tokens: Maximum tokens to generate
    
    Returns:
        Completion suggestion
    """
    client = get_client()
    
    # Split context at cursor
    if cursor_position:
        before_cursor = code_context[:cursor_position]
        after_cursor = code_context[cursor_position:]
    else:
        before_cursor = code_context
        after_cursor = ""
    
    prompt = f"""Complete this {language} code:

```{language}
{before_cursor}<CURSOR>{after_cursor}
```

Provide only the completion at <CURSOR>, no explanations."""
    
    response = await client.complete(
        model="openai/gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,  # Low for deterministic completion
        max_tokens=max_tokens,
        stop=["\n\n", "```", "def ", "class ", "async def "]
    )
    
    completion = response.choices[0].message.content.strip()
    return completion


async def explain_code(code: str, language: str = "python") -> str:
    """
    Explain what code does.
    
    Args:
        code: Code to explain
        language: Programming language
    
    Returns:
        Natural language explanation
    """
    client = get_client()
    
    prompt = f"""Explain this {language} code in simple terms:

```{language}
{code}
```"""
    
    response = await client.complete(
        model="anthropic/claude-3.5-sonnet",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )
    
    return response.choices[0].message.content


async def generate_docstring(
    function_code: str,
    style: str = "google"
) -> str:
    """
    Generate docstring for function.
    
    Args:
        function_code: Function source code
        style: Docstring style (google, numpy, sphinx)
    
    Returns:
        Generated docstring
    """
    client = get_client()
    
    prompt = f"""Generate a {style}-style docstring for this Python function:

```python
{function_code}
```

Return only the docstring, properly indented."""
    
    response = await client.complete(
        model="openai/gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=300
    )
    
    return response.choices[0].message.content
```

### Usage Example

```python
# Complete code
code = """
def calculate_roi(buy_price, sell_price, fees):
    profit = sell_price - buy_price - fees
    # Calculate ROI percentage
"""

completion = await complete_code(code, cursor_position=len(code))
print(completion)
# Output: return (profit / buy_price) * 100
```

---

## Model Management

### Model Selection Strategy

**File**: `backend/integrations/openrouter/models.py`

```python
"""Model selection and management."""

from typing import Optional, List, Dict
from enum import Enum


class TaskType(Enum):
    """Types of AI tasks."""
    EXTRACTION = "extraction"
    GENERATION = "generation"
    REASONING = "reasoning"
    CODE = "code"
    CHAT = "chat"


class Priority(Enum):
    """Selection priority."""
    COST = "cost"
    SPEED = "speed"
    QUALITY = "quality"


# Model recommendations by task and priority
MODEL_MAP: Dict[TaskType, Dict[Priority, str]] = {
    TaskType.EXTRACTION: {
        Priority.COST: "meta-llama/llama-3.1-8b-instruct:free",
        Priority.SPEED: "mistralai/mistral-7b-instruct:free",
        Priority.QUALITY: "openai/gpt-4-turbo"
    },
    TaskType.GENERATION: {
        Priority.COST: "meta-llama/llama-3.1-8b-instruct:free",
        Priority.SPEED: "mistralai/mistral-7b-instruct:free",
        Priority.QUALITY: "anthropic/claude-3.5-sonnet"
    },
    TaskType.REASONING: {
        Priority.COST: "qwen/qwen-2-7b-instruct:free",
        Priority.SPEED: "mistralai/mistral-7b-instruct:free",
        Priority.QUALITY: "openai/gpt-4"
    },
    TaskType.CODE: {
        Priority.COST: "meta-llama/llama-3.1-8b-instruct:free",
        Priority.SPEED: "mistralai/codestral-latest",
        Priority.QUALITY: "openai/gpt-4-turbo"
    },
    TaskType.CHAT: {
        Priority.COST: "meta-llama/llama-3.1-8b-instruct:free",
        Priority.SPEED: "mistralai/mistral-7b-instruct:free",
        Priority.QUALITY: "anthropic/claude-3.5-sonnet"
    }
}


def select_model(
    task_type: TaskType,
    priority: Priority = Priority.COST,
    fallback: bool = True
) -> str:
    """
    Select appropriate model for task.
    
    Args:
        task_type: Type of AI task
        priority: Selection priority (cost, speed, quality)
        fallback: Whether to fallback to free model if primary fails
    
    Returns:
        Model identifier
    """
    try:
        return MODEL_MAP[task_type][priority]
    except KeyError:
        if fallback:
            # Fallback to cost-effective model
            return MODEL_MAP[task_type][Priority.COST]
        raise ValueError(f"No model found for {task_type} with priority {priority}")


def get_fallback_models(primary_model: str) -> List[str]:
    """
    Get fallback models for a primary model.
    
    Args:
        primary_model: Primary model identifier
    
    Returns:
        List of fallback model identifiers
    """
    # Define fallback chains
    fallbacks = {
        "openai/gpt-4": [
            "openai/gpt-4-turbo",
            "anthropic/claude-3.5-sonnet",
            "meta-llama/llama-3.1-8b-instruct:free"
        ],
        "anthropic/claude-3.5-sonnet": [
            "anthropic/claude-3-opus",
            "openai/gpt-4-turbo",
            "meta-llama/llama-3.1-8b-instruct:free"
        ],
        "openai/gpt-4-turbo": [
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-sonnet",
            "meta-llama/llama-3.1-8b-instruct:free"
        ]
    }
    
    return fallbacks.get(primary_model, ["meta-llama/llama-3.1-8b-instruct:free"])


async def complete_with_fallback(
    client,
    model: str,
    messages: List[Dict],
    **kwargs
):
    """
    Complete with automatic fallback.
    
    Args:
        client: OpenRouter client
        model: Primary model
        messages: Chat messages
        **kwargs: Additional parameters
    
    Returns:
        Completion response
    """
    models_to_try = [model] + get_fallback_models(model)
    
    last_error = None
    for try_model in models_to_try:
        try:
            return await client.complete(
                model=try_model,
                messages=messages,
                **kwargs
            )
        except Exception as e:
            last_error = e
            print(f"Model {try_model} failed, trying fallback...")
            continue
    
    raise RuntimeError(f"All fallback models failed. Last error: {last_error}")
```

---

## Best Practices

### 1. Cost Management

```python
# Use free models for routine tasks
model = select_model(TaskType.EXTRACTION, Priority.COST)

# Use premium models only when needed
model = select_model(TaskType.GENERATION, Priority.QUALITY)

# Limit max_tokens to control costs
response = await client.complete(
    model=model,
    messages=messages,
    max_tokens=500  # Limit output length
)
```

### 2. Error Handling

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def safe_complete(model: str, messages: List[Dict]):
    """Complete with retry logic."""
    try:
        return await complete_with_fallback(
            client=get_client(),
            model=model,
            messages=messages
        )
    except Exception as e:
        logger.error(f"Completion failed: {e}")
        raise
```

### 3. Prompt Engineering

```python
# Be specific and clear
good_prompt = """
Extract product information from this title:
"Dell Latitude 5420 14\" Laptop i5 16GB RAM 256GB SSD"

Return JSON with these fields:
- brand (string)
- model (string)
- screen_size (number, in inches)
- processor (string)
- ram (number, in GB)
- storage (number, in GB)
"""

# Avoid vague prompts
bad_prompt = "Tell me about this laptop"
```

### 4. Response Validation

```python
import json
from pydantic import BaseModel, ValidationError

class ProductMetadata(BaseModel):
    brand: str
    model: str
    category: str

async def validated_extraction(product_title: str) -> ProductMetadata:
    """Extract metadata with validation."""
    response = await client.complete(
        model="meta-llama/llama-3.1-8b-instruct:free",
        messages=[{
            "role": "user",
            "content": f"Extract metadata from: {product_title}. Return JSON."
        }]
    )
    
    try:
        data = json.loads(response.choices[0].message.content)
        return ProductMetadata(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Invalid response: {e}")
        raise
```

### 5. Caching

```python
from functools import lru_cache
import hashlib

def cache_key(model: str, prompt: str) -> str:
    """Generate cache key."""
    return hashlib.sha256(f"{model}:{prompt}".encode()).hexdigest()

# In-memory cache
_completion_cache = {}

async def cached_complete(model: str, prompt: str, ttl: int = 3600):
    """Complete with caching."""
    key = cache_key(model, prompt)
    
    # Check cache
    if key in _completion_cache:
        cached, timestamp = _completion_cache[key]
        if time.time() - timestamp < ttl:
            return cached
    
    # Call API
    response = await client.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Store in cache
    _completion_cache[key] = (response, time.time())
    
    return response
```

---

## Examples

### Example 1: Product Metadata Extraction

```python
async def extract_product_metadata(title: str, description: str = ""):
    """Extract product metadata."""
    client = get_client()
    
    prompt = f"""
    Extract structured product information:
    
    Title: {title}
    Description: {description}
    
    Return JSON with:
    - brand: string
    - model: string  
    - category: string (from: electronics, clothing, home, sports, other)
    - condition: string (new, like-new, good, fair, poor)
    - specifications: object (key specs)
    - keywords: array of strings (for SEO)
    """
    
    response = await client.complete(
        model="meta-llama/llama-3.1-8b-instruct:free",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=800
    )
    
    return json.loads(response.choices[0].message.content)
```

### Example 2: SEO-Optimized Title Generation

```python
async def generate_seo_title(product_data: dict, platform: str = "ebay"):
    """Generate SEO-optimized listing title."""
    client = get_client()
    
    prompt = f"""
    Generate an SEO-optimized {platform} listing title for:
    
    {json.dumps(product_data, indent=2)}
    
    Requirements:
    - Include brand, model, key specs
    - Add relevant keywords
    - eBay limit: 80 characters
    - Mercari limit: 40 characters
    - Include condition if not new
    
    Return only the title, no explanations.
    """
    
    response = await client.complete(
        model="openai/gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=100
    )
    
    return response.choices[0].message.content.strip()
```

### Example 3: Market Analysis

```python
async def analyze_market_trends(product_category: str, comparables: List[dict]):
    """Analyze market trends for pricing."""
    client = get_client()
    
    prompt = f"""
    Analyze market trends for {product_category}:
    
    Recent sold prices:
    {json.dumps(comparables, indent=2)}
    
    Provide:
    1. Average and median prices
    2. Price trend (rising, stable, falling)
    3. Recommended pricing strategy
    4. Best time to list
    5. Market velocity (how fast items sell)
    
    Return as JSON.
    """
    
    response = await client.complete(
        model="anthropic/claude-3.5-sonnet",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000
    )
    
    return json.loads(response.choices[0].message.content)
```

---

## Monitoring and Debugging

### Enable Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("openrouter")

# Log all API calls
client = OpenRouterClient()
client.client.event_hooks = {
    "request": [lambda request: logger.debug(f"Request: {request.url}")],
    "response": [lambda response: logger.debug(f"Response: {response.status_code}")]
}
```

### Track Usage

```python
class UsageTracker:
    """Track OpenRouter API usage."""
    
    def __init__(self):
        self.total_tokens = 0
        self.total_requests = 0
        self.cost = 0.0
    
    def record(self, response: CompletionResponse):
        """Record usage from response."""
        self.total_tokens += response.usage.total_tokens
        self.total_requests += 1
        # Calculate cost based on model pricing
        # (OpenRouter provides this in response)
    
    def report(self):
        """Generate usage report."""
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "estimated_cost": self.cost
        }
```

---

## Troubleshooting

### Common Issues

**1. API Key Invalid**
```python
# Error: 401 Unauthorized
# Solution: Check API key is set correctly
print(os.getenv("OPENROUTER_API_KEY"))
```

**2. Rate Limiting**
```python
# Error: 429 Too Many Requests
# Solution: Implement exponential backoff
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=1, min=4, max=60))
async def rate_limited_complete(...):
    return await client.complete(...)
```

**3. Model Not Found**
```python
# Error: Model 'xyz' not found
# Solution: List available models
models = await client.list_models()
print([m['id'] for m in models])
```

---

**Related Documentation**:
- [Agents Architecture](AGENTS.md)
- [SRS](SRS.md)
- [Observability](OBSERVABILITY.md)

**External Links**:
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [OpenRouter Models](https://openrouter.ai/models)

**Last Updated**: 2025-12-15  
**Maintained By**: AI Team
