# LLM Mock設計メモ

## 1. 目的

本ドキュメントは、「業務系SE向け AIテスト設計支援ツール」の Phase 1：ローカルMVP における LLM Mock の設計を整理するものです。

Phase 1では、OpenAI APIやAmazon Bedrockなどの外部LLM APIは使用せず、Backend内のMockサービスでテスト観点・テストケース案・追加確認事項を生成します。

MVPにおけるLLM Mockの目的は、生成AIそのものの精度を追求することではなく、以下の流れを安定して動作確認できるようにすることです。

```text
仕様入力
↓
LLM Mockによるテスト設計結果生成
↓
生成結果JSON作成
↓
Markdown変換
↓
履歴保存
↓
画面表示
```

---

## 2. LLM Mockを使う理由

MVP初期でLLM Mockを使う理由は以下です。

| 理由 | 内容 |
|---|---|
| 外部APIキーが不要 | OpenAI APIキーやBedrock設定なしで開発できる |
| 動作が安定する | 同じ入力に対して同じ出力を返せる |
| テストしやすい | pytestで期待結果を検証しやすい |
| コストが発生しない | API利用料を気にせず開発できる |
| セキュリティリスクを抑えられる | 入力内容を外部APIへ送信しない |
| UI/API/DBを先に固められる | LLM連携前にアプリ全体の流れを完成できる |
| 将来差し替えやすい | Mockの入出力を固定することでOpenAI APIやBedrockに置き換えやすい |

---

## 3. 設計方針

LLM Mockの設計方針は以下です。

- 同じ入力に対して同じ出力を返す
- ランダムな生成は行わない
- 外部APIは呼び出さない
- 入力値の一部を出力に反映する
- `target_type` に応じて生成観点を一部切り替える
- `test_level` に応じて確認粒度を一部切り替える
- 生成結果JSONの構造は固定する
- Markdown変換しやすい構造にする
- pytestで検証しやすい構造にする
- 将来のOpenAI API / Bedrock連携に差し替えやすい境界を作る

---

## 4. 対象範囲

### 4.1 MVPで対応すること

LLM Mockでは、以下を生成します。

| 生成対象 | 内容 |
|---|---|
| 概要 | 入力されたタイトル・対象種別に応じた概要文 |
| テスト観点 | 正常系、異常系、境界値、DB更新確認など |
| テストケース案 | 最小限のテストケース |
| 追加確認事項 | 仕様確認が必要な事項 |
| Markdown変換用データ | Markdown出力に利用できる構造 |

---

### 4.2 MVPで対応しないこと

LLM Mockでは、以下は行いません。

| 対象外 | 理由 |
|---|---|
| 自然言語の高度な解析 | MVPでは過剰なため |
| 入力仕様の完全な理解 | Mockの目的から外れるため |
| OpenAI API呼び出し | MVP初期では外部APIを使わないため |
| Amazon Bedrock呼び出し | Phase 4以降の候補のため |
| RAG | MVPでは不要なため |
| ファイル解析 | ファイルアップロードを扱わないため |
| プロンプトテンプレート管理 | 初期は固定ロジックで十分なため |
| 生成結果のスコアリング | MVPでは不要なため |
| トークン数・料金計算 | 外部LLM APIを使わないため |

---

## 5. 入力仕様

LLM Mockサービスは、Backend APIから以下の入力を受け取ります。

```json
{
  "title": "注文登録APIのテスト設計",
  "target_type": "api",
  "test_level": "integration",
  "input_text": "注文情報を受け取り、注文テーブルと注文明細テーブルに登録するAPI。注文登録時に在庫引当APIを呼び出す。",
  "supplemental_notes": "在庫引当失敗時は注文登録を行わず、エラーレスポンスを返す。"
}
```

---

## 6. 入力項目

| 項目 | 型 | 必須 | 内容 |
|---|---|---:|---|
| `title` | string | 任意 | テスト設計タイトル |
| `target_type` | string | 必須 | テスト対象種別 |
| `test_level` | string | 必須 | テストレベル |
| `input_text` | string | 必須 | 仕様メモ |
| `supplemental_notes` | string | 任意 | 補足事項 |

---

## 7. `target_type` の想定値

| 値 | 表示名 | 生成観点の特徴 |
|---|---|---|
| `screen` | 画面 | 入力チェック、表示制御、エラーメッセージ、権限 |
| `api` | API | リクエスト、レスポンス、ステータスコード、DB更新、外部連携 |
| `batch` | バッチ | 実行条件、対象データ、再実行、ログ、異常終了 |
| `db` | DB更新 | 登録、更新、削除、整合性、排他、トランザクション |
| `external` | 外部連携 | タイムアウト、リトライ、エラー応答、疎通、ログ |
| `other` | その他 | 共通的な正常系、異常系、確認事項 |

---

## 8. `test_level` の想定値

| 値 | 表示名 | 生成観点の特徴 |
|---|---|---|
| `unit` | 単体テスト | 単一機能・単一処理の入力値と戻り値を重視 |
| `integration` | 結合テスト | API、DB、外部連携、画面間連携を重視 |
| `system` | システムテスト | 業務シナリオ、運用、性能、リカバリを重視 |
| `acceptance` | 受入テスト | 利用者観点、業務要件、受入条件を重視 |

---

## 9. 出力仕様

LLM Mockは、以下の構造のJSONを返します。

```json
{
  "summary": "注文登録APIに対するテスト観点とテストケース案です。",
  "viewpoints": [
    {
      "category": "正常系",
      "items": [
        "必須項目をすべて指定した場合に処理が成功すること",
        "複数明細を含む注文情報が正しく処理されること"
      ]
    },
    {
      "category": "異常系",
      "items": [
        "必須項目が未入力の場合にエラーとなること",
        "不正なコード値が指定された場合にエラーとなること"
      ]
    }
  ],
  "test_cases": [
    {
      "case_no": "TC-001",
      "title": "正常なデータ登録",
      "precondition": "必要なマスタデータが登録済みである",
      "steps": [
        "正常な入力データを送信する",
        "レスポンス内容を確認する",
        "DB登録内容を確認する"
      ],
      "expected_result": "処理が成功し、期待するデータが登録される",
      "priority": "High"
    }
  ],
  "additional_questions": [
    "エラー発生時のメッセージ仕様を確認する必要があります。",
    "外部連携失敗時のリカバリ方針を確認する必要があります。"
  ]
}
```

---

## 10. 出力項目

### 10.1 `summary`

生成結果の概要です。

| 項目 | 内容 |
|---|---|
| 型 | string |
| 用途 | 画面表示、Markdown出力 |
| 例 | `注文登録APIに対するテスト観点とテストケース案です。` |

`title` が入力されている場合は、タイトルを利用して概要文を作成します。  
未入力の場合は、`target_type` の表示名を使って概要文を作成します。

---

### 10.2 `viewpoints`

テスト観点の一覧です。

| 項目 | 内容 |
|---|---|
| 型 | array |
| 用途 | テスト観点表示、Markdown出力 |

要素の構造は以下です。

| 項目 | 型 | 内容 |
|---|---|---|
| `category` | string | 観点カテゴリ |
| `items` | array | 観点の箇条書き |

---

### 10.3 `test_cases`

テストケース案の一覧です。

| 項目 | 内容 |
|---|---|
| 型 | array |
| 用途 | テストケース表、Markdown出力 |

要素の構造は以下です。

| 項目 | 型 | 内容 |
|---|---|---|
| `case_no` | string | テストケース番号 |
| `title` | string | テストケース名 |
| `precondition` | string | 前提条件 |
| `steps` | array | テスト手順 |
| `expected_result` | string | 期待結果 |
| `priority` | string | 優先度 |

---

### 10.4 `additional_questions`

追加確認事項の一覧です。

| 項目 | 内容 |
|---|---|
| 型 | array |
| 用途 | 仕様確認事項、Markdown出力 |

仕様が曖昧になりやすい点、実装前・テスト設計前に確認すべき点を出力します。

---

## 11. 観点カテゴリ

MVPでは、以下のカテゴリを基本とします。

| カテゴリ | 内容 |
|---|---|
| 正常系 | 正しい入力・通常フローで期待通り処理されるか |
| 異常系 | 不正入力、存在しないデータ、エラー応答時の確認 |
| 境界値 | 数値、日付、文字数、件数などの境界条件 |
| 入力チェック | 必須、形式、桁数、文字種など |
| DB更新確認 | 登録、更新、削除、整合性、トランザクション |
| 外部連携確認 | タイムアウト、リトライ、異常応答、疎通 |
| 権限確認 | 権限別の操作可否、参照可否 |
| ログ確認 | 正常時・異常時のログ出力 |
| リカバリ観点 | 失敗時の再実行、ロールバック、復旧 |
| 性能観点 | 件数増加、応答時間、処理時間 |

すべてのカテゴリを毎回出力する必要はありません。  
`target_type` と `test_level` に応じて、必要なカテゴリを選択します。

---

## 12. `target_type` 別の生成方針

### 12.1 `screen`

画面仕様向けの観点を生成します。

主なカテゴリ：

- 正常系
- 異常系
- 入力チェック
- 境界値
- 権限確認
- 表示確認

観点例：

- 必須項目をすべて入力した場合に登録・更新が成功すること
- 必須項目が未入力の場合にエラーメッセージが表示されること
- 入力文字数の上限値・下限値で期待通り制御されること
- 権限のないユーザーが操作できないこと

---

### 12.2 `api`

API仕様向けの観点を生成します。

主なカテゴリ：

- 正常系
- 異常系
- 入力チェック
- レスポンス確認
- DB更新確認
- 外部連携確認

観点例：

- 正常なリクエストを送信した場合に期待するレスポンスが返ること
- 必須項目が未指定の場合にエラーレスポンスが返ること
- ステータスコードが仕様通りであること
- DB更新内容が期待通りであること
- 外部連携失敗時に適切なエラーとなること

---

### 12.3 `batch`

バッチ処理向けの観点を生成します。

主なカテゴリ：

- 正常系
- 異常系
- 対象データ確認
- 再実行確認
- ログ確認
- リカバリ観点

観点例：

- 対象データが存在する場合に正常終了すること
- 対象データが存在しない場合の終了ステータスが仕様通りであること
- 異常データが含まれる場合にエラー処理されること
- 異常終了後に再実行できること
- 処理件数やエラー内容がログに出力されること

---

### 12.4 `db`

DB更新処理向けの観点を生成します。

主なカテゴリ：

- 正常系
- 異常系
- DB更新確認
- 整合性確認
- 排他確認
- トランザクション確認

観点例：

- 登録対象データが正しく登録されること
- 更新対象データが正しく更新されること
- 存在しないデータを更新しようとした場合にエラーとなること
- 関連テーブルとの整合性が保たれること
- 異常発生時にロールバックされること

---

### 12.5 `external`

外部連携処理向けの観点を生成します。

主なカテゴリ：

- 正常系
- 異常系
- 外部連携確認
- タイムアウト確認
- リトライ確認
- ログ確認

観点例：

- 外部システムが正常応答した場合に処理が成功すること
- 外部システムがエラー応答した場合に適切にエラー処理されること
- タイムアウト時に仕様通りのリトライまたはエラー処理が行われること
- 連携失敗時に必要なログが出力されること

---

### 12.6 `other`

分類が難しい処理向けの共通観点を生成します。

主なカテゴリ：

- 正常系
- 異常系
- 入力チェック
- 追加確認事項

観点例：

- 通常条件で期待通り処理されること
- 不正な条件でエラーとなること
- 仕様上の前提条件が満たされていない場合の動作を確認すること

---

## 13. `test_level` 別の生成方針

### 13.1 `unit`

単体テスト向けの観点を強めます。

重視する観点：

- 入力値
- 戻り値
- 分岐条件
- 例外処理
- 境界値

---

### 13.2 `integration`

結合テスト向けの観点を強めます。

重視する観点：

- API呼び出し
- DB更新
- 外部連携
- 画面間連携
- トランザクション
- エラー伝播

---

### 13.3 `system`

システムテスト向けの観点を強めます。

重視する観点：

- 業務シナリオ
- 複数機能連携
- 運用観点
- 性能観点
- 障害時のリカバリ

---

### 13.4 `acceptance`

受入テスト向けの観点を強めます。

重視する観点：

- 利用者観点
- 業務要件
- 受入条件
- 表示文言
- 操作手順
- 業務ルールとの一致

---

## 14. 生成ロジック概要

MVPでは、以下のような単純なロジックで生成します。

```text
1. 入力値を受け取る
2. title が未入力の場合は自動タイトルを使用する
3. target_type に応じて基本観点セットを選択する
4. test_level に応じて追加観点を選択する
5. summary を作成する
6. viewpoints を作成する
7. test_cases を作成する
8. additional_questions を作成する
9. 固定JSON構造で返却する
```

---

## 15. 擬似コード

```python
def generate_test_design(request):
    title = request.title or generate_default_title()

    base_viewpoints = get_base_viewpoints(request.target_type)
    level_viewpoints = get_level_viewpoints(request.test_level)

    viewpoints = merge_viewpoints(base_viewpoints, level_viewpoints)

    result = {
        "summary": build_summary(title, request.target_type),
        "viewpoints": viewpoints,
        "test_cases": build_test_cases(request.target_type, request.test_level),
        "additional_questions": build_additional_questions(request.target_type),
    }

    return result
```

---

## 16. Markdown生成との関係

LLM Mockは、まず生成結果JSONを返します。

Markdownは、生成結果JSONと入力情報をもとに `markdown_builder` などの別処理で作成します。

```text
LLM Mock
↓
生成結果JSON
↓
Markdown Builder
↓
Markdown文字列
```

Markdown生成をMockサービス内に直接埋め込まない理由は以下です。

- JSON生成とMarkdown生成の責務を分けるため
- 将来OpenAI APIに差し替えてもMarkdown変換を再利用できるため
- テストしやすくするため
- Frontend表示とMarkdown出力の両方に対応しやすくするため

---

## 17. 想定ファイル構成

Backend実装時は、以下のような構成を想定します。

```text
backend/
  app/
    services/
      llm_mock.py
      markdown_builder.py
    schemas/
      test_design.py
```

ファイルの責務は以下です。

| ファイル | 役割 |
|---|---|
| `llm_mock.py` | 入力値をもとに生成結果JSONを返す |
| `markdown_builder.py` | 生成結果JSONをMarkdown文字列へ変換する |
| `schemas/test_design.py` | リクエスト・レスポンスの型定義 |

実際のファイル構成は実装時に調整してよいものとします。

---

## 18. テスト方針

LLM Mockは、pytestで以下を確認します。

| テスト観点 | 内容 |
|---|---|
| 正常系 | 有効な入力で生成結果JSONが返る |
| target_type別 | `screen`、`api`、`batch`、`db`、`external`、`other` で観点が切り替わる |
| test_level別 | `unit`、`integration`、`system`、`acceptance` で観点が切り替わる |
| 決定論的動作 | 同じ入力に対して同じ出力を返す |
| JSON構造 | `summary`、`viewpoints`、`test_cases`、`additional_questions` が存在する |
| Markdown変換 | JSONからMarkdownが生成できる |

---

## 19. テストケース例

### 19.1 API向けMock生成

入力：

```json
{
  "title": "注文登録APIのテスト設計",
  "target_type": "api",
  "test_level": "integration",
  "input_text": "注文情報を受け取り、注文テーブルと注文明細テーブルに登録するAPI。",
  "supplemental_notes": "在庫引当処理は外部API連携で行う。"
}
```

期待する確認内容：

- `summary` が存在する
- `viewpoints` に正常系が含まれる
- `viewpoints` に異常系が含まれる
- `viewpoints` にDB更新確認が含まれる
- `viewpoints` に外部連携確認が含まれる
- `test_cases` が1件以上存在する
- `additional_questions` が1件以上存在する

---

### 19.2 バッチ向けMock生成

入力：

```json
{
  "title": "日次売上集計バッチのテスト設計",
  "target_type": "batch",
  "test_level": "system",
  "input_text": "日次で売上データを集計し、売上サマリテーブルを更新するバッチ。",
  "supplemental_notes": "異常終了時はログを確認し、原因を取り除いたうえで再実行する。"
}
```

期待する確認内容：

- `viewpoints` に対象データ確認が含まれる
- `viewpoints` にログ確認が含まれる
- `viewpoints` にリカバリ観点が含まれる
- `test_cases` が1件以上存在する
- `additional_questions` に再実行や異常終了時の確認事項が含まれる

---

### 19.3 画面向けMock生成

入力：

```json
{
  "title": "ログイン画面のテスト設計",
  "target_type": "screen",
  "test_level": "acceptance",
  "input_text": "ユーザーIDとパスワードを入力してログインする画面。",
  "supplemental_notes": "認証失敗時はエラーメッセージを表示する。"
}
```

期待する確認内容：

- `viewpoints` に入力チェックが含まれる
- `viewpoints` にエラーメッセージ確認が含まれる
- `viewpoints` に権限確認が含まれる
- `test_cases` が1件以上存在する
- `additional_questions` にアカウントロックや認証失敗時の仕様確認が含まれる

---

## 20. セキュリティ・守秘義務上の注意

LLM Mockは外部APIを呼び出さないため、入力内容が外部サービスに送信されることはありません。

ただし、入力内容と生成結果はSQLiteに保存されます。

そのため、以下の情報は入力しません。

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

動作確認には、必ず架空データまたはマスキング済みデータを使用します。

---

## 21. 将来のOpenAI API / Bedrock連携に向けた考慮

将来、LLM MockをOpenAI APIやAmazon Bedrockに差し替える場合に備えて、以下を意識します。

| 観点 | 方針 |
|---|---|
| 入力形式 | Mockと外部LLMで同じ入力情報を使えるようにする |
| 出力形式 | 外部LLM利用時も同じJSON構造に整形する |
| Provider切替 | `llm_provider` で `mock` / `openai` / `bedrock` を区別できるようにする |
| Model保存 | `llm_model` に使用モデル名を保存できるようにする |
| Markdown変換 | LLMにMarkdownを直接出させず、JSONからBackend側で変換する方針を維持する |
| コスト管理 | 外部LLM利用時は回数制限や利用ログを検討する |
| セキュリティ | 外部送信前に注意書きとマスキング方針を明確にする |

---

## 22. MVP完了条件

LLM MockのMVP完了条件は以下です。

- 外部LLM APIを呼び出さずに生成結果JSONを返せる
- `target_type` に応じて観点が一部切り替わる
- `test_level` に応じて観点が一部切り替わる
- 同じ入力に対して同じ出力を返す
- `summary`、`viewpoints`、`test_cases`、`additional_questions` を含む
- Markdown変換に利用できる構造になっている
- pytestで主要な生成結果を検証できる
- 将来OpenAI APIやBedrockに差し替えやすい構成になっている