"""LLM model registry with pre-initialized instances."""

from typing import (
    Any,
    Dict,
    List,
    cast,
)

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.core.config import settings
from app.core.logging import logger

_API_KEY = SecretStr(settings.OPENAI_API_KEY)
_BASE_URL = settings.OPENAI_BASE_URL


class LLMRegistry:
    """Registry of available LLM models with pre-initialized instances."""

    LLMS: List[Dict[str, Any]] = [
        {
            "name": "deepseek-chat",
            "llm": ChatOpenAI(
                model="deepseek-chat",
                api_key=_API_KEY,
                base_url=_BASE_URL,
                temperature=settings.DEFAULT_LLM_TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
            ),
        },
        {
            "name": "deepseek-reasoner",
            "llm": ChatOpenAI(
                model="deepseek-reasoner",
                api_key=_API_KEY,
                base_url=_BASE_URL,
                temperature=settings.DEFAULT_LLM_TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
            ),
        },
    ]

    @classmethod
    def get(cls, model_name: str, **kwargs) -> BaseChatModel:
        """Get an LLM by name with optional argument overrides."""
        model_entry = next((e for e in cls.LLMS if e["name"] == model_name), None)

        if not model_entry:
            available = ", ".join(e["name"] for e in cls.LLMS)
            raise ValueError(f"model '{model_name}' not found in registry. available models: {available}")

        if kwargs:
            base_llm = cast(ChatOpenAI, model_entry["llm"])
            logger.debug(
                "creating_llm_with_custom_args",
                model_name=model_name,
                model=base_llm.model_name,
                custom_args=list(kwargs.keys()),
            )
            return ChatOpenAI(
                model=base_llm.model_name,
                api_key=_API_KEY,
                base_url=_BASE_URL,
                max_tokens=settings.MAX_TOKENS,
                **kwargs,
            )

        logger.debug("using_default_llm_instance", model_name=model_name)
        return model_entry["llm"]

    @classmethod
    def get_all_names(cls) -> List[str]:
        """Return all registered model names in order."""
        return [e["name"] for e in cls.LLMS]

    @classmethod
    def get_model_at_index(cls, index: int) -> Dict[str, Any]:
        """Return the model entry at a specific index, wrapping to 0 if out of range."""
        if 0 <= index < len(cls.LLMS):
            return cls.LLMS[index]
        return cls.LLMS[0]
