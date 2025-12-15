"""
OpenRouter Utility Functions

Helper functions for token counting, cost estimation, and text processing.
"""

import re
from typing import Dict, Any, Optional


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Estimate token count for text.
    
    This is a rough estimation. For accurate counts, use tiktoken library.
    
    Args:
        text: Text to count tokens for
        model: Model name for tokenizer selection
        
    Returns:
        Estimated token count
    """
    # Rough estimation: ~4 characters per token on average
    return len(text) // 4


def estimate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model_pricing: Dict[str, float]
) -> float:
    """Estimate cost for a completion request.
    
    Args:
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        model_pricing: Pricing dict with 'prompt' and 'completion' keys
        
    Returns:
        Estimated cost in USD
    """
    prompt_cost = float(model_pricing.get("prompt", 0)) * prompt_tokens / 1_000_000
    completion_cost = float(model_pricing.get("completion", 0)) * completion_tokens / 1_000_000
    return prompt_cost + completion_cost


def format_prompt(
    template: str,
    variables: Dict[str, Any]
) -> str:
    """Format prompt template with variables.
    
    Args:
        template: Prompt template with {variable} placeholders
        variables: Dictionary of variable values
        
    Returns:
        Formatted prompt string
        
    Example:
        template = "Write a description for {product} priced at ${price}"
        variables = {"product": "iPad", "price": 299.99}
        prompt = format_prompt(template, variables)
    """
    return template.format(**variables)


def parse_response(response: str, format: str = "text") -> Any:
    """Parse completion response into desired format.
    
    Args:
        response: Raw response text
        format: Desired format ('text', 'json', 'code')
        
    Returns:
        Parsed response
    """
    if format == "text":
        return response.strip()
    
    elif format == "json":
        import json
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            response = json_match.group(1)
        return json.loads(response)
    
    elif format == "code":
        # Extract code from markdown code blocks
        code_match = re.search(r'```(?:\w+)?\s*(.*?)\s*```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        return response.strip()
    
    return response


def truncate_text(text: str, max_tokens: int = 1000) -> str:
    """Truncate text to fit within token limit.
    
    Args:
        text: Text to truncate
        max_tokens: Maximum tokens
        
    Returns:
        Truncated text
    """
    estimated_tokens = count_tokens(text)
    if estimated_tokens <= max_tokens:
        return text
    
    # Truncate to estimated character count
    max_chars = max_tokens * 4
    return text[:max_chars] + "..."


def split_into_chunks(
    text: str,
    chunk_size: int = 2000,
    overlap: int = 200
) -> list[str]:
    """Split text into overlapping chunks.
    
    Args:
        text: Text to split
        chunk_size: Maximum tokens per chunk
        overlap: Token overlap between chunks
        
    Returns:
        List of text chunks
    """
    max_chars = chunk_size * 4
    overlap_chars = overlap * 4
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap_chars
    
    return chunks
