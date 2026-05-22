# API設計メモ

## 1. 目的

本ドキュメントは、「業務系SE向け AIテスト設計支援ツール」の Phase 1：ローカルMVP におけるAPI設計を整理するものです。

Phase 1では、ローカル環境で以下の流れを実現するための最小APIを作成します。

```text
仕様入力
↓
LLM Mockによるテスト設計結果生成
↓
生成結果表示
↓
Markdownコピー
↓
履歴保存
↓
履歴一覧・履歴詳細確認
```

MVPでは、OpenAI APIやAmazon Bedrockなどの外部LLM APIは使用せず、Backend内のLLM Mockサービスで生成結果を作成します。

## 更新メモ

本ドキュメントは、ローカルMVP総合動作確認後の実装状態に合わせて、APIパス、入力項目名、`target_type` / `test_level` のコード値を更新しています。

- 生成API: `POST /test-designs/generate`
- 履歴一覧API: `GET /test-designs/histories`
- 履歴詳細API: `GET /test-designs/histories/{history_id}`
- 入力項目: `title`、`target_type`、`test_level`、`spec_text`、`supplement`
- `target_type`: `screen`、`api`、`batch`、`db`、`external`
- `test_level`: `unit`、`integration`、`system`

---

## 2. API設計方針

API設計の方針は以下です。

- FastAPIでREST APIを作成する
- FrontendはNext.js / React / TypeScriptからAPIを呼び出す
- MVPでは認証・認可は実装しない
- MVPでは生成成功時に自動で履歴保存する
- 生成結果はJSON形式とMarkdown形式の両方で返す
- 履歴データはSQLiteに保存する
- 入力値には本業の顧客情報、個人情報、APIキー、パスワード、業務機密を含めない
- 外部LLM APIを使わないため、APIキーは不要とする

---

## 3. API一覧

MVPで作成するAPIは以下です。

| メソッド | パス | 用途 |
|---|---|---|
| GET | `/health` | Backendのヘルスチェック |
| POST | `/test-designs/generate` | テスト設計結果の生成と履歴保存 |
| GET | `/test-designs/histories` | 生成履歴一覧の取得 |
| GET | `/test-designs/histories/{history_id}` | 生成履歴詳細の取得 |

---

## 4. 共通仕様

### 4.1 ベースURL

ローカル開発時のBackend URLは以下を想定します。

```text
http://localhost:8000
```

Frontendからは環境変数でBackend API URLを参照する想定です。

例：

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

### 4.2 リクエスト形式

POST APIでは、リクエストボディにJSONを使用します。

```http
Content-Type: application/json
```

---

### 4.3 レスポンス形式

レスポンスはJSON形式とします。

```http
Content-Type: application/json
```

---

### 4.4 日時形式

日時はISO 8601形式の文字列で返却します。

例：

```text
2026-05-21T10:00:00
```

Backend / DBではUTC基準で扱い、Frontend表示時にJSTへ変換します。

---

## 5. データ項目定義

### 5.1 テスト対象種別

`target_type` は以下の値を想定します。

| 値 | 表示名 | 用途 |
|---|---|---|
| `screen` | 画面 | 画面仕様、入力チェック、表示制御など |
| `api` | API | REST API、外部公開API、内部APIなど |
| `batch` | バッチ | 日次処理、集計処理、ファイル取込など |
| `db` | DB更新 | 登録、更新、削除、整合性確認など |
| `external` | 外部連携 | 外部API、ファイル連携、リトライ、タイムアウトなど |

---

### 5.2 テストレベル

`test_level` は以下の値を想定します。

| 値 | 表示名 | 用途 |
|---|---|---|
| `unit` | 単体テスト | 関数、メソッド、単一処理単位の確認 |
| `integration` | 結合テスト | API、DB、外部連携を含む結合確認 |
| `system` | システムテスト | システム全体としての業務シナリオ確認 |

---

## 6. GET `/health`

### 6.1 概要

Backendの起動確認を行うためのヘルスチェックAPIです。

### 6.2 リクエスト

リクエストボディはありません。

### 6.3 レスポンス

```json
{
  "status": "ok"
}
```

### 6.4 ステータスコード

| ステータス | 内容 |
|---:|---|
| 200 | 正常 |

### 6.5 curl例

```bash
curl http://localhost:8000/health
```

---

## 7. POST `/test-designs/generate`

### 7.1 概要

仕様入力を受け取り、LLM Mockでテスト設計結果を生成し、SQLiteに履歴保存します。

MVPでは、生成処理と履歴保存を分けず、生成成功時に自動保存します。

### 7.2 リクエスト項目

| 項目 | 型 | 必須 | 内容 |
|---|---|---:|---|
| `title` | string | 任意 | テスト設計タイトル |
| `target_type` | string | 必須 | テスト対象種別 |
| `test_level` | string | 必須 | テストレベル |
| `spec_text` | string | 必須 | 仕様メモ |
| `supplement` | string | 任意 | 補足事項 |

### 7.3 リクエスト例

```json
{
  "title": "注文登録APIのテスト設計",
  "target_type": "api",
  "test_level": "integration",
  "spec_text": "注文情報を受け取り、注文テーブルと注文明細テーブルに登録するAPI。注文登録時に在庫引当APIを呼び出す。",
  "supplement": "在庫引当失敗時は注文登録を行わず、エラーレスポンスを返す。"
}
```

### 7.4 レスポンス項目

| 項目 | 型 | 内容 |
|---|---|---|
| `id` | integer | 履歴ID |
| `title` | string | テスト設計タイトル |
| `target_type` | string | テスト対象種別 |
| `test_level` | string | テストレベル |
| `spec_text` | string | 入力された仕様メモ |
| `supplement` | string | 補足事項 |
| `result_json` | object | 生成結果JSON |
| `result_markdown` | string | Markdown形式の生成結果 |
| `llm_provider` | string | LLM Provider。MVPでは `mock` |
| `llm_model` | string | LLM Model。MVPでは `mock-v1` |
| `created_at` | string | 作成日時 |
| `updated_at` | string | 更新日時 |

### 7.5 レスポンス例

```json
{
  "id": 1,
  "title": "注文登録APIのテスト設計",
  "target_type": "api",
  "test_level": "integration",
  "spec_text": "注文情報を受け取り、注文テーブルと注文明細テーブルに登録するAPI。注文登録時に在庫引当APIを呼び出す。",
  "supplement": "在庫引当失敗時は注文登録を行わず、エラーレスポンスを返す。",
  "result_json": {
    "summary": "注文登録APIに対するテスト観点とテストケース案です。",
    "viewpoints": [
      {
        "category": "正常系",
        "items": [
          "必須項目をすべて指定した場合に処理が成功すること",
          "複数明細を含む注文情報が正しく登録されること"
        ]
      },
      {
        "category": "異常系",
        "items": [
          "必須項目が未入力の場合にエラーとなること",
          "在庫引当APIが失敗した場合に注文登録されないこと"
        ]
      },
      {
        "category": "DB更新確認",
        "items": [
          "注文テーブルに注文ヘッダ情報が登録されること",
          "注文明細テーブルに明細情報が登録されること"
        ]
      }
    ],
    "test_cases": [
      {
        "case_no": "TC-001",
        "title": "正常な注文登録",
        "precondition": "有効な顧客情報と商品情報が存在する",
        "steps": [
          "正常な注文情報を送信する",
          "レスポンス内容を確認する",
          "DB登録内容を確認する"
        ],
        "expected_result": "注文登録が成功し、注文IDが返却される",
        "priority": "High"
      }
    ],
    "additional_questions": [
      "在庫引当失敗時のエラーコード仕様を確認する必要があります。",
      "注文登録後の通知処理有無を確認する必要があります。"
    ]
  },
  "result_markdown": "# テスト設計結果\n\n## 入力情報\n\n- タイトル: 注文登録APIのテスト設計\n...",
  "llm_provider": "mock",
  "llm_model": "mock-v1",
  "created_at": "2026-05-21T10:00:00",
  "updated_at": "2026-05-21T10:00:00"
}
```

### 7.6 ステータスコード

| ステータス | 内容 |
|---:|---|
| 201 | 生成・保存成功 |
| 400 | 入力値不正 |
| 422 | リクエストバリデーションエラー |
| 500 | サーバー内部エラー |

### 7.7 バリデーション方針

MVPでは、以下のバリデーションを行います。

| 項目 | ルール |
|---|---|
| `target_type` | 定義済みの値のみ許可する |
| `test_level` | 定義済みの値のみ許可する |
| `spec_text` | 必須、空文字不可 |
| `title` | 未入力の場合はBackend側で自動生成する |
| `supplement` | 未入力可 |

タイトル未入力時の自動生成例：

```text
テスト設計 2026-05-21 10:00
```

---

## 8. GET `/test-designs/histories`

### 8.1 概要

保存済みのテスト設計生成履歴を一覧取得します。

MVPでは検索、フィルタ、ページングは実装しません。  
作成日時の降順で返却します。

### 8.2 リクエスト

リクエストボディはありません。

### 8.3 レスポンス項目

| 項目 | 型 | 内容 |
|---|---|---|
| `id` | integer | 履歴ID |
| `title` | string | テスト設計タイトル |
| `target_type` | string | テスト対象種別 |
| `test_level` | string | テストレベル |
| `created_at` | string | 作成日時 |

### 8.4 レスポンス例

```json
[
  {
    "id": 2,
    "title": "日次売上集計バッチのテスト設計",
    "target_type": "batch",
    "test_level": "integration",
    "created_at": "2026-05-21T11:00:00"
  },
  {
    "id": 1,
    "title": "注文登録APIのテスト設計",
    "target_type": "api",
    "test_level": "integration",
    "created_at": "2026-05-21T10:00:00"
  }
]
```

### 8.5 ステータスコード

| ステータス | 内容 |
|---:|---|
| 200 | 正常 |
| 500 | サーバー内部エラー |

### 8.6 curl例

```bash
curl http://localhost:8000/test-designs/histories
```

---

## 9. GET `/test-designs/histories/{history_id}`

### 9.1 概要

指定したIDのテスト設計生成履歴を詳細取得します。

### 9.2 パスパラメータ

| 項目 | 型 | 必須 | 内容 |
|---|---|---:|---|
| `id` | integer | 必須 | 履歴ID |

### 9.3 レスポンス項目

| 項目 | 型 | 内容 |
|---|---|---|
| `id` | integer | 履歴ID |
| `title` | string | テスト設計タイトル |
| `target_type` | string | テスト対象種別 |
| `test_level` | string | テストレベル |
| `spec_text` | string | 入力された仕様メモ |
| `supplement` | string | 補足事項 |
| `result_json` | object | 生成結果JSON |
| `result_markdown` | string | Markdown形式の生成結果 |
| `llm_provider` | string | LLM Provider |
| `llm_model` | string | LLM Model |
| `created_at` | string | 作成日時 |
| `updated_at` | string | 更新日時 |

### 9.4 レスポンス例

```json
{
  "id": 1,
  "title": "注文登録APIのテスト設計",
  "target_type": "api",
  "test_level": "integration",
  "spec_text": "注文情報を受け取り、注文テーブルと注文明細テーブルに登録するAPI。注文登録時に在庫引当APIを呼び出す。",
  "supplement": "在庫引当失敗時は注文登録を行わず、エラーレスポンスを返す。",
  "result_json": {
    "summary": "注文登録APIに対するテスト観点とテストケース案です。",
    "viewpoints": [],
    "test_cases": [],
    "additional_questions": []
  },
  "result_markdown": "# テスト設計結果\n\n## 入力情報\n\n- タイトル: 注文登録APIのテスト設計\n...",
  "llm_provider": "mock",
  "llm_model": "mock-v1",
  "created_at": "2026-05-21T10:00:00",
  "updated_at": "2026-05-21T10:00:00"
}
```

### 9.5 ステータスコード

| ステータス | 内容 |
|---:|---|
| 200 | 正常 |
| 404 | 指定IDの履歴が存在しない |
| 500 | サーバー内部エラー |

### 9.6 curl例

```bash
curl http://localhost:8000/test-designs/histories/1
```

---

## 10. エラーレスポンス方針

MVPでは、エラー時に以下の形式で返却します。

```json
{
  "detail": "エラーメッセージ"
}
```

FastAPI標準のバリデーションエラーは、MVPでは標準形式のまま扱います。

### 10.1 エラー例：必須項目不足

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "spec_text"
      ],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

### 10.2 エラー例：履歴が存在しない

```json
{
  "detail": "Test design history not found"
}
```

---

## 11. セキュリティ・守秘義務上の注意

本APIに送信する入力値には、以下を含めないこととします。

- 顧客名
- 個人情報
- APIキー
- パスワード
- アクセストークン
- 本番環境情報
- 実際の設計書
- 実際のソースコード
- 実際の障害ログ
- 業務機密
- 契約上公開できない情報

MVPではローカル環境で動作しますが、入力内容はSQLiteに保存されるため、架空データまたはマスキング済みデータのみを使用します。

---

## 12. MVPでは実装しないAPI

Phase 1の初期MVPでは、以下のAPIは作成しません。

| API | 理由 |
|---|---|
| ログインAPI | 認証はMVP対象外のため |
| ユーザー管理API | マルチユーザー化はMVP対象外のため |
| 履歴削除API | 初期MVPでは参照中心とするため |
| 履歴更新API | 生成履歴は編集しない前提のため |
| 検索API | 履歴件数が少ない前提のため |
| ファイルアップロードAPI | セキュリティリスクと実装範囲が増えるため |
| OpenAI API連携用API | Mock完成後の拡張候補とするため |
| Bedrock連携用API | Phase 4以降の候補とするため |

---

## 13. 実装時の補足方針

実装時は、以下のような構成を想定します。

```text
backend/
  app/
    main.py
    api/
      routes.py
    models/
      test_design.py
    schemas/
      test_design.py
    services/
      llm_mock.py
      markdown_builder.py
    db/
      session.py
```

ただし、実際のファイル構成は実装時に調整してよいものとします。

MVPでは、過剰なレイヤ分割よりも、以下を優先します。

- 読みやすいこと
- テストしやすいこと
- 後からOpenAI APIやBedrockに差し替えやすいこと
- READMEで説明しやすいこと

---

## 14. 完了条件

本API設計に基づくBackend実装の完了条件は以下です。

- `GET /health` が動作する
- `POST /test-designs/generate` でテスト設計結果を生成できる
- 生成結果がSQLiteに保存される
- `GET /test-designs/histories` で履歴一覧を取得できる
- `GET /test-designs/histories/{history_id}` で履歴詳細を取得できる
- 生成結果JSONとMarkdownをレスポンスで取得できる
- 主要APIのpytestが通る
- 実データや機密情報を使わず、架空データで動作確認できる
