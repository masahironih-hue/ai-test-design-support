from app.models.test_design import TestDesignGenerateRequest


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


def build_test_design_prompt(request: TestDesignGenerateRequest) -> str:
    target_type_label = _TARGET_TYPE_LABELS[request.target_type]
    test_level_label = _TEST_LEVEL_LABELS[request.test_level]
    supplement = request.supplement or "なし"

    return f"""あなたは業務系システム開発に詳しいテスト設計支援アシスタントです。
以下の入力情報をもとに、テスト観点、テストケース、追加確認事項をMarkdownで作成してください。

注意:
- 入力情報は架空データまたはマスキング済みデータである前提です。
- 実案件情報、顧客情報、個人情報、APIキー、パスワード、業務機密を含めないでください。
- 出力は日本語のMarkdownのみとし、JSONやコードフェンスで囲まないでください。
- テスト観点は正常系、異常系、入力チェック、境界値、対象種別固有観点を含めてください。
- テストケースは表形式にし、No、分類、条件、期待結果を含めてください。

# 入力情報

- タイトル: {request.title}
- 対象種別: {target_type_label}
- テストレベル: {test_level_label}

## 仕様本文

{request.spec_text}

## 補足事項

{supplement}
"""
