def _valid_payload():
    return {
        "title": "架空の在庫引当API",
        "target_type": "api",
        "test_level": "integration",
        "spec_text": "商品IDと数量を受け取り、在庫引当を行う架空のAPI。",
        "supplement": "外部倉庫システムとの連携はMockとする。",
    }


def test_generate_saves_history(client):
    payload = _valid_payload()

    generate_response = client.post("/test-designs/generate", json=payload)
    assert generate_response.status_code == 200

    histories_response = client.get("/test-designs/histories")
    assert histories_response.status_code == 200

    histories = histories_response.json()
    assert len(histories) == 1
    assert histories[0]["title"] == payload["title"]
    assert histories[0]["target_type"] == payload["target_type"]
    assert histories[0]["test_level"] == payload["test_level"]
    assert "id" in histories[0]
    assert "created_at" in histories[0]


def test_get_history_detail(client):
    payload = _valid_payload()

    client.post("/test-designs/generate", json=payload)

    histories = client.get("/test-designs/histories").json()
    history_id = histories[0]["id"]

    detail_response = client.get(f"/test-designs/histories/{history_id}")

    assert detail_response.status_code == 200

    detail = detail_response.json()
    assert detail["id"] == history_id
    assert detail["title"] == payload["title"]
    assert detail["target_type"] == payload["target_type"]
    assert detail["test_level"] == payload["test_level"]
    assert detail["spec_text"] == payload["spec_text"]
    assert detail["supplement"] == payload["supplement"]
    assert isinstance(detail["viewpoints"], list)
    assert isinstance(detail["test_cases"], list)
    assert isinstance(detail["markdown"], str)
    assert detail["markdown"]


def test_get_history_detail_returns_404_when_not_found(client):
    response = client.get("/test-designs/histories/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "History not found"


def test_invalid_request_is_not_saved(client):
    invalid_payload = {
        "title": "架空の在庫引当API",
        "target_type": "api",
        "test_level": "integration",
        # spec_text がないため不正
        "supplement": "外部倉庫システムとの連携はMockとする。",
    }

    response = client.post("/test-designs/generate", json=invalid_payload)
    assert response.status_code == 422

    histories_response = client.get("/test-designs/histories")
    assert histories_response.status_code == 200
    assert histories_response.json() == []
