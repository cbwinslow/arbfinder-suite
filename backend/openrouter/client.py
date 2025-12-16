"""
OpenRouter API Client

Comprehensive async client for OpenRouter API with retry logic,
error handling, and cost tracking.
"""

import logging
import os
import time
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, List, Optional

try:
    import httpx
    from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
except ImportError:
    print("Missing dependencies. Install with: pip install httpx tenacity")
    raise

logger = logging.getLogger(__name__)


# Custom exceptions
class OpenRouterError(Exception):
    """Base exception for OpenRouter errors."""


class RateLimitError(OpenRouterError):
    """Raised when rate limit is exceeded."""


class AuthenticationError(OpenRouterError):
    """Raised when authentication fails."""


class ModelNotFoundError(OpenRouterError):
    """Raised when model is not found."""


@dataclass
class Usage:
    """Token usage information."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float = 0.0


@dataclass
class CompletionResponse:
    """Completion response from OpenRouter."""

    id: str
    model: str
    content: str
    finish_reason: str
    usage: Usage
    created_at: float


class OpenRouterClient:
    """Async client for OpenRouter API."""

    API_BASE = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3,
        app_name: str = "ArbFinder Suite",
        app_url: str = "https://github.com/cbwinslow/arbfinder-suite",
    ):
        """Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
            base_url: API base URL (default: https://openrouter.ai/api/v1)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            app_name: Application name for X-Title header
            app_url: Application URL for HTTP-Referer header
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.base_url = base_url or self.API_BASE
        self.timeout = timeout
        self.max_retries = max_retries
        self.app_name = app_name
        self.app_url = app_url

        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": self.app_url,
                "X-Title": self.app_name,
                "Content-Type": "application/json",
            },
        )

        # Track usage stats
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost = 0.0

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, RateLimitError)),
    )
    async def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict] = None, stream: bool = False
    ) -> Any:
        """Make HTTP request to OpenRouter API.

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint path
            data: Request body data
            stream: Whether to stream response

        Returns:
            Response data or stream iterator

        Raises:
            OpenRouterError: If request fails
            RateLimitError: If rate limit exceeded
            AuthenticationError: If authentication fails
        """
        url = f"{self.base_url}{endpoint}"

        try:
            if stream:
                return await self.client.stream(method, url, json=data)

            response = await self.client.request(method, url, json=data)
            response.raise_for_status()

            result = response.json()

            # Check for API errors
            if "error" in result:
                error_msg = result["error"].get("message", str(result["error"]))
                error_code = result["error"].get("code", "unknown")

                if error_code == "rate_limit_exceeded":
                    raise RateLimitError(error_msg)
                elif error_code in ("invalid_api_key", "insufficient_quota"):
                    raise AuthenticationError(error_msg)
                else:
                    raise OpenRouterError(f"{error_code}: {error_msg}")

            self.total_requests += 1
            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            else:
                raise OpenRouterError(f"HTTP {e.response.status_code}: {e}")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise OpenRouterError(f"Request failed: {e}")

    async def complete(
        self,
        prompt: str,
        model: str = "openrouter/anthropic/claude-instant-v1",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[List[str]] = None,
        **kwargs,
    ) -> CompletionResponse:
        """Generate completion for a prompt.

        Args:
            prompt: Input prompt text
            model: Model identifier
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2 to 2)
            presence_penalty: Presence penalty (-2 to 2)
            stop: Stop sequences
            **kwargs: Additional parameters

        Returns:
            CompletionResponse object

        Raises:
            OpenRouterError: If request fails
        """
        data = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
        }

        if stop:
            data["stop"] = stop

        # Add any additional parameters
        data.update(kwargs)

        response = await self._make_request("POST", "/completions", data=data)

        # Parse response
        choice = response["choices"][0]
        usage = response.get("usage", {})

        usage_obj = Usage(
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            cost=usage.get("cost", 0.0),
        )

        self.total_tokens += usage_obj.total_tokens
        self.total_cost += usage_obj.cost

        return CompletionResponse(
            id=response.get("id", ""),
            model=response.get("model", model),
            content=choice.get("text", ""),
            finish_reason=choice.get("finish_reason", ""),
            usage=usage_obj,
            created_at=response.get("created", time.time()),
        )

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "openrouter/anthropic/claude-instant-v1",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs,
    ) -> CompletionResponse:
        """Generate chat completion.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            CompletionResponse object

        Example:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"}
            ]
            response = await client.chat(messages)
        """
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        data.update(kwargs)

        response = await self._make_request("POST", "/chat/completions", data=data)

        # Parse response
        choice = response["choices"][0]
        usage = response.get("usage", {})

        usage_obj = Usage(
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            cost=usage.get("cost", 0.0),
        )

        self.total_tokens += usage_obj.total_tokens
        self.total_cost += usage_obj.cost

        return CompletionResponse(
            id=response.get("id", ""),
            model=response.get("model", model),
            content=choice.get("message", {}).get("content", ""),
            finish_reason=choice.get("finish_reason", ""),
            usage=usage_obj,
            created_at=response.get("created", time.time()),
        )

    async def stream(
        self,
        prompt: str,
        model: str = "openrouter/anthropic/claude-instant-v1",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream completion tokens as they're generated.

        Args:
            prompt: Input prompt text
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Yields:
            Token strings as they're generated

        Example:
            async for token in client.stream("Write a story"):
                print(token, end="", flush=True)
        """
        data = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        data.update(kwargs)

        async with await self._make_request(
            "POST", "/completions", data=data, stream=True
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]  # Remove "data: " prefix

                    if data_str == "[DONE]":
                        break

                    try:
                        import json

                        chunk = json.loads(data_str)

                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            choice = chunk["choices"][0]
                            text = choice.get("text", "")
                            if text:
                                yield text
                    except json.JSONDecodeError:
                        continue

    async def get_models(self) -> List[Dict[str, Any]]:
        """Get list of available models.

        Returns:
            List of model dictionaries with metadata
        """
        response = await self._make_request("GET", "/models")
        return response.get("data", [])

    async def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics for current API key.

        Returns:
            Dictionary with usage statistics
        """
        response = await self._make_request("GET", "/generation")
        return response.get("data", {})

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get local usage statistics.

        Returns:
            Dictionary with request count, tokens, and cost
        """
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "avg_tokens_per_request": (
                self.total_tokens / self.total_requests if self.total_requests > 0 else 0
            ),
            "avg_cost_per_request": (
                self.total_cost / self.total_requests if self.total_requests > 0 else 0
            ),
        }


# Convenience functions


async def get_client(api_key: Optional[str] = None) -> OpenRouterClient:
    """Get OpenRouter client instance.

    Args:
        api_key: Optional API key

    Returns:
        Configured OpenRouterClient
    """
    return OpenRouterClient(api_key=api_key)
