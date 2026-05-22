# Markdown出力設計メモ

## 1. 目的

本ドキュメントは、「業務系SE向け AIテスト設計支援ツール」の Phase 1：ローカルMVP におけるMarkdown出力仕様を整理するものです。

Phase 1では、LLM Mockが生成したテスト設計結果JSONを、Markdown形式に変換して画面表示・コピー・履歴保存できるようにします。

Markdown出力の目的は、生成結果を以下の用途に再利用しやすくすることです。

- テスト設計メモのたたき台
- GitHub Issuesへの貼り付け
- README / docsへの貼り付け
- 面談時のデモ説明
- 将来のExcel出力やテンプレート出力への拡張

## 更新メモ

本ドキュメントは、ローカルMVP総合動作確認後の実装状態に合わせて、APIパス、入力項目名、`target_type` / `test_level` のコード値を更新しています。

- 生成API: `POST /test-designs/generate`
- 履歴一覧API: `GET /test-designs/histories`
- 履歴詳細API: `GET /test-designs/histories/{history_id}`
- 入力項目: `title`、`target_type`、`test_level`、`spec_text`、`supplement`
- `target_type`: `screen`、`api`、`batch`、`db`、`external`
- `test_level`: `unit`、`integration`、`system`

---

## 2. Markdown出力方針

MVPにおけるMarkdown出力方針は以下です。

- Backend側でMarkdown文字列を生成する
- Frontendでは生成済みMarkdownを表示・コピーする
- Markdownは履歴データとしてSQLiteに保存する
- 履歴詳細では保存済みMarkdownを表示する
- MarkdownはGitHub上で読みやすい形式にする
- 表の中に長文を詰め込みすぎない
- 手順などの長い内容は箇条書きで表示する
- 生成結果は最終成果物ではなく、テスト設計のたたき台として扱う
- セキュリティ・守秘義務上の注意事項を含める

---

## 3. Markdown生成タイミング

Markdownは、テスト設計生成APIの処理内で生成します。

対象API：

```text
POST /test-designs/generate
```

処理の流れ：

```text
入力値バリデーション
↓
LLM Mockで生成結果JSONを作成
↓
生成結果JSONと入力情報からMarkdownを作成
↓
生成結果JSONとMarkdownをSQLiteへ保存
↓
レスポンスとして返却
```

履歴詳細表示時にはMarkdownを再生成せず、保存済みの `result_markdown` を利用します。

---

## 4. Markdown生成元データ

Markdownは、以下のデータをもとに生成します。

### 4.1 入力情報

| 項目 | 内容 |
|---|---|
| `title` | テスト設計タイトル |
| `target_type` | テスト対象種別 |
| `test_level` | テストレベル |
| `spec_text` | 仕様メモ |
| `supplement` | 補足事項 |

### 4.2 生成結果JSON

| 項目 | 内容 |
|---|---|
| `summary` | 生成結果の概要 |
| `viewpoints` | テスト観点一覧 |
| `test_cases` | テストケース案 |
| `additional_questions` | 追加確認事項 |

### 4.3 メタ情報

| 項目 | 内容 |
|---|---|
| `llm_provider` | MVPでは `mock` |
| `llm_model` | MVPでは `mock-v1` |
| `created_at` | 生成日時 |

---

## 5. Markdown全体構成

MVPのMarkdown出力は、以下の構成とします。

```text
# テスト設計結果

## 入力情報

## 仕様メモ

## 補足事項

## 概要

## テスト観点

## テストケース案

## 追加確認事項

## 生成情報

## 注意事項
```

補足事項が未入力の場合は、`## 補足事項` を省略してもよいものとします。

---

## 6. Markdown出力例

以下は、Markdown出力の例です。

```markdown
# テスト設計結果

## 入力情報

- タイトル: 注文登録APIのテスト設計
- テスト対象種別: API
- テストレベル: 結合テスト

## 仕様メモ

注文情報を受け取り、注文テーブルと注文明細テーブルに登録するAPI。注文登録時に在庫引当APIを呼び出す。

## 補足事項

在庫引当失敗時は注文登録を行わず、エラーレスポンスを返す。

## 概要

注文登録APIに対するテスト観点とテストケース案です。

## テスト観点

### 正常系

- 必須項目をすべて指定した場合に処理が成功すること
- 複数明細を含む注文情報が正しく処理されること

### 異常系

- 必須項目が未入力の場合にエラーとなること
- 在庫引当APIが失敗した場合に注文登録されないこと

### DB更新確認

- 注文テーブルに注文ヘッダ情報が登録されること
- 注文明細テーブルに明細情報が登録されること

## テストケース案

### TC-001: 正常な注文登録

- 前提条件: 有効な顧客情報と商品情報が存在する
- 優先度: High

#### 手順

1. 正常な注文情報を送信する
2. レスポンス内容を確認する
3. DB登録内容を確認する

#### 期待結果

注文登録が成功し、注文IDが返却される。

## 追加確認事項

- 在庫引当失敗時のエラーコード仕様を確認する必要があります。
- 注文登録後の通知処理有無を確認する必要があります。

## 生成情報

- 生成方式: mock
- モデル: mock-v1
- 生成日時: 2026-05-21T10:00:00

## 注意事項

この出力はAIによるテスト設計支援結果です。
最終的なテスト観点・期待結果は、実際の仕様書、設計書、業務ルールに基づいて確認してください。

顧客名、個人情報、APIキー、パスワード、本番環境情報、業務機密を含む情報は入力しないでください。
必要に応じて、架空データへの置き換えやマスキングを行ってから利用してください。
```

---

## 7. 各セクション仕様

## 7.1 タイトル

Markdownの先頭には、固定で以下を出力します。

```markdown
# テスト設計結果
```

MVPでは、入力タイトルをH1にしません。

理由：

- 出力形式を固定できる
- 履歴ごとのMarkdown構成が揃う
- タイトルは入力情報として扱える

---

## 7.2 入力情報

入力情報には、以下を出力します。

```markdown
## 入力情報

- タイトル: 注文登録APIのテスト設計
- テスト対象種別: API
- テストレベル: 結合テスト
```

`target_type` と `test_level` は、英字コードではなく日本語表示名に変換します。

### target_type表示名

| 値 | 表示名 |
|---|---|
| `screen` | 画面 |
| `api` | API |
| `batch` | バッチ |
| `db` | DB更新 |
| `external` | 外部連携 |

### test_level表示名

| 値 | 表示名 |
|---|---|
| `unit` | 単体テスト |
| `integration` | 結合テスト |
| `system` | システムテスト |

---

## 7.3 仕様メモ

仕様メモには、ユーザーが入力した `spec_text` を出力します。

```markdown
## 仕様メモ

注文情報を受け取り、注文テーブルと注文明細テーブルに登録するAPI。
```

入力文が長い場合でも、MVPではそのまま出力します。

ただし、Markdown表示が崩れないように、必要に応じて前後の空白は除去します。

---

## 7.4 補足事項

補足事項には、ユーザーが入力した `supplement` を出力します。

```markdown
## 補足事項

在庫引当失敗時は注文登録を行わず、エラーレスポンスを返す。
```

補足事項が未入力の場合は、このセクションを省略してもよいものとします。

---

## 7.5 概要

概要には、生成結果JSONの `summary` を出力します。

```markdown
## 概要

注文登録APIに対するテスト観点とテストケース案です。
```

---

## 7.6 テスト観点

テスト観点には、生成結果JSONの `viewpoints` を出力します。

入力JSON例：

```json
{
  "viewpoints": [
    {
      "category": "正常系",
      "items": [
        "必須項目をすべて指定した場合に処理が成功すること",
        "複数明細を含む注文情報が正しく処理されること"
      ]
    }
  ]
}
```

Markdown出力例：

```markdown
## テスト観点

### 正常系

- 必須項目をすべて指定した場合に処理が成功すること
- 複数明細を含む注文情報が正しく処理されること
```

カテゴリは `###` 見出しとして出力します。  
観点は箇条書きで出力します。

---

## 7.7 テストケース案

テストケース案には、生成結果JSONの `test_cases` を出力します。

MVPでは、テストケース案をMarkdown表ではなく、見出しと箇条書き中心で出力します。

理由：

- 手順が複数行になるため、表に入れると崩れやすい
- GitHub上で読みやすい
- コピー後の編集がしやすい
- 将来Excel出力に変換しやすい

入力JSON例：

```json
{
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
      "expected_result": "注文登録が成功し、注文IDが返却される。",
      "priority": "High"
    }
  ]
}
```

Markdown出力例：

```markdown
## テストケース案

### TC-001: 正常な注文登録

- 前提条件: 有効な顧客情報と商品情報が存在する
- 優先度: High

#### 手順

1. 正常な注文情報を送信する
2. レスポンス内容を確認する
3. DB登録内容を確認する

#### 期待結果

注文登録が成功し、注文IDが返却される。
```

---

## 7.8 追加確認事項

追加確認事項には、生成結果JSONの `additional_questions` を出力します。

入力JSON例：

```json
{
  "additional_questions": [
    "在庫引当失敗時のエラーコード仕様を確認する必要があります。",
    "注文登録後の通知処理有無を確認する必要があります。"
  ]
}
```

Markdown出力例：

```markdown
## 追加確認事項

- 在庫引当失敗時のエラーコード仕様を確認する必要があります。
- 注文登録後の通知処理有無を確認する必要があります。
```

追加確認事項は、仕様確認や設計レビュー時に使う想定です。

---

## 7.9 生成情報

生成情報には、生成方式・モデル・生成日時を出力します。

```markdown
## 生成情報

- 生成方式: mock
- モデル: mock-v1
- 生成日時: 2026-05-21T10:00:00
```

MVPでは `mock` 固定ですが、将来OpenAI APIやBedrockへ拡張した際に説明しやすくするため、生成情報を含めます。

---

## 7.10 注意事項

Markdown末尾には、以下の注意事項を出力します。

```markdown
## 注意事項

この出力はAIによるテスト設計支援結果です。
最終的なテスト観点・期待結果は、実際の仕様書、設計書、業務ルールに基づいて確認してください。

顧客名、個人情報、APIキー、パスワード、本番環境情報、業務機密を含む情報は入力しないでください。
必要に応じて、架空データへの置き換えやマスキングを行ってから利用してください。
```

このセクションは省略しません。

理由：

- AI出力をそのまま最終成果物にしないことを明確にするため
- 守秘義務・セキュリティ方針を明示するため
- ポートフォリオとして業務利用時の注意を説明しやすくするため

---

## 8. Markdown生成処理の責務

Markdown生成処理は、LLM Mockとは分離します。

想定ファイル：

```text
backend/app/services/markdown_builder.py
```

責務：

- 入力情報をMarkdownへ変換する
- 生成結果JSONをMarkdownへ変換する
- 表示名変換を行う
- 注意事項を付与する
- Markdown文字列を返す

LLM Mockの責務：

```text
入力情報をもとに生成結果JSONを返す
```

Markdown Builderの責務：

```text
入力情報 + 生成結果JSON + 生成情報をMarkdown文字列へ変換する
```

責務を分ける理由：

- MockからOpenAI APIへ差し替えてもMarkdown生成を再利用できる
- pytestで個別にテストしやすい
- Frontend側の実装を単純にできる
- 出力形式の変更をBackend側に閉じ込められる

---

## 9. Markdown生成ロジック概要

Markdown生成の処理概要は以下です。

```text
1. 入力情報を受け取る
2. 生成結果JSONを受け取る
3. target_type を日本語表示名に変換する
4. test_level を日本語表示名に変換する
5. 入力情報セクションを作成する
6. 仕様メモセクションを作成する
7. 補足事項があれば補足事項セクションを作成する
8. 概要セクションを作成する
9. テスト観点セクションを作成する
10. テストケース案セクションを作成する
11. 追加確認事項セクションを作成する
12. 生成情報セクションを作成する
13. 注意事項セクションを作成する
14. Markdown文字列として返す
```

---

## 10. 擬似コード

```python
def build_markdown(input_data, result_json, metadata):
    lines = []

    lines.append("# テスト設計結果")
    lines.append("")

    lines.extend(build_input_section(input_data))
    lines.extend(build_spec_section(input_data.spec_text))

    if input_data.supplement:
        lines.extend(build_supplemental_section(input_data.supplement))

    lines.extend(build_summary_section(result_json["summary"]))
    lines.extend(build_viewpoints_section(result_json["viewpoints"]))
    lines.extend(build_test_cases_section(result_json["test_cases"]))
    lines.extend(build_additional_questions_section(result_json["additional_questions"]))
    lines.extend(build_metadata_section(metadata))
    lines.extend(build_notice_section())

    return "\n".join(lines)
```

---

## 11. Markdownエスケープ方針

MVPでは、厳密なMarkdownエスケープ処理は作り込みすぎません。

ただし、最低限以下を考慮します。

| 対象 | 方針 |
|---|---|
| 前後の空白 | `strip()` で除去 |
| 改行 | 入力された改行を基本的に維持 |
| Markdown記号 | MVPでは原則そのまま扱う |
| 表形式 | 手順などの長文を表に入れないことで崩れを防ぐ |
| HTML | MVPではサニタイズの作り込みは行わないが、画面表示時にHTMLとして解釈しない |

Frontendでは、MarkdownをHTMLとして直接レンダリングせず、まずはテキストまたは安全なMarkdown表示として扱います。

---

## 12. Markdownコピー方針

Frontendでは、APIレスポンスの `result_markdown` をコピー対象にします。

コピー対象：

```text
result_markdown
```

コピー操作：

```text
Markdownをコピー
```

コピー成功時の表示：

```text
コピーしました
```

コピー失敗時の表示：

```text
コピーに失敗しました。手動で選択してコピーしてください。
```

MVPでは、Markdown編集機能は作成しません。

---

## 13. 履歴保存方針

生成時に作成したMarkdown文字列は、SQLiteの `result_markdown` に保存します。

対象テーブル：

```text
test_design_histories
```

対象カラム：

```text
result_markdown
```

履歴詳細画面では、保存済みの `result_markdown` を表示します。

保存済みJSONからMarkdownを再生成しない理由：

- 生成時点の出力をそのまま保持するため
- Markdown仕様変更による過去履歴の表示差分を避けるため
- 実装を単純にするため

---

## 14. MVPでは対応しないこと

Phase 1の初期MVPでは、以下は対応しません。

| 対象 | 理由 |
|---|---|
| Markdownテンプレート編集 | 初期MVPでは固定形式で十分なため |
| 複数テンプレート切替 | 実装範囲が広がるため |
| Excel出力 | Phase 4以降の拡張候補のため |
| PDF出力 | MVPの目的から外れるため |
| MarkdownからHTMLへの高度な変換 | 表示・コピーが中心のため |
| Markdownのリアルタイム編集 | 初期MVPでは不要なため |
| 生成済みMarkdownの再生成 | 仕様変更時の扱いが複雑になるため |
| Mermaid図出力 | MVPでは過剰なため |

---

## 15. テスト方針

Markdown生成処理は、pytestで以下を確認します。

| テスト観点 | 内容 |
|---|---|
| 正常系 | 有効な入力と生成結果JSONからMarkdownが生成される |
| 入力情報 | タイトル、対象種別、テストレベルが含まれる |
| 仕様メモ | 入力した仕様メモが含まれる |
| 補足事項あり | 補足事項セクションが出力される |
| 補足事項なし | 補足事項セクションを省略できる |
| テスト観点 | viewpointsのカテゴリと項目が出力される |
| テストケース | case_no、title、steps、expected_resultが出力される |
| 追加確認事項 | additional_questionsが出力される |
| 生成情報 | provider、model、created_atが出力される |
| 注意事項 | AI出力の注意と機密情報入力禁止の注意が含まれる |

---

## 16. テストケース例

### 16.1 補足事項あり

入力：

```json
{
  "title": "注文登録APIのテスト設計",
  "target_type": "api",
  "test_level": "integration",
  "spec_text": "注文情報を受け取り、注文テーブルに登録するAPI。",
  "supplement": "在庫引当失敗時はエラーを返す。"
}
```

期待する確認内容：

- `# テスト設計結果` が含まれる
- `## 入力情報` が含まれる
- `注文登録APIのテスト設計` が含まれる
- `API` が含まれる
- `結合テスト` が含まれる
- `## 仕様メモ` が含まれる
- `## 補足事項` が含まれる
- `## 注意事項` が含まれる

---

### 16.2 補足事項なし

入力：

```json
{
  "title": "ログイン画面のテスト設計",
  "target_type": "screen",
  "test_level": "integration",
  "spec_text": "ユーザーIDとパスワードを入力してログインする画面。",
  "supplement": ""
}
```

期待する確認内容：

- `# テスト設計結果` が含まれる
- `ログイン画面のテスト設計` が含まれる
- `画面` が含まれる
- `受入テスト` が含まれる
- `## 仕様メモ` が含まれる
- `## 補足事項` は省略されてもよい
- `## 注意事項` が含まれる

---

## 17. 将来の拡張候補

MVP完了後、必要に応じて以下を検討します。

| 拡張 | 内容 |
|---|---|
| Markdownテンプレート管理 | 出力形式をテンプレートとして管理する |
| Excel出力 | テストケース案を表形式で出力する |
| Markdownプレビュー強化 | MarkdownをHTMLプレビューする |
| 観点別テンプレート | 画面/API/バッチ別に出力フォーマットを変える |
| 日本語・英語切替 | 出力言語を切り替える |
| 生成済みMarkdown再生成 | 保存済みJSONから最新テンプレートで再生成する |
| GitHub Issue形式出力 | GitHub Issueに貼りやすい形式を追加する |

---

## 18. セキュリティ・守秘義務上の注意

Markdownには、入力された仕様メモや補足事項が含まれます。

そのため、以下の情報は入力・出力しません。

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

MarkdownをREADME、docs、GitHub Issues、技術記事などへ貼り付ける場合も、架空データまたはマスキング済みデータであることを確認します。

---

## 19. 完了条件

Markdown出力機能の完了条件は以下です。

- 生成結果JSONからMarkdown文字列を作成できる
- 入力情報がMarkdownに含まれる
- 仕様メモがMarkdownに含まれる
- 補足事項がある場合はMarkdownに含まれる
- テスト観点がMarkdownに含まれる
- テストケース案がMarkdownに含まれる
- 追加確認事項がMarkdownに含まれる
- 生成情報がMarkdownに含まれる
- 注意事項がMarkdownに含まれる
- 生成されたMarkdownをSQLiteに保存できる
- FrontendでMarkdownを表示できる
- FrontendでMarkdownをコピーできる
- 架空データで動作確認できる
