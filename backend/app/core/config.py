import os
from dataclasses import dataclass


ALLOWED_LLM_PROVIDERS = ("mock", "openai")
ALLOWED_OPENAI_MODELS = ("gpt-5.4-nano", "gpt-5.4-mini")

DEFAULT_LLM_PROVIDER = "mock"
DEFAULT_OPENAI_MODEL = "gpt-5.4-nano"
DEFAULT_OPENAI_MAX_OUTPUT_TOKENS = 1200
DEFAULT_OPENAI_TIMEOUT_SECONDS = 30


class ConfigError(ValueError):
    """Raised when environment configuration is invalid."""


@dataclass(frozen=True)
class AppSettings:
    llm_provider: str
    openai_api_key: str | None
    openai_model: str
    openai_max_output_tokens: int
    openai_timeout_seconds: int


def get_settings() -> AppSettings:
    provider = _get_env_value("APP_LLM_PROVIDER", DEFAULT_LLM_PROVIDER).lower()
    if provider not in ALLOWED_LLM_PROVIDERS:
        allowed = ", ".join(ALLOWED_LLM_PROVIDERS)
        raise ConfigError(
            f"Unsupported APP_LLM_PROVIDER: {provider}. Allowed values: {allowed}."
        )

    model = _get_env_value("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    if model not in ALLOWED_OPENAI_MODELS:
        allowed = ", ".join(ALLOWED_OPENAI_MODELS)
        raise ConfigError(
            f"Unsupported OPENAI_MODEL: {model}. Allowed values: {allowed}."
        )

    max_output_tokens = _get_positive_int_env(
        "OPENAI_MAX_OUTPUT_TOKENS",
        DEFAULT_OPENAI_MAX_OUTPUT_TOKENS,
    )
    timeout_seconds = _get_positive_int_env(
        "OPENAI_TIMEOUT_SECONDS",
        DEFAULT_OPENAI_TIMEOUT_SECONDS,
    )

    return AppSettings(
        llm_provider=provider,
        openai_api_key=_get_optional_env_value("OPENAI_API_KEY"),
        openai_model=model,
        openai_max_output_tokens=max_output_tokens,
        openai_timeout_seconds=timeout_seconds,
    )


def ensure_openai_ready(settings: AppSettings) -> None:
    if _is_missing_api_key(settings.openai_api_key):
        raise ConfigError("OPENAI_API_KEY is required when APP_LLM_PROVIDER=openai.")


def _get_env_value(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default

    return value.strip()


def _get_optional_env_value(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None

    stripped_value = value.strip()
    return stripped_value or None


def _get_positive_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default

    try:
        parsed_value = int(value)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a positive integer.") from exc

    if parsed_value <= 0:
        raise ConfigError(f"{name} must be a positive integer.")

    return parsed_value


def _is_missing_api_key(api_key: str | None) -> bool:
    if api_key is None:
        return True

    return api_key in {"your_openai_api_key_here", "CHANGE_ME"}
