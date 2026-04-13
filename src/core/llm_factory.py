"""
LLM Factory — Swap providers by changing LLM_PROVIDER in .env

Supported providers:
    groq      → pip install langchain-groq
    openai    → pip install langchain-openai
    anthropic → pip install langchain-anthropic
    google    → pip install langchain-google-genai
"""
from langchain_core.language_models.chat_models import BaseChatModel
from src.core.config import settings


def get_llm() -> BaseChatModel:
    """
    Factory that returns the correct ChatModel based on settings.llm_provider.
    Only the selected provider's package needs to be installed.
    """
    provider = settings.llm_provider.lower()
    api_key = settings.llm_api_key or settings.groq_api_key  # fallback for legacy .env
    model = settings.llm_model_name
    temperature = settings.llm_temperature

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model,
            temperature=temperature,
            api_key=api_key or None,  # None lets it fall back to GROQ_API_KEY env var
        )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key or None,
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=api_key or None,
        )

    elif provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=api_key or None,
        )

    else:
        supported = ["groq", "openai", "anthropic", "google"]
        raise ValueError(
            f"Unsupported LLM provider: '{provider}'. "
            f"Supported providers: {supported}"
        )
