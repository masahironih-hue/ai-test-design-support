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

## Markdownコピー機能の確認

生成結果の Markdown 表示欄にある `Markdownをコピー` ボタンから、生成された Markdown 文字列をクリップボードへコピーできます。

### 確認手順

1. Backend を起動する
2. Frontend を起動する
3. 仕様入力フォームに架空のサンプル仕様を入力する
4. テスト設計結果を生成する
5. Markdown形式の生成結果が表示されることを確認する
6. `Markdownをコピー` ボタンを押す
7. `Markdownをコピーしました。` と表示されることを確認する
8. メモ帳などに貼り付けて、Markdown本文がコピーされていることを確認する

### 注意事項

- 実案件の仕様、顧客情報、個人情報、APIキー、パスワード、業務機密は入力しない
- 動作確認には架空のサンプル仕様のみを使用する
- `.env.local`、`node_modules/`、`.next/` は Git 管理対象に含めない

## 履歴一覧画面の確認

Backend と Frontend を起動した状態で、以下を確認する。

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

### 確認内容

- 画面下部に生成履歴一覧が表示される
- 履歴がない場合は「まだ生成履歴はありません。」と表示される
- Backend が停止している場合は履歴取得エラーが表示される
- テスト設計を生成後、「再読み込み」を押すと履歴一覧に表示される
- 履歴ID、タイトル、対象種別、テストレベル、作成日時が表示される

### 注意事項

確認には架空のサンプル仕様のみを使用する。
顧客情報、個人情報、APIキー、パスワード、本番環境情報、業務機密は入力しない。