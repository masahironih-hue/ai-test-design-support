# Phase 1 実装前チェックリスト

## 1. 目的

本ドキュメントは、「業務系SE向け AIテスト設計支援ツール」の Phase 1：ローカルMVP 実装に入る前の確認事項を整理するものです。

Phase 1では、以下の流れをローカル環境で動作させることを目的とします。

```text
仕様入力
↓
LLM Mockによるテスト観点生成
↓
生成結果表示
↓
Markdownコピー
↓
履歴保存
↓
履歴一覧・履歴詳細確認
```

本チェックリストの目的は、実装開始前に以下を明確にすることです。

- MVPスコープが固まっていること
- 設計メモが最低限そろっていること
- 実装順序が明確であること
- GitHub Issuesに分解できること
- 守秘義務・セキュリティ上のリスクを避けられること
- 過剰設計に進まないこと

---

## 2. 設計docs確認

Phase 1実装前に、以下のdocsが作成されていることを確認します。

| ファイル | 状態 | 内容 |
|---|---|---|
| `docs/mvp-requirements.md` | 確認済み | MVPの目的、作る機能、作らない機能 |
| `docs/api-design.md` | 確認済み | API一覧、リクエスト、レスポンス |
| `docs/db-design.md` | 確認済み | SQLiteテーブル設計 |
| `docs/llm-mock-design.md` | 確認済み | LLM Mockの入出力、生成方針 |
| `docs/screen-design.md` | 確認済み | 画面構成、入力項目、画面遷移 |
| `docs/markdown-output.md` | 確認済み | Markdown出力形式 |
| `docs/sample-specs.md` | 確認済み | 架空サンプル仕様 |
| `docs/security-policy.md` | 確認済み | セキュリティ・守秘義務方針 |
| `docs/development-policy.md` | 確認済み | 開発運用方針 |
| `docs/setup-local.md` | 確認済み | ローカル環境構築メモ |

確認後、状態を以下のように更新します。

```text
未確認 → 確認済み
```

---

## 3. MVPスコープ確認

### 3.1 MVPで作るもの

以下はPhase 1のMVP対象とします。

| 対象 | 確認 |
|---|---|
| FastAPIの最小構成 | 確認済み |
| `/health` API | 確認済み |
| SQLite接続 | 確認済み |
| 履歴保存テーブル | 確認済み |
| LLM Mockサービス | 確認済み |
| Markdown生成処理 | 確認済み |
| テスト設計生成API | 確認済み |
| 履歴一覧API | 確認済み |
| 履歴詳細API | 確認済み |
| Next.js最小構成 | 確認済み |
| 仕様入力フォーム | 確認済み |
| セキュリティ注意書き表示 | 確認済み |
| サンプル仕様選択 | 確認済み |
| 生成結果表示 | 確認済み |
| Markdownコピー | 確認済み |
| 履歴一覧画面 | 確認済み |
| 履歴詳細画面 | 確認済み |
| README / docs更新 | 確認済み |

---

### 3.2 MVPで作らないもの

以下はPhase 1初期MVPでは作りません。

| 対象 | 理由 | 確認 |
|---|---|---|
| OpenAI API連携 | Mockで先に画面/API/DBを固めるため | 確認済み |
| Amazon Bedrock連携 | Phase 4以降の候補のため | 確認済み |
| AWSデプロイ | Phase 2で扱うため | 確認済み |
| Docker必須化 | 初期環境構築負荷を下げるため | 確認済み |
| 認証 | ローカルMVPでは不要なため | 確認済み |
| 課金 | MVPの目的から外れるため | 確認済み |
| マルチテナント | 過剰設計となるため | 確認済み |
| ファイルアップロード | セキュリティリスクと実装範囲が増えるため | 確認済み |
| Excel出力 | Markdown出力後の拡張で十分なため | 確認済み |
| RAG | 初期MVPには不要なため | 確認済み |
| プロンプトテンプレート管理 | まずは固定Mockで十分なため | 確認済み |
| 履歴検索 | 初期履歴件数が少ない前提のため | 確認済み |
| 履歴編集 | 初期MVPでは不要なため | 確認済み |
| 履歴削除 | 初期MVPでは参照中心とするため | 確認済み |

---

## 4. 技術スタック確認

Phase 1では以下の技術スタックを使用します。

| 領域 | 技術 | 確認 |
|---|---|---|
| Backend | Python | 確認済み |
| Backend Framework | FastAPI | 確認済み |
| DB | SQLite | 確認済み |
| ORM | SQLModel優先 | 確認済み |
| Test | pytest | 確認済み |
| Frontend | Next.js | 確認済み |
| UI | React | 確認済み |
| Language | TypeScript | 確認済み |
| Package Manager | pnpm | 確認済み |
| AI / LLM | LLM Mock | 確認済み |
| Repository | GitHub | 確認済み |

MVPではAWS、Docker、外部LLM APIは必須にしません。

---

## 5. セキュリティ確認

Phase 1実装前に、以下を確認します。

| 確認項目 | 状態 |
|---|---|
| 本業の顧客情報を使用しない | 確認済み |
| 実在する顧客名を使用しない | 確認済み |
| 個人情報を使用しない | 確認済み |
| APIキーをGitHubに載せない | 確認済み |
| パスワードをGitHubに載せない | 確認済み |
| アクセストークンをGitHubに載せない | 確認済み |
| 本番環境情報を使用しない | 確認済み |
| 実際の設計書を使用しない | 確認済み |
| 実際のソースコードを使用しない | 確認済み |
| 実際の障害ログを使用しない | 確認済み |
| 業務機密を使用しない | 確認済み |
| サンプル仕様は架空データのみを使用する | 確認済み |
| SQLiteのDBファイルをGit管理対象外にする | 確認済み |
| `.env` をGit管理対象外にする | 確認済み |
| `.env.example` のみGit管理対象にする | 確認済み |
| 画面にセキュリティ注意書きを表示する | 確認済み |

---

## 6. Git管理確認

実装前に以下を確認します。

| 確認項目 | コマンド例 | 状態 |
|---|---|---|
| 現在のブランチを確認する | `git branch --show-current` | 確認済み |
| 作業差分を確認する | `git status` | 確認済み |
| docsがコミット済みである | `git log --oneline -5` | 確認済み |
| 不要ファイルが含まれていない | `git status --ignored` | 確認済み |
| `.env` が追跡されていない | `git ls-files .env` | 確認済み |
| DBファイルが追跡されていない | `git ls-files "*.db"` | 確認済み |

---

## 7. `.gitignore` 確認

Phase 1実装前に、`.gitignore` に以下が含まれていることを確認します。

```gitignore
# Environment variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/

# Node.js
node_modules/
.next/
dist/
build/

# SQLite database files
*.db
*.sqlite
*.sqlite3
backend/app.db
backend/data/*.db

# Logs
*.log
logs/
```

既存の `.gitignore` と重複する場合は、無理に重複追加せず、必要な項目が含まれていることを確認します。

---

## 8. GitHub Issues確認

Phase 1実装用に、以下のIssueを登録または整理します。

| 優先度 | Issue | 状態 |
|---:|---|---|
| 1 | `Docs: MVP要件定義を整理する` | 確認済み |
| 2 | `Backend: FastAPI最小構成を作成する` | 確認済み |
| 3 | `Backend: SQLite履歴保存の最小構成を作成する` | 確認済み |
| 4 | `Backend: LLM Mockサービスを作成する` | 確認済み |
| 5 | `Backend: テスト設計生成APIを作成する` | 確認済み |
| 6 | `Frontend: Next.js最小構成と入力フォームを作成する` | 確認済み |
| 7 | `Frontend: 生成結果表示とMarkdownコピーを作成する` | 確認済み |
| 8 | `Frontend: 履歴一覧・履歴詳細画面を作成する` | 確認済み |
| 9 | `Docs: ローカル起動手順とMVP説明を更新する` | 確認済み |

Issueラベル候補：

| ラベル | 用途 |
|---|---|
| `phase-1` | Phase 1対象 |
| `mvp` | MVP必須 |
| `backend` | Backend関連 |
| `frontend` | Frontend関連 |
| `docs` | ドキュメント関連 |
| `ai` | LLM Mock関連 |
| `priority-high` | 優先度高 |

---

## 9. 実装順序確認

Phase 1は、以下の順序で実装します。

| Step | 内容 | 状態 |
|---:|---|---|
| 1 | Backend最小構成を作成する | 確認済み |
| 2 | `/health` APIを作成する | 確認済み |
| 3 | SQLite接続と履歴テーブルを作成する | 確認済み |
| 4 | LLM Mockサービスを作成する | 確認済み |
| 5 | Markdown生成処理を作成する | 確認済み |
| 6 | テスト設計生成APIを作成する | 確認済み |
| 7 | 履歴一覧API・履歴詳細APIを作成する | 確認済み |
| 8 | Backendのpytestを作成する | 確認済み |
| 9 | Frontend最小構成を作成する | 確認済み |
| 10 | 仕様入力フォームを作成する | 確認済み |
| 11 | 生成結果表示とMarkdownコピーを作成する | 確認済み |
| 12 | 履歴一覧画面を作成する | 確認済み |
| 13 | 履歴詳細画面を作成する | 確認済み |
| 14 | サンプル仕様を画面に組み込む | 確認済み |
| 15 | README / docsを更新する | 確認済み |

---

## 10. Backend実装前確認

Backend実装に入る前に、以下を確認します。

| 確認項目 | 状態 |
|---|---|
| Backendディレクトリ方針が決まっている | 確認済み |
| FastAPIを使用する | 確認済み |
| SQLiteを使用する | 確認済み |
| SQLModelを優先候補とする | 確認済み |
| pytestを使用する | 確認済み |
| `/health` から作成する | 確認済み |
| 外部LLM APIはまだ使わない | 確認済み |
| APIキーは不要 | 確認済み |
| DBファイルはGit管理対象外 | 確認済み |

想定するBackend構成：

```text
backend/
  app/
    main.py
    api/
    db/
    models/
    schemas/
    services/
  tests/
```

---

## 11. Frontend実装前確認

Frontend実装に入る前に、以下を確認します。

| 確認項目 | 状態 |
|---|---|
| Next.jsを使用する | 確認済み |
| Reactを使用する | 確認済み |
| TypeScriptを使用する | 確認済み |
| pnpmを使用する | 確認済み |
| 初期画面は `/` とする | 確認済み |
| 履歴一覧は `/history` とする | 確認済み |
| 履歴詳細は `/history/[id]` とする | 確認済み |
| 複雑な状態管理ライブラリは使わない | 確認済み |
| サンプル仕様はFrontend定数で持つ | 確認済み |
| Markdownコピーを実装する | 確認済み |

想定するFrontend構成：

```text
frontend/
  app/
  components/
  lib/
  types/
```

---

## 12. 動作確認方針

Phase 1では、以下の動作確認を行います。

| 確認対象 | 確認内容 | 状態 |
|---|---|---|
| Backend | FastAPIが起動する | 確認済み |
| Backend | `/health` が正常応答する | 確認済み |
| Backend | テスト設計生成APIが正常応答する | 確認済み |
| Backend | SQLiteに履歴が保存される | 確認済み |
| Backend | 履歴一覧APIが正常応答する | 確認済み |
| Backend | 履歴詳細APIが正常応答する | 確認済み |
| Frontend | 生成画面が表示される | 確認済み |
| Frontend | セキュリティ注意書きが表示される | 確認済み |
| Frontend | サンプル仕様を選択できる | 確認済み |
| Frontend | 生成APIを呼び出せる | 確認済み |
| Frontend | 生成結果が表示される | 確認済み |
| Frontend | Markdownをコピーできる | 確認済み |
| Frontend | 履歴一覧が表示される | 確認済み |
| Frontend | 履歴詳細が表示される | 確認済み |

---

## 13. MVP完了条件

Phase 1のMVP完了条件は以下です。

| 完了条件 | 状態 |
|---|---|
| ローカルでBackendが起動できる | 確認済み |
| ローカルでFrontendが起動できる | 確認済み |
| 仕様入力フォームから生成処理を実行できる | 確認済み |
| LLM Mockによる生成結果が表示される | 確認済み |
| Markdown形式の出力をコピーできる | 確認済み |
| 生成結果がSQLiteに保存される | 確認済み |
| 履歴一覧を確認できる | 確認済み |
| 履歴詳細を確認できる | 確認済み |
| 架空サンプル仕様でデモできる | 確認済み |
| セキュリティ注意書きが画面に表示されている | 確認済み |
| READMEまたはdocsにローカル起動手順が記載されている | 確認済み |
| GitHub上でMVPの目的・構成・制約を説明できる | 確認済み |

---

## 14. 実装開始判定

以下を満たしたら、Phase 1実装に入ってよいものとします。

| 判定項目 | 状態 |
|---|---|
| MVPスコープが明確になっている | 確認済み |
| 作る機能・作らない機能が明確になっている | 確認済み |
| API設計が整理されている | 確認済み |
| DB設計が整理されている | 確認済み |
| LLM Mock仕様が整理されている | 確認済み |
| 画面設計が整理されている | 確認済み |
| Markdown出力仕様が整理されている | 確認済み |
| サンプル仕様が整理されている | 確認済み |
| セキュリティ方針が明確になっている | 確認済み |
| GitHub Issuesに分解できている | 確認済み |
| `.env` やDBファイルをGit管理しない方針が明確になっている | 確認済み |

すべて確認済みになったら、以下の実装スレッドへ進みます。

```text
[実装] Backend最小構成
```

---

## 15. 次に作成するスレッド

Phase 1の最初の実装スレッドは、以下とします。

```text
[実装] Backend最小構成
```

このスレッドでは、以下のみを扱います。

- Backendディレクトリ構成
- FastAPI最小構成
- `/health` API
- Backend起動確認
- pytest最小構成
- README / docsへの起動手順反映

このスレッドでは、以下はまだ扱いません。

- LLM Mock実装
- SQLite履歴保存
- Frontend実装
- OpenAI API連携
- AWS構成
- Docker構成

---

## 16. 実装開始時の注意

実装開始時は、最初から大きく作り込みすぎないようにします。

優先順位は以下です。

1. 起動すること
2. `/health` が返ること
3. テストが通ること
4. ディレクトリ構成が説明しやすいこと
5. 次のDB・LLM Mock実装につなげやすいこと

最初の実装では、アプリ全体を完成させようとせず、Backendの最小構成に限定します。
