"""
OpenRouter SDK Integration for ArbFinder Suite

This package provides a comprehensive wrapper around the OpenRouter API,
offering easy access to 100+ LLM models with features like:
- Free model discovery
- Automatic fallback chains
- Cost tracking
- Streaming support
- Code completion
- Retry logic with exponential backoff

Usage:
    from backend.openrouter import OpenRouterClient, get_free_models
    
    client = OpenRouterClient(api_key="your-key")
    
    # Get free models
    free_models = await get_free_models()
    
    # Generate completion
    response = await client.complete(
        prompt="Write a product description for...",
        model="openrouter/anthropic/claude-instant-v1"
    )
    
    # Stream response
    async for chunk in client.stream(prompt="...", model="..."):
        print(chunk, end="", flush=True)
"""

from .client import OpenRouterClient, OpenRouterError, RateLimitError
from .models import get_free_models, get_all_models, ModelInfo
from .completion import (
    complete_text,
    complete_code,
    complete_chat,
    CompletionOptions
)
from .streaming import stream_completion, StreamChunk
from .utils import (
    count_tokens,
    estimate_cost,
    format_prompt,
    parse_response
)

__version__ = "2.0.0"
__all__ = [
    # Client
    "OpenRouterClient",
    "OpenRouterError",
    "RateLimitError",
    
    # Models
    "get_free_models",
    "get_all_models",
    "ModelInfo",
    
    # Completion
    "complete_text",
    "complete_code",
    "complete_chat",
    "CompletionOptions",
    
    # Streaming
    "stream_completion",
    "StreamChunk",
    
    # Utils
    "count_tokens",
    "estimate_cost",
    "format_prompt",
    "parse_response",
]
