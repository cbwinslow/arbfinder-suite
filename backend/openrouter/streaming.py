"""
OpenRouter Streaming Support

Functions for streaming completion responses token-by-token.
"""

from typing import AsyncIterator, Optional
from dataclasses import dataclass

from .client import OpenRouterClient


@dataclass
class StreamChunk:
    """Streaming chunk data."""
    text: str
    is_final: bool = False


async def stream_completion(
    prompt: str,
    model: str = "openrouter/anthropic/claude-instant-v1",
    temperature: float = 0.7,
    max_tokens: int = 1000,
    client: Optional[OpenRouterClient] = None
) -> AsyncIterator[StreamChunk]:
    """Stream completion tokens as they're generated.
    
    Args:
        prompt: Input prompt
        model: Model to use
        temperature: Sampling temperature
        max_tokens: Maximum tokens
        client: Optional existing client
        
    Yields:
        StreamChunk objects with text tokens
        
    Example:
        async for chunk in stream_completion("Write a story about..."):
            print(chunk.text, end="", flush=True)
    """
    if client is None:
        client = OpenRouterClient()
    
    try:
        async for token in client.stream(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        ):
            yield StreamChunk(text=token, is_final=False)
        
        # Yield final chunk
        yield StreamChunk(text="", is_final=True)
        
    finally:
        if client:
            await client.close()
