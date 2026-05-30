from typing import Any

from app.core.config import AppSettings, ConfigError, ensure_openai_ready, get_settings
from app.models.test_design import (
    TestDesignGenerateRequest,
    TestDesignGenerateResponse,
)
from app.services.llm_errors import (
    LLMConfigurationError,
    LLMProviderAPIError,
    LLMProviderTimeoutError,
    LLMResponseError,
)
from app.services.llm_mock import generate_test_design_mock
from app.services.prompt_builder import build_test_design_prompt


def generate_test_design_openai(
    request: TestDesignGenerateRequest,
    settings: AppSettings | None = None,
) -> TestDesignGenerateResponse:
    settings = settings or get_settings()

    try:
        ensure_openai_ready(settings)
    except ConfigError as exc:
        raise LLMConfigurationError(str(exc)) from exc

    prompt = build_test_design_prompt(request)
    client = _create_openai_client(settings)

    try:
        response = client.responses.create(
            model=settings.openai_model,
            input=prompt,
            max_output_tokens=settings.openai_max_output_tokens,
        )
    except Exception as exc:
        if _is_exception_named(exc, "APITimeoutError") or isinstance(
            exc, TimeoutError
        ):
            raise LLMProviderTimeoutError("OpenAI API request timed out.") from exc

        raise LLMProviderAPIError(
            "OpenAI API request failed. Check the API key, model access, rate limits, and network."
        ) from exc

    markdown = _extract_output_text(response)
    base_response = generate_test_design_mock(request)

    return TestDesignGenerateResponse(
        title=request.title,
        target_type=request.target_type,
        test_level=request.test_level,
        viewpoints=base_response.viewpoints,
        test_cases=base_response.test_cases,
        markdown=markdown,
    )


def _create_openai_client(settings: AppSettings) -> Any:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise LLMConfigurationError(
            "OpenAI SDK is not installed. Install backend dependencies before using APP_LLM_PROVIDER=openai."
        ) from exc

    return OpenAI(
        api_key=settings.openai_api_key,
        timeout=float(settings.openai_timeout_seconds),
        max_retries=0,
    )


def _extract_output_text(response: Any) -> str:
    try:
        output_text = getattr(response, "output_text", None)
    except Exception as exc:
        fallback_text = _extract_text_from_output_items(response)
        if fallback_text:
            return fallback_text

        raise LLMResponseError("OpenAI response text could not be read.") from exc

    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    fallback_text = _extract_text_from_output_items(response)
    if fallback_text:
        return fallback_text

    raise LLMResponseError("OpenAI response did not contain readable text output.")


def _extract_text_from_output_items(response: Any) -> str | None:
    output_items = getattr(response, "output", None)
    if not output_items:
        return None

    texts: list[str] = []

    for output_item in output_items:
        content_items = _get_value(output_item, "content")
        if not content_items:
            continue

        for content_item in content_items:
            text = _get_value(content_item, "text")
            if isinstance(text, str) and text.strip():
                texts.append(text.strip())

    if not texts:
        return None

    return "\n\n".join(texts)


def _get_value(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        return value.get(key)

    return getattr(value, key, None)


def _is_exception_named(exc: Exception, class_name: str) -> bool:
    return any(cls.__name__ == class_name for cls in type(exc).mro())
