from types import SimpleNamespace

import pytest

from app.core.config import get_settings
from app.models.test_design import (
    TestDesignGenerateRequest as GenerateRequest,
    TestDesignGenerateResponse as GenerateResponse,
)
from app.services import llm_openai, llm_provider
from app.services.llm_errors import (
    LLMConfigurationError,
    LLMProviderTimeoutError,
)


def _valid_request() -> GenerateRequest:
    return GenerateRequest(
        title="架空の在庫引当API",
        target_type="api",
        test_level="integration",
        spec_text="商品IDと数量を受け取り、在庫引当を行う架空のAPI。",
        supplement="外部倉庫システムとの連携はMockとする。",
    )


def _fake_response(markdown: str = "# Fake OpenAI Markdown") -> GenerateResponse:
    return GenerateResponse(
        title="架空の在庫引当API",
        target_type="api",
        test_level="integration",
        viewpoints=[],
        test_cases=[],
        markdown=markdown,
    )


def test_default_provider_uses_mock(monkeypatch) -> None:
    monkeypatch.delenv("APP_LLM_PROVIDER", raising=False)

    response = llm_provider.generate_test_design(_valid_request())

    assert response.markdown.startswith("# テスト設計結果")
    assert response.viewpoints
    assert response.test_cases


def test_mock_provider_uses_existing_mock(monkeypatch) -> None:
    monkeypatch.setenv("APP_LLM_PROVIDER", "mock")

    response = llm_provider.generate_test_design(_valid_request())

    assert response.markdown.startswith("# テスト設計結果")
    assert response.viewpoints[0].category == "正常系"
    assert response.test_cases[0].case_no == "TC-001"


def test_openai_provider_delegates_to_openai_service(monkeypatch) -> None:
    called = {}

    def fake_generate_test_design_openai(request, settings):
        called["request"] = request
        called["settings"] = settings
        return _fake_response()

    monkeypatch.setenv("APP_LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        llm_provider,
        "generate_test_design_openai",
        fake_generate_test_design_openai,
    )

    response = llm_provider.generate_test_design(_valid_request())

    assert called["request"].title == "架空の在庫引当API"
    assert called["settings"].openai_model == "gpt-5.4-nano"
    assert response.markdown == "# Fake OpenAI Markdown"


def test_openai_provider_requires_api_key(monkeypatch) -> None:
    monkeypatch.setenv("APP_LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(LLMConfigurationError, match="OPENAI_API_KEY"):
        llm_provider.generate_test_design(_valid_request())


def test_invalid_openai_model_is_rejected_before_openai_call(monkeypatch) -> None:
    monkeypatch.setenv("APP_LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "unsupported-model")

    with pytest.raises(LLMConfigurationError, match="Unsupported OPENAI_MODEL"):
        llm_provider.generate_test_design(_valid_request())


def test_openai_service_uses_fake_client_without_real_api_call(monkeypatch) -> None:
    calls = []

    class FakeResponses:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(output_text="# OpenAI Markdown")

    fake_client = SimpleNamespace(responses=FakeResponses())

    monkeypatch.setenv("APP_LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        llm_openai,
        "_create_openai_client",
        lambda settings: fake_client,
    )

    response = llm_openai.generate_test_design_openai(
        _valid_request(),
        settings=get_settings(),
    )

    assert calls[0]["model"] == "gpt-5.4-nano"
    assert calls[0]["max_output_tokens"] == 1200
    assert response.markdown == "# OpenAI Markdown"
    assert response.viewpoints
    assert response.test_cases


def test_openai_timeout_is_mapped_without_response_body_logging(monkeypatch) -> None:
    class FakeResponses:
        def create(self, **kwargs):
            raise TimeoutError()

    fake_client = SimpleNamespace(responses=FakeResponses())

    monkeypatch.setenv("APP_LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        llm_openai,
        "_create_openai_client",
        lambda settings: fake_client,
    )

    with pytest.raises(LLMProviderTimeoutError, match="timed out"):
        llm_openai.generate_test_design_openai(
            _valid_request(),
            settings=get_settings(),
        )


def test_openai_configuration_error_returns_clear_api_error(client, monkeypatch) -> None:
    payload = _valid_request().model_dump()

    monkeypatch.setenv("APP_LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post("/test-designs/generate", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "OPENAI_API_KEY is required when APP_LLM_PROVIDER=openai."
    )
