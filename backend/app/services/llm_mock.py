from app.models.test_design import (
    TestCase,
    TestDesignGenerateRequest,
    TestDesignGenerateResponse,
    Viewpoint,
)


_TARGET_TYPE_LABELS = {
    "screen": "画面",
    "api": "API",
    "batch": "バッチ",
    "db": "DB",
    "external": "外部連携",
}

_TEST_LEVEL_LABELS = {
    "unit": "単体テスト",
    "integration": "結合テスト",
    "system": "システムテスト",
}


def generate_test_design_mock(
    request: TestDesignGenerateRequest,
) -> TestDesignGenerateResponse:
    """LLMの代替として固定ルールでテスト設計結果を生成する。"""

    viewpoints = _build_viewpoints(request)
    test_cases = _build_test_cases(request)
    markdown = _build_markdown(request, viewpoints, test_cases)

    return TestDesignGenerateResponse(
        title=request.title,
        target_type=request.target_type,
        test_level=request.test_level,
        viewpoints=viewpoints,
        test_cases=test_cases,
        markdown=markdown,
    )


def _build_viewpoints(request: TestDesignGenerateRequest) -> list[Viewpoint]:
    """対象種別に応じた最小限のテスト観点を生成する。"""

    title = request.title
    target_label = _TARGET_TYPE_LABELS[request.target_type]

    viewpoints = [
        Viewpoint(
            category="正常系",
            items=[
                f"{title}の主要処理が仕様どおり成功すること",
                "正常な入力・前提条件で期待する結果が得られること",
            ],
        ),
        Viewpoint(
            category="異常系",
            items=[
                "不正な入力・前提条件で適切にエラーとなること",
                "エラー発生時に利用者または運用者が原因を判断できること",
            ],
        ),
        Viewpoint(
            category="入力チェック",
            items=[
                "必須項目が未入力の場合にエラーとなること",
                "桁数、形式、型、許容値のチェックが行われること",
            ],
        ),
        Viewpoint(
            category="境界値",
            items=[
                "最小値、最大値、最大桁数で正しく処理されること",
                "境界値を超えた場合に適切にエラーとなること",
            ],
        ),
        Viewpoint(
            category=f"{target_label}固有観点",
            items=_build_target_specific_viewpoints(request),
        ),
        Viewpoint(
            category="ログ・確認事項",
            items=[
                "正常終了時・異常終了時に必要なログが出力されること",
                "後続処理、DB更新、外部連携への影響を確認すること",
            ],
        ),
    ]

    return viewpoints


def _build_target_specific_viewpoints(
    request: TestDesignGenerateRequest,
) -> list[str]:
    """target_type ごとの差分観点を返す。"""

    if request.target_type == "screen":
        return [
            "画面遷移、メッセージ表示、入力項目の活性・非活性を確認すること",
            "ボタン押下時の処理結果とエラー表示を確認すること",
        ]

    if request.target_type == "api":
        return [
            "リクエストパラメータ、レスポンス項目、HTTPステータスを確認すること",
            "不正リクエスト時のエラーレスポンス形式を確認すること",
        ]

    if request.target_type == "batch":
        return [
            "正常終了、異常終了、リカバリ、再実行時の動作を確認すること",
            "処理件数、出力ファイル、ログ出力内容を確認すること",
        ]

    if request.target_type == "db":
        return [
            "登録、更新、削除対象のテーブル・カラムが正しいこと",
            "トランザクション、ロールバック、排他制御の観点を確認すること",
        ]

    if request.target_type == "external":
        return [
            "外部システムへの送受信データ、応答結果、エラー時の扱いを確認すること",
            "タイムアウト、リトライ、通信失敗時の挙動を確認すること",
        ]

    return ["対象種別に応じた固有観点を確認すること"]


def _build_test_cases(request: TestDesignGenerateRequest) -> list[TestCase]:
    """最小限のテストケースを生成する。"""

    return [
        TestCase(
            case_no="TC-001",
            category="正常系",
            condition="仕様に沿った有効な入力値・前提条件を用意する",
            expected_result="処理が成功し、期待する結果が得られること",
        ),
        TestCase(
            case_no="TC-002",
            category="異常系",
            condition="不正な入力値または不正な前提条件を用意する",
            expected_result="処理が失敗し、適切なエラー内容が返されること",
        ),
        TestCase(
            case_no="TC-003",
            category="入力チェック",
            condition="必須項目未入力、形式不正、桁数超過の入力値を用意する",
            expected_result="入力チェックエラーとなり、後続処理が実行されないこと",
        ),
        TestCase(
            case_no="TC-004",
            category="境界値",
            condition="最小値、最大値、最大桁数、上限超過の値を用意する",
            expected_result="境界内の値は正常処理され、境界外の値はエラーとなること",
        ),
        TestCase(
            case_no="TC-005",
            category="ログ・確認事項",
            condition="正常終了時および異常終了時の処理を実行する",
            expected_result="確認に必要なログ、メッセージ、処理結果が確認できること",
        ),
    ]


def _build_markdown(
    request: TestDesignGenerateRequest,
    viewpoints: list[Viewpoint],
    test_cases: list[TestCase],
) -> str:
    """レスポンスに含めるMarkdown文字列を生成する。"""

    target_label = _TARGET_TYPE_LABELS[request.target_type]
    test_level_label = _TEST_LEVEL_LABELS[request.test_level]

    lines: list[str] = [
        "# テスト設計結果",
        "",
        "## 入力情報",
        "",
        f"- タイトル: {request.title}",
        f"- 対象種別: {target_label}",
        f"- テストレベル: {test_level_label}",
        "",
        "## 仕様概要",
        "",
        request.spec_text,
        "",
    ]

    if request.supplement:
        lines.extend(
            [
                "## 補足事項",
                "",
                request.supplement,
                "",
            ]
        )

    lines.extend(
        [
            "## テスト観点",
            "",
        ]
    )

    for viewpoint in viewpoints:
        lines.extend(
            [
                f"### {viewpoint.category}",
                "",
            ]
        )
        for item in viewpoint.items:
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
            f"{_escape_markdown_table_cell(test_case.case_no)} | "
            f"{_escape_markdown_table_cell(test_case.category)} | "
            f"{_escape_markdown_table_cell(test_case.condition)} | "
            f"{_escape_markdown_table_cell(test_case.expected_result)} |"
        )

    lines.extend(
        [
            "",
            "## 注意事項",
            "",
            "- この結果はLLM Mockによる固定テンプレート生成です。",
            "- 実案件の顧客情報、個人情報、APIキー、パスワード、業務機密は入力しないでください。",
            "- 実際のテスト設計では、仕様書、設計書、業務ルール、既存障害、運用観点を踏まえて見直してください。",
            "",
        ]
    )

    return "\n".join(lines)


def _escape_markdown_table_cell(value: str) -> str:
    """Markdown表のセル崩れを抑制する。"""

    return value.replace("|", "\\|").replace("\r", " ").replace("\n", " ")
