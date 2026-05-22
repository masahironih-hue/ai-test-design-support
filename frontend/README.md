## Backend API 接続確認

Frontend の仕様入力フォームから、Backend の `POST /test-designs/generate` API を呼び出し、生成結果を画面表示できるようにした。

### 前提

Backend と Frontend を別々の PowerShell で起動する。

```text
Backend : http://localhost:8000
Frontend: http://localhost:3000
```

### 環境変数

Frontend では Backend API の Base URL を以下で管理する。

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

`.env.local` は Git 管理対象外とする。  
設定例として `.env.example` のみ Git 管理対象に含める。

### Backend 起動

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

### Frontend 起動

```powershell
cd frontend
pnpm dev
```

### 画面確認

ブラウザで以下にアクセスする。

```text
http://localhost:3000
```

架空のサンプル仕様を入力し、以下を確認する。

- API呼び出し中の状態が表示される
- API成功時に生成結果が表示される
- テスト観点が表示される
- テストケースが表示される
- Markdown形式の生成結果が表示される
- API失敗時にエラーが表示される

### CORS

Frontend と Backend は別ポートで起動するため、Backend 側で CORS を設定する。

許可オリジンはローカル開発用に限定する。

```text
http://localhost:3000
```

`allow_origins=["*"]` は使用しない。

### 確認コマンド

Frontend:

```powershell
cd frontend
pnpm lint
pnpm build
```

Backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest
```

### Git 管理対象外

以下は Git 管理対象に含めない。

```text
.env
.env.local
node_modules/
.next/
.venv/
__pycache__/
.pytest_cache/
*.db
*.sqlite
*.sqlite3
```