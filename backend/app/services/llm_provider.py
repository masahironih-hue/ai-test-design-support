from app.core.config import ConfigError, get_settings
from app.models.test_design import (
    TestDesignGenerateRequest,
    TestDesignGenerateResponse,
)
from app.services.llm_errors import LLMConfigurationError
from app.services.llm_mock import generate_test_design_mock
from app.services.llm_openai import generate_test_design_openai


def generate_test_design(
    request: TestDesignGenerateRequest,
) -> TestDesignGenerateResponse:
    try:
        settings = get_settings()
    except ConfigError as exc:
        raise LLMConfigurationError(str(exc)) from exc

    if settings.llm_provider == "mock":
        return generate_test_design_mock(request)

    if settings.llm_provider == "openai":
        return generate_test_design_openai(request, settings=settings)

    raise LLMConfigurationError(
        "Unsupported APP_LLM_PROVIDER. Allowed values: mock, openai."
    )
