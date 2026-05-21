## Backend ローカル起動手順

### 前提

- Python 3.13.x
- Windows PowerShell

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

### Backend起動

```powershell
python -m uvicorn app.main:app --reload
```

### ヘルスチェック

```powershell
curl http://127.0.0.1:8000/health
```

期待レスポンス:

```json
{
  "status": "ok",
  "service": "ai-test-design-support-backend"
}
```

### テスト実行

```powershell
python -m pytest
```


## LLM Mock API 動作確認

### Backend起動

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

### API確認

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

### テスト実行

```powershell
python -m pytest
```

### 注意事項

このAPIは外部LLMを呼び出さないMock実装です。  
実案件の顧客情報、個人情報、APIキー、パスワード、業務機密は入力しないでください。

## SQLite 履歴保存

Backend 起動時に SQLite のテーブルを作成します。

開発用DBファイルは以下に作成されます。

```text
backend/app.db
```

DBファイルは Git 管理対象外です。

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

### 主なAPI

```text
POST /test-designs/generate
GET /test-designs/histories
GET /test-designs/histories/{history_id}
```

### 生成・保存APIの確認例

APIリクエストでは、`target_type` と `test_level` に表示名ではなくコード値を指定します。

```powershell
$body = @{
  title = "架空の在庫引当API"
  target_type = "api"
  test_level = "integration"
  spec_text = "商品IDと数量を受け取り、在庫引当を行う架空のAPI。"
  supplement = "外部倉庫システムとの連携はMockとする。"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/test-designs/generate" `
  -Method Post `
  -ContentType "application/json; charset=utf-8" `
  -Body $body
```

### 履歴一覧APIの確認例

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/test-designs/histories" `
  -Method Get |
ConvertTo-Json -Depth 10
```

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

### テスト実行

```powershell
python -m pytest
```

テストでは一時SQLite DBを使用し、開発用DBとは分離します。

### Git管理上の注意

SQLite DBファイルや `.env` は Git 管理対象外にします。

```gitignore
# Environment
.env

# SQLite
*.db
*.sqlite
*.sqlite3
```

commit 前に以下を確認します。

```powershell
git status --short
```

```powershell
git ls-files | Select-String -Pattern "\.db$|\.sqlite$|\.sqlite3$|\.env$"
```

何も表示されなければ、DBファイルや `.env` は Git 管理対象に含まれていません。