from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://koinos:password@localhost:5433/koinos_db"

    # LLM Configuration — provider-agnostic
    llm_provider: str = "groq"           # "groq", "openai", "anthropic", "google"
    llm_api_key: str = ""                # Universal API key field
    llm_model_name: str = "llama-3.1-8b-instant"
    llm_temperature: float = 0.0

    # Legacy alias — still works if GROQ_API_KEY is set in .env
    groq_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
