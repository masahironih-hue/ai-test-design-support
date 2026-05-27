"""Minimal Lambda handler for the AWS backend mock API."""

from __future__ import annotations

import base64
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.parse import unquote


GENERATE_ROUTE_PATH = "/test-designs/generate"
HISTORIES_ROUTE_PATH = "/test-designs/histories"
MAX_TITLE_LENGTH = 100
MAX_SPEC_TEXT_LENGTH = 10000
MAX_SUPPLEMENT_LENGTH = 2000
TARGET_TYPES = {"screen", "api", "batch", "db", "external"}
TEST_LEVELS = {"unit", "integration", "system"}
_HISTORIES_TABLE: Any | None = None

TARGET_TYPE_LABELS = {
    "screen": "画面",
    "api": "API",
    "batch": "バッチ",
    "db": "DB",
    "external": "外部連携",
}
TEST_LEVEL_LABELS = {
    "unit": "単体テスト",
    "integration": "結合テスト",
    "system": "システムテスト",
}


class RequestValidationError(Exception):
    def __init__(self, detail: str | dict[str, Any]) -> None:
        self.detail = detail


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    method = _get_method(event)
    path = _get_path(event)

    try:
        if path == GENERATE_ROUTE_PATH:
            if method != "POST":
                return _error_response(
                    405,
                    "Method not allowed.",
                    method,
                    path,
                    "method_not_allowed",
                )

            response_body = _handle_generate(event)
            _safe_log(
                method,
                path,
                200,
                history_id=str(response_body["history_id"]),
            )
            return _json_response(200, response_body)

        if path == HISTORIES_ROUTE_PATH:
            if method != "GET":
                return _error_response(
                    405,
                    "Method not allowed.",
                    method,
                    path,
                    "method_not_allowed",
                )

            response_body = _list_histories()
            _safe_log(method, path, 200)
            return _json_response(200, response_body)

        history_id = _extract_history_id(event, path)
        if history_id is not None:
            if method != "GET":
                return _error_response(
                    405,
                    "Method not allowed.",
                    method,
                    path,
                    "method_not_allowed",
                    history_id=history_id,
                )

            response_body = _get_history(history_id)
            if response_body is None:
                return _error_response(
                    404,
                    "History not found.",
                    method,
                    path,
                    "history_not_found",
                    history_id=history_id,
                )

            _safe_log(method, path, 200, history_id=history_id)
            return _json_response(200, response_body)

        return _error_response(404, "Not found.", method, path, "not_found")
    except RequestValidationError as error:
        return _error_response(400, error.detail, method, path, "bad_request")
    except Exception:
        return _error_response(
            500,
            "Internal server error.",
            method,
            path,
            "internal_error",
        )


def _handle_generate(event: dict[str, Any]) -> dict[str, Any]:
    payload = _parse_body(event)
    request = _validate_request(payload)
    response_body = _build_test_design_response(request)
    history_item = _build_history_item(request, response_body)
    _put_history_item(history_item)

    return {
        **response_body,
        "history_id": history_item["history_id"],
        "created_at": history_item["created_at"],
    }


def _list_histories() -> list[dict[str, Any]]:
    response = _get_histories_table().scan(
        ProjectionExpression=(
            "#history_id, #title, #target_type, #test_level, #created_at"
        ),
        ExpressionAttributeNames={
            "#history_id": "history_id",
            "#title": "title",
            "#target_type": "target_type",
            "#test_level": "test_level",
            "#created_at": "created_at",
        },
    )
    items = response.get("Items", [])
    summaries = [
        _history_summary_from_item(item) for item in items if isinstance(item, dict)
    ]

    return sorted(
        summaries,
        key=lambda item: (item["created_at"], item["history_id"]),
        reverse=True,
    )


def _get_history(history_id: str) -> dict[str, Any] | None:
    response = _get_histories_table().get_item(Key={"history_id": history_id})
    item = response.get("Item")

    if not isinstance(item, dict):
        return None

    return _history_detail_from_item(item)


def _build_history_item(
    request: dict[str, str | None],
    response_body: dict[str, Any],
) -> dict[str, Any]:
    return {
        "history_id": str(uuid.uuid4()),
        "title": request["title"],
        "target_type": request["target_type"],
        "test_level": request["test_level"],
        "spec_text": request["spec_text"],
        "supplement": request["supplement"],
        "viewpoints": response_body["viewpoints"],
        "test_cases": response_body["test_cases"],
        "markdown": response_body["markdown"],
        "created_at": _utc_now_iso(),
    }


def _put_history_item(item: dict[str, Any]) -> None:
    _get_histories_table().put_item(Item=item)


def _get_histories_table() -> Any:
    global _HISTORIES_TABLE

    if _HISTORIES_TABLE is None:
        table_name = os.environ.get("HISTORIES_TABLE_NAME", "").strip()
        if not table_name:
            raise RuntimeError("HISTORIES_TABLE_NAME is not configured.")

        import boto3

        _HISTORIES_TABLE = boto3.resource("dynamodb").Table(table_name)

    return _HISTORIES_TABLE


def _get_method(event: dict[str, Any]) -> str:
    http_context = event.get("requestContext", {}).get("http", {})
    method = http_context.get("method") or event.get("httpMethod") or ""
    return str(method).upper()


def _get_path(event: dict[str, Any]) -> str:
    http_context = event.get("requestContext", {}).get("http", {})
    path = event.get("rawPath") or http_context.get("path") or event.get("path") or ""
    return str(path)


def _extract_history_id(event: dict[str, Any], path: str) -> str | None:
    path_parameters = event.get("pathParameters")
    if isinstance(path_parameters, dict):
        history_id = path_parameters.get("history_id")
        if isinstance(history_id, str) and history_id.strip():
            return history_id.strip()

    prefix = f"{HISTORIES_ROUTE_PATH}/"
    if not path.startswith(prefix):
        return None

    history_id = path[len(prefix) :]
    if not history_id or "/" in history_id:
        return None

    decoded_history_id = unquote(history_id).strip()
    return decoded_history_id if decoded_history_id else None


def _history_summary_from_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "history_id": _string_item(item, "history_id"),
        "title": _string_item(item, "title"),
        "target_type": _string_item(item, "target_type"),
        "test_level": _string_item(item, "test_level"),
        "created_at": _string_item(item, "created_at"),
    }


def _history_detail_from_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "history_id": _string_item(item, "history_id"),
        "title": _string_item(item, "title"),
        "target_type": _string_item(item, "target_type"),
        "test_level": _string_item(item, "test_level"),
        "spec_text": _string_item(item, "spec_text"),
        "supplement": _optional_string_item(item, "supplement"),
        "viewpoints": _list_item(item, "viewpoints"),
        "test_cases": _list_item(item, "test_cases"),
        "markdown": _string_item(item, "markdown"),
        "created_at": _string_item(item, "created_at"),
    }


def _string_item(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    return str(value)


def _optional_string_item(item: dict[str, Any], key: str) -> str | None:
    value = item.get(key)
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def _list_item(item: dict[str, Any], key: str) -> list[Any]:
    value = item.get(key)
    return value if isinstance(value, list) else []


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_body(event: dict[str, Any]) -> dict[str, Any]:
    body = event.get("body")

    if body is None or body == "":
        raise RequestValidationError("Request body is required.")

    if event.get("isBase64Encoded"):
        try:
            body = base64.b64decode(body).decode("utf-8")
        except Exception as error:
            raise RequestValidationError("Request body must be valid UTF-8.") from error

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as error:
        raise RequestValidationError("Request body must be valid JSON.") from error

    if not isinstance(payload, dict):
        raise RequestValidationError("Request body must be a JSON object.")

    return payload


def _validate_request(payload: dict[str, Any]) -> dict[str, str | None]:
    required_fields = ["title", "target_type", "test_level", "spec_text"]
    missing_fields = [
        field
        for field in required_fields
        if not _is_non_empty_string(payload.get(field))
    ]

    if missing_fields:
        raise RequestValidationError(
            {
                "message": "Required fields are missing or empty.",
                "fields": missing_fields,
            }
        )

    target_type = str(payload["target_type"])
    test_level = str(payload["test_level"])

    if target_type not in TARGET_TYPES:
        raise RequestValidationError(
            {
                "message": "target_type is invalid.",
                "allowed_values": sorted(TARGET_TYPES),
            }
        )

    if test_level not in TEST_LEVELS:
        raise RequestValidationError(
            {
                "message": "test_level is invalid.",
                "allowed_values": sorted(TEST_LEVELS),
            }
        )

    title = str(payload["title"]).strip()
    spec_text = str(payload["spec_text"]).strip()
    supplement = payload.get("supplement")

    if len(title) > MAX_TITLE_LENGTH:
        raise RequestValidationError(
            {"message": "title is too long.", "max_length": MAX_TITLE_LENGTH}
        )

    if len(spec_text) > MAX_SPEC_TEXT_LENGTH:
        raise RequestValidationError(
            {"message": "spec_text is too long.", "max_length": MAX_SPEC_TEXT_LENGTH}
        )

    if supplement is not None:
        if not isinstance(supplement, str):
            raise RequestValidationError("supplement must be a string.")

        supplement = supplement.strip()
        if len(supplement) > MAX_SUPPLEMENT_LENGTH:
            raise RequestValidationError(
                {
                    "message": "supplement is too long.",
                    "max_length": MAX_SUPPLEMENT_LENGTH,
                }
            )

    return {
        "title": title,
        "target_type": target_type,
        "test_level": test_level,
        "spec_text": spec_text,
        "supplement": supplement,
    }


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _build_test_design_response(request: dict[str, str | None]) -> dict[str, Any]:
    viewpoints = _build_viewpoints(request)
    test_cases = _build_test_cases()
    markdown = _build_markdown(request, viewpoints, test_cases)

    return {
        "title": request["title"],
        "target_type": request["target_type"],
        "test_level": request["test_level"],
        "viewpoints": viewpoints,
        "test_cases": test_cases,
        "markdown": markdown,
    }


def _build_viewpoints(request: dict[str, str | None]) -> list[dict[str, Any]]:
    target_type = str(request["target_type"])
    target_label = TARGET_TYPE_LABELS[target_type]
    title = str(request["title"])

    return [
        {
            "category": "正常系",
            "items": [
                f"{title}の主要処理が仕様どおり成功すること",
                "正常な入力・前提条件で期待する結果が得られること",
            ],
        },
        {
            "category": "異常系",
            "items": [
                "不正な入力・前提条件で適切にエラーとなること",
                "エラー発生時に利用者または運用者が原因を判断できること",
            ],
        },
        {
            "category": "入力チェック",
            "items": [
                "必須項目が未入力の場合にエラーとなること",
                "桁数、形式、型、許容値のチェックが行われること",
            ],
        },
        {
            "category": "境界値",
            "items": [
                "最小値、最大値、最大桁数で正しく処理されること",
                "境界値を超えた場合に適切にエラーとなること",
            ],
        },
        {
            "category": f"{target_label}固有観点",
            "items": _build_target_specific_viewpoints(target_type),
        },
        {
            "category": "ログ・確認事項",
            "items": [
                "正常終了時・異常終了時に必要なログが出力されること",
                "後続処理、DB更新、外部連携への影響を確認すること",
            ],
        },
    ]


def _build_target_specific_viewpoints(target_type: str) -> list[str]:
    if target_type == "screen":
        return [
            "画面遷移、メッセージ表示、入力項目の活性・非活性を確認すること",
            "ボタン押下時の処理結果とエラー表示を確認すること",
        ]

    if target_type == "api":
        return [
            "リクエストパラメータ、レスポンス項目、HTTPステータスを確認すること",
            "不正リクエスト時のエラーレスポンス形式を確認すること",
        ]

    if target_type == "batch":
        return [
            "正常終了、異常終了、リカバリ、再実行時の動作を確認すること",
            "処理件数、出力ファイル、ログ出力内容を確認すること",
        ]

    if target_type == "db":
        return [
            "登録、更新、削除対象のテーブル・カラムが正しいこと",
            "トランザクション、ロールバック、排他制御の観点を確認すること",
        ]

    return [
        "外部システムへの送受信データ、応答結果、エラー時の扱いを確認すること",
        "タイムアウト、リトライ、通信失敗時の挙動を確認すること",
    ]


def _build_test_cases() -> list[dict[str, str]]:
    return [
        {
            "case_no": "TC-001",
            "category": "正常系",
            "condition": "仕様に沿った有効な入力値・前提条件を用意する",
            "expected_result": "処理が成功し、期待する結果が得られること",
        },
        {
            "case_no": "TC-002",
            "category": "異常系",
            "condition": "不正な入力値または不正な前提条件を用意する",
            "expected_result": "処理が失敗し、適切なエラー内容が返されること",
        },
        {
            "case_no": "TC-003",
            "category": "入力チェック",
            "condition": "必須項目未入力、形式不正、桁数超過の入力値を用意する",
            "expected_result": "入力チェックエラーとなり、後続処理が実行されないこと",
        },
        {
            "case_no": "TC-004",
            "category": "境界値",
            "condition": "最小値、最大値、最大桁数、上限超過の値を用意する",
            "expected_result": "境界内の値は正常処理され、境界外の値はエラーとなること",
        },
        {
            "case_no": "TC-005",
            "category": "ログ・確認事項",
            "condition": "正常終了時および異常終了時の処理を実行する",
            "expected_result": "確認に必要なログ、メッセージ、処理結果が確認できること",
        },
    ]


def _build_markdown(
    request: dict[str, str | None],
    viewpoints: list[dict[str, Any]],
    test_cases: list[dict[str, str]],
) -> str:
    target_type = str(request["target_type"])
    test_level = str(request["test_level"])
    lines = [
        "# テスト設計結果",
        "",
        "## 入力情報",
        "",
        f"- タイトル: {request['title']}",
        f"- 対象種別: {TARGET_TYPE_LABELS[target_type]}",
        f"- テストレベル: {TEST_LEVEL_LABELS[test_level]}",
        "",
        "## 仕様概要",
        "",
        str(request["spec_text"]),
        "",
    ]

    if request.get("supplement"):
        lines.extend(["## 補足事項", "", str(request["supplement"]), ""])

    lines.extend(["## テスト観点", ""])

    for viewpoint in viewpoints:
        lines.extend([f"### {viewpoint['category']}", ""])
        for item in viewpoint["items"]:
            lines.append(f"- {item}")
        lines.append("")

    lines.extend(
        [
            "## テストケース",
            "",
            "| No | 分類 | 条件 | 期待結果 |",
            "|---|---|---|---|",
        ]
    )

    for test_case in test_cases:
        lines.append(
            "| "
            f"{_escape_markdown_table_cell(test_case['case_no'])} | "
            f"{_escape_markdown_table_cell(test_case['category'])} | "
            f"{_escape_markdown_table_cell(test_case['condition'])} | "
            f"{_escape_markdown_table_cell(test_case['expected_result'])} |"
        )

    lines.extend(
        [
            "",
            "## 注意事項",
            "",
            "- この結果はLLM Mock相当の固定テンプレート生成です。",
            "- 実案件の顧客情報、個人情報、APIキー、パスワード、業務機密は入力しないでください。",
            "- 実際のテスト設計では、仕様書、設計書、業務ルール、既存障害、運用観点を踏まえて見直してください。",
            "",
        ]
    )
    return "\n".join(lines)


def _escape_markdown_table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def _json_response(status_code: int, body: Any) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": _headers(),
        "body": json.dumps(body, ensure_ascii=False),
    }


def _error_response(
    status_code: int,
    detail: str | dict[str, Any],
    method: str,
    path: str,
    error_type: str,
    history_id: str | None = None,
) -> dict[str, Any]:
    _safe_log(method, path, status_code, error_type, history_id)
    return _json_response(status_code, {"detail": detail})


def _headers() -> dict[str, str]:
    return {
        "content-type": "application/json; charset=utf-8",
        "access-control-allow-origin": os.environ.get("ALLOWED_ORIGIN", "*"),
        "access-control-allow-methods": "GET,POST,OPTIONS",
        "access-control-allow-headers": "content-type",
    }


def _safe_log(
    method: str,
    path: str,
    status_code: int,
    error_type: str | None = None,
    history_id: str | None = None,
) -> None:
    log_item = {
        "method": method,
        "path": path,
        "status_code": status_code,
    }
    if error_type:
        log_item["error_type"] = error_type
    if history_id:
        log_item["history_id"] = history_id
    print(json.dumps(log_item, ensure_ascii=False))
