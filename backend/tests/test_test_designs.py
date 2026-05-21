from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_generate_test_design_success() -> None:
    payload = {
        "title": "ログイン画面",
        "target_type": "screen",
        "test_level": "integration",
        "spec_text": (
            "利用者IDとパスワードを入力し、認証に成功した場合は"
            "メニュー画面へ遷移する。認証に失敗した場合は"
            "エラーメッセージを表示する。"
        ),
        "supplement": "業務系Webアプリのログイン機能を想定する。",
    }

    response = client.post("/test-designs/generate", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "ログイン画面"
    assert data["target_type"] == "screen"
    assert data["test_level"] == "integration"

    assert len(data["viewpoints"]) > 0
    assert data["viewpoints"][0]["category"] == "正常系"
    assert len(data["viewpoints"][0]["items"]) > 0

    assert len(data["test_cases"]) > 0
    assert data["test_cases"][0]["case_no"] == "TC-001"

    assert data["markdown"].startswith("# テスト設計結果")
    assert "## テスト観点" in data["markdown"]
    assert "## テストケース" in data["markdown"]
    assert "TC-001" in data["markdown"]


def test_generate_test_design_invalid_target_type() -> None:
    payload = {
        "title": "ログイン画面",
        "target_type": "invalid",
        "test_level": "integration",
        "spec_text": "ログイン機能の仕様。",
    }

    response = client.post("/test-designs/generate", json=payload)

    assert response.status_code == 422


def test_generate_test_design_invalid_test_level() -> None:
    payload = {
        "title": "ログイン画面",
        "target_type": "screen",
        "test_level": "invalid",
        "spec_text": "ログイン機能の仕様。",
    }

    response = client.post("/test-designs/generate", json=payload)

    assert response.status_code == 422


def test_generate_test_design_title_required() -> None:
    payload = {
        "title": "",
        "target_type": "screen",
        "test_level": "integration",
        "spec_text": "ログイン機能の仕様。",
    }

    response = client.post("/test-designs/generate", json=payload)

    assert response.status_code == 422
