# Backend README

## Backend ローカル起動手順

### 前提

- Python 3.13.x
- Windows PowerShell

以下のコマンドは、リポジトリ直下から実行する前提です。

---

## 初回セットアップ

### 仮想環境作成

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 依存関係インストール

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

---

## Backend起動

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

起動後、以下のURLでAPIが起動していることを確認します。

```text
http://127.0.0.1:8000
```

---

## ヘルスチェック

別のPowerShellを開き、以下を実行します。

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

期待レスポンス:

```json
{
  "status": "ok",
  "service": "ai-test-design-support-backend"
}
```

---

## テスト実行

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest
```

---

## LLM Mock API 動作確認

### 概要

`POST /test-designs/generate` に仕様情報を送信すると、LLM Provider によってテスト観点・テストケース・Markdown形式の生成結果を返却します。

デフォルトは `APP_LLM_PROVIDER=mock` で、外部LLM APIは呼び出しません。
任意機能として `APP_LLM_PROVIDER=openai` を指定した場合のみ OpenAI API を呼び出します。

- Mock生成: デフォルト
- OpenAI API連携: 任意機能
- Amazon Bedrock連携: 未実装
- CI / pytest: OpenAI APIを実呼び出ししない

OpenAI APIを利用する場合は、環境変数に以下を設定します。

```env
APP_LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5.4-nano
OPENAI_MAX_OUTPUT_TOKENS=1200
OPENAI_TIMEOUT_SECONDS=30
```

`OPENAI_MODEL` は `gpt-5.4-nano` / `gpt-5.4-mini` のallowlist内で切り替えます。
モデル変更時は、OpenAI公式のモデル・料金・品質・速度・利用制限を確認してください。
OpenAI API利用時は利用料が発生する可能性があります。

---

### Backend起動

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

---

### API確認

APIリクエストでは、`target_type` と `test_level` に表示名ではなくコード値を指定します。

#### `target_type`

```text
screen
api
batch
db
external
```

#### `test_level`

```text
unit
integration
system
```

確認例:

```powershell
$body = @{
  title = "ログイン画面"
  target_type = "screen"
  test_level = "integration"
  spec_text = "利用者IDとパスワードを入力し、認証に成功した場合はメニュー画面へ遷移する。認証に失敗した場合はエラーメッセージを表示する。"
  supplement = "業務系Webアプリのログイン機能を想定する。"
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/test-designs/generate" `
  -ContentType "application/json; charset=utf-8" `
  -Body $body
```

---

### 注意事項

デフォルトのMock生成では外部LLMを呼び出しません。
`APP_LLM_PROVIDER=openai` の場合、入力内容はOpenAI APIへ送信されます。

以下の情報は入力しないでください。

```text
顧客名、個人情報、APIキー、パスワード、本番環境情報、業務機密を含む情報は入力しないでください。
必要に応じてマスキングしてから利用してください。
```

動作確認には、架空のサンプル仕様のみを使用します。
`.env` / `.env.local` に記載した実値はGitHubへコミットしないでください。

---

## SQLite 履歴保存

Backend起動時にSQLiteのテーブルを作成します。

開発用DBファイルは以下に作成されます。

```text
backend/app.db
```

DBファイルはGit管理対象外です。

---

### 履歴保存の流れ

```text
POST /test-designs/generate
↓
LLM Mock によるテスト設計生成
↓
SQLite へ履歴保存
↓
GET /test-designs/histories で一覧取得
↓
GET /test-designs/histories/{history_id} で詳細取得
```

---

### 主なAPI

```text
POST /test-designs/generate
GET /test-designs/histories
GET /test-designs/histories/{history_id}
```

---

### 生成・保存APIの確認例

```powershell
$body = @{
  title = "架空の在庫引当API"
  target_type = "api"
  test_level = "integration"
  spec_text = "商品IDと数量を受け取り、在庫引当を行う架空のAPI。"
  supplement = "外部倉庫システムとの連携はMockとする。"
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/test-designs/generate" `
  -Method Post `
  -ContentType "application/json; charset=utf-8" `
  -Body $body
```

---

### 履歴一覧APIの確認例

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/test-designs/histories" `
  -Method Get |
ConvertTo-Json -Depth 10
```

---

### 履歴詳細APIの確認例

```powershell
$histories = @(Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/test-designs/histories" `
  -Method Get)

$historyId = $histories[0].id

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/test-designs/histories/$historyId" `
  -Method Get |
ConvertTo-Json -Depth 10
```

---

## SQLite DBの扱い

### 履歴保持

生成履歴はSQLite DBに保存されます。

Backendを再起動しても、既存の履歴は保持されます。

`init_db()` はテーブル作成用であり、既存の履歴データは削除しません。

---

### 開発用DBを初期化したい場合

開発中に履歴を初期化したい場合は、Backendを停止したうえで、開発用SQLite DBファイルを手動で削除します。

```text
backend/app.db
```

削除後にBackendを再起動すると、テーブルが再作成されます。

---

## テスト実行

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest
```

テストでは一時SQLite DBを使用し、開発用DBとは分離します。

---

## Git管理上の注意

以下はGit管理対象外にします。

```text
.env
.env.local
.venv/
__pycache__/
.pytest_cache/
*.db
*.sqlite
*.sqlite3
```

`.gitignore` には、少なくとも以下を含めます。

```gitignore
# Environment
.env
.env.local

# Python
.venv/
__pycache__/
.pytest_cache/

# SQLite
*.db
*.sqlite
*.sqlite3
```

---

## commit前の確認

commit前に、不要なファイルがGit管理対象に含まれていないことを確認します。

```powershell
git status --short
```

SQLite DBファイルや環境変数ファイルがGit管理対象に含まれていないことを確認します。

```powershell
git ls-files | Select-String -Pattern "\.db$|\.sqlite$|\.sqlite3$|(^|/)\.env$|(^|/)\.env\.local$|(^|/)\.venv/"
```

何も表示されなければ、DBファイル、環境変数ファイル、仮想環境ディレクトリはGit管理対象に含まれていません。

---

## Backendで扱わないもの

現時点のローカルMVPでは、以下は扱いません。

- OpenAI API連携の本格運用
- Amazon Bedrock連携
- AWSデプロイ
- 認証
- 課金
- マルチテナント
- ファイルアップロード
- Excel出力
- RAG

まずはローカル環境で、仕様入力からテスト設計生成、履歴保存、履歴取得までを確認できる状態を優先します。
