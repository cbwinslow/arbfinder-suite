"""
OpenRouter Completion Functions

High-level convenience functions for text and code completion tasks.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from .client import OpenRouterClient


@dataclass
class CompletionOptions:
    """Options for completion requests."""

    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None


async def complete_text(
    prompt: str,
    model: str = "openrouter/anthropic/claude-instant-v1",
    options: Optional[CompletionOptions] = None,
    client: Optional[OpenRouterClient] = None,
) -> str:
    """Complete text with default settings optimized for general use.

    Args:
        prompt: Input prompt
        model: Model to use
        options: Completion options
        client: Optional existing client

    Returns:
        Completed text string

    Example:
        text = await complete_text("Write a product description for...")
    """
    if options is None:
        options = CompletionOptions()

    if client is None:
        client = OpenRouterClient()

    try:
        response = await client.complete(
            prompt=prompt,
            model=model,
            temperature=options.temperature,
            max_tokens=options.max_tokens,
            top_p=options.top_p,
            frequency_penalty=options.frequency_penalty,
            presence_penalty=options.presence_penalty,
            stop=options.stop,
        )
        return response.content
    finally:
        if client:
            await client.close()


async def complete_code(
    prompt: str,
    language: str = "python",
    model: str = "openrouter/deepseek/deepseek-coder",
    options: Optional[CompletionOptions] = None,
    client: Optional[OpenRouterClient] = None,
) -> str:
    """Complete code with settings optimized for code generation.

    Args:
        prompt: Code prompt
        language: Programming language
        model: Model to use (defaults to code-specialized model)
        options: Completion options
        client: Optional existing client

    Returns:
        Generated code string

    Example:
        code = await complete_code(
            "def calculate_profit(price, cost):",
            language="python"
        )
    """
    if options is None:
        # Code generation works better with lower temperature
        options = CompletionOptions(temperature=0.2, max_tokens=2000)

    # Add language context to prompt
    full_prompt = f"```{language}\n{prompt}\n```\n\nComplete the code:"

    return await complete_text(full_prompt, model, options, client)


async def complete_chat(
    messages: List[Dict[str, str]],
    model: str = "openrouter/anthropic/claude-instant-v1",
    options: Optional[CompletionOptions] = None,
    client: Optional[OpenRouterClient] = None,
) -> str:
    """Complete chat conversation.

    Args:
        messages: List of chat messages
        model: Model to use
        options: Completion options
        client: Optional existing client

    Returns:
        Assistant response string

    Example:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
        response = await complete_chat(messages)
    """
    if options is None:
        options = CompletionOptions()

    if client is None:
        client = OpenRouterClient()

    try:
        response = await client.chat(
            messages=messages,
            model=model,
            temperature=options.temperature,
            max_tokens=options.max_tokens,
        )
        return response.content
    finally:
        if client:
            await client.close()
