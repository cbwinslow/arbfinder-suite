"""
OpenRouter Models Management

Functions for discovering, filtering, and managing OpenRouter models,
with a focus on identifying free models for cost optimization.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .client import OpenRouterClient

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """Model information dataclass."""

    id: str
    name: str
    description: str
    pricing: Dict[str, float]
    context_length: int
    architecture: Optional[str] = None
    top_provider: Optional[str] = None
    is_free: bool = False
    is_moderated: bool = False


async def get_all_models(client: Optional[OpenRouterClient] = None) -> List[ModelInfo]:
    """Get all available models from OpenRouter.

    Args:
        client: Optional OpenRouterClient instance

    Returns:
        List of ModelInfo objects
    """
    if client is None:
        client = OpenRouterClient()

    try:
        models_data = await client.get_models()

        models = []
        for model_dict in models_data:
            pricing = model_dict.get("pricing", {})

            # Check if model is free (both prompt and completion are $0)
            is_free = (
                float(pricing.get("prompt", "0")) == 0.0
                and float(pricing.get("completion", "0")) == 0.0
            )

            model_info = ModelInfo(
                id=model_dict.get("id", ""),
                name=model_dict.get("name", ""),
                description=model_dict.get("description", ""),
                pricing=pricing,
                context_length=model_dict.get("context_length", 0),
                architecture=model_dict.get("architecture", {}).get("tokenizer"),
                top_provider=model_dict.get("top_provider", {}).get("name"),
                is_free=is_free,
                is_moderated=model_dict.get("is_moderated", False),
            )
            models.append(model_info)

        return models

    except Exception as e:
        logger.error(f"Failed to fetch models: {e}")
        return []
    finally:
        if client:
            await client.close()


async def get_free_models(
    client: Optional[OpenRouterClient] = None, min_context_length: int = 2000
) -> List[ModelInfo]:
    """Get all free models from OpenRouter.

    Args:
        client: Optional OpenRouterClient instance
        min_context_length: Minimum context length (tokens)

    Returns:
        List of free ModelInfo objects

    Example:
        free_models = await get_free_models()
        for model in free_models:
            print(f"{model.name}: {model.context_length} tokens")
    """
    all_models = await get_all_models(client)

    free_models = [
        model
        for model in all_models
        if model.is_free and model.context_length >= min_context_length
    ]

    # Sort by context length (descending)
    free_models.sort(key=lambda m: m.context_length, reverse=True)

    logger.info(f"Found {len(free_models)} free models")
    return free_models


async def get_model_by_id(
    model_id: str, client: Optional[OpenRouterClient] = None
) -> Optional[ModelInfo]:
    """Get specific model by ID.

    Args:
        model_id: Model identifier
        client: Optional OpenRouterClient instance

    Returns:
        ModelInfo object or None if not found
    """
    all_models = await get_all_models(client)

    for model in all_models:
        if model.id == model_id:
            return model

    return None


async def recommend_model(
    task_type: str = "general",
    max_cost: float = 0.0,
    min_context: int = 2000,
    client: Optional[OpenRouterClient] = None,
) -> Optional[ModelInfo]:
    """Recommend a model based on task requirements.

    Args:
        task_type: Type of task ('general', 'code', 'chat', 'analysis')
        max_cost: Maximum cost per 1M tokens (0.0 for free only)
        min_context: Minimum context length required
        client: Optional OpenRouterClient instance

    Returns:
        Recommended ModelInfo or None

    Example:
        model = await recommend_model(task_type="code", max_cost=0.0)
        print(f"Use model: {model.id}")
    """
    all_models = await get_all_models(client)

    # Filter by cost and context
    candidates = [model for model in all_models if model.context_length >= min_context]

    if max_cost == 0.0:
        candidates = [m for m in candidates if m.is_free]
    else:
        candidates = [m for m in candidates if float(m.pricing.get("prompt", "999")) <= max_cost]

    if not candidates:
        logger.warning("No models match criteria")
        return None

    # Task-specific preferences
    task_preferences = {
        "general": ["claude", "gpt", "llama"],
        "code": ["codellama", "deepseek", "claude", "gpt"],
        "chat": ["claude", "gpt", "llama", "mistral"],
        "analysis": ["claude", "gpt-4", "llama"],
    }

    preferred_keywords = task_preferences.get(task_type, ["claude", "gpt"])

    # Score models based on preferences
    scored_models = []
    for model in candidates:
        score = model.context_length / 1000  # Base score on context length

        # Bonus for preferred models
        model_id_lower = model.id.lower()
        for keyword in preferred_keywords:
            if keyword in model_id_lower:
                score += 1000
                break

        # Bonus for free models
        if model.is_free:
            score += 500

        scored_models.append((score, model))

    # Sort by score and return best
    scored_models.sort(key=lambda x: x[0], reverse=True)

    recommended = scored_models[0][1]
    logger.info(
        f"Recommended model: {recommended.id} "
        f"(context: {recommended.context_length}, free: {recommended.is_free})"
    )

    return recommended


async def compare_models(
    model_ids: List[str], client: Optional[OpenRouterClient] = None
) -> Dict[str, Any]:
    """Compare multiple models side by side.

    Args:
        model_ids: List of model IDs to compare
        client: Optional OpenRouterClient instance

    Returns:
        Dictionary with comparison data

    Example:
        comparison = await compare_models([
            "openrouter/anthropic/claude-instant-v1",
            "openrouter/openai/gpt-3.5-turbo"
        ])
    """
    all_models = await get_all_models(client)
    models_map = {m.id: m for m in all_models}

    comparison = {
        "models": [],
        "metrics": {
            "avg_context_length": 0,
            "total_free": 0,
            "cheapest_prompt": None,
            "cheapest_completion": None,
        },
    }

    total_context = 0
    min_prompt_cost = float("inf")
    min_completion_cost = float("inf")
    cheapest_prompt_model = None
    cheapest_completion_model = None

    for model_id in model_ids:
        if model_id not in models_map:
            logger.warning(f"Model not found: {model_id}")
            continue

        model = models_map[model_id]
        comparison["models"].append(
            {
                "id": model.id,
                "name": model.name,
                "context_length": model.context_length,
                "pricing": model.pricing,
                "is_free": model.is_free,
            }
        )

        total_context += model.context_length

        if model.is_free:
            comparison["metrics"]["total_free"] += 1

        prompt_cost = float(model.pricing.get("prompt", "999"))
        if prompt_cost < min_prompt_cost:
            min_prompt_cost = prompt_cost
            cheapest_prompt_model = model.id

        completion_cost = float(model.pricing.get("completion", "999"))
        if completion_cost < min_completion_cost:
            min_completion_cost = completion_cost
            cheapest_completion_model = model.id

    if comparison["models"]:
        comparison["metrics"]["avg_context_length"] = total_context / len(comparison["models"])
        comparison["metrics"]["cheapest_prompt"] = cheapest_prompt_model
        comparison["metrics"]["cheapest_completion"] = cheapest_completion_model

    return comparison


# Cached free models list (24 hour TTL)
_free_models_cache = None
_cache_timestamp = 0


async def get_free_models_cached(ttl: int = 86400) -> List[ModelInfo]:
    """Get free models with caching.

    Args:
        ttl: Time to live for cache in seconds (default: 24 hours)

    Returns:
        List of free ModelInfo objects
    """
    global _free_models_cache, _cache_timestamp

    import time

    current_time = time.time()

    if _free_models_cache is None or current_time - _cache_timestamp > ttl:
        logger.info("Refreshing free models cache")
        _free_models_cache = await get_free_models()
        _cache_timestamp = current_time

    return _free_models_cache


# Convenience function for getting model IDs only
async def get_free_model_ids() -> List[str]:
    """Get list of free model IDs.

    Returns:
        List of model ID strings
    """
    models = await get_free_models_cached()
    return [model.id for model in models]


# Example usage
if __name__ == "__main__":

    async def main():
        # Get all free models
        free_models = await get_free_models()

        print(f"Found {len(free_models)} free models:\n")
        for model in free_models[:10]:  # Show first 10
            print(f"  {model.name}")
            print(f"    ID: {model.id}")
            print(f"    Context: {model.context_length} tokens")
            print()

        # Recommend a model for code generation
        recommended = await recommend_model(task_type="code", max_cost=0.0)
        if recommended:
            print(f"\nRecommended model for code: {recommended.id}")

    asyncio.run(main())
