# Frontend README

## 概要

このディレクトリは、「業務系SE向け AIテスト設計支援ツール」の Frontend です。

Next.js / React / TypeScript / pnpm / App Router を使用し、Backend API と連携して以下を行います。

- 仕様入力フォームの表示
- 入力値の状態管理
- 最小バリデーション
- Backend API 呼び出し
- テスト設計生成結果の表示
- Markdown形式の生成結果表示
- Markdownコピー
- 履歴一覧表示
- 履歴詳細表示
- 保存済みMarkdownコピー
- セキュリティ注意事項表示
- 日時のJST表示

---

## 前提

- Node.js
- pnpm
- Windows PowerShell

以下のコマンドは、リポジトリ直下から実行する前提です。

---

## 初回セットアップ

```powershell
cd frontend
pnpm install
```

---

## 環境変数

Frontend では、Backend API の Base URL を以下で管理します。

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

設定例は以下に配置します。

```text
frontend/.env.example
```

ローカル開発では、以下のように `.env.local` を作成して使用します。

```text
frontend/.env.local
```

注意事項：

- `.env.local` はローカル開発用です
- `.env.local` は Git 管理対象外です
- `.env.example` のみ Git 管理対象に含めます
- APIキー、パスワード、アクセストークンなどの秘密情報を GitHub に上げないでください
- 現時点では外部LLM APIキーは不要です

---

## Backend / Frontend 起動

Backend と Frontend は、別々の PowerShell で起動します。

```text
Backend : http://localhost:8000
Frontend: http://localhost:3000
```

---

### Backend 起動

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

---

### Frontend 起動

別の PowerShell を開き、以下を実行します。

```powershell
cd frontend
pnpm dev
```

起動後、ブラウザで以下にアクセスします。

```text
http://localhost:3000
```

---


## 静的export

AWS S3 + CloudFront 配信用に、Next.js の静的exportを行います。

```powershell
pnpm build
```

`next.config.ts` で `output: "export"` を設定しているため、build後に `out/` が生成されます。

```powershell
Test-Path .\out
Get-ChildItem .\out
```

`out/` はビルド成果物のため、Git管理対象には含めません。

CloudFront配信環境では、Backend APIはまだAWS化していないため、画面表示は確認できますが、生成API・履歴APIを利用するにはローカルBackendまたは後続のAWS Backend構成が必要です。

---

## Backend API 接続確認

Frontend の仕様入力フォームから、Backend の `POST /test-designs/generate` API を呼び出し、生成結果を画面表示できることを確認します。

### 確認内容

架空のサンプル仕様を入力し、以下を確認します。

- 仕様入力フォームが表示される
- 必須項目未入力時にエラーが表示される
- API呼び出し中の状態が表示される
- API成功時に生成結果が表示される
- テスト観点が表示される
- テストケースが表示される
- Markdown形式の生成結果が表示される
- API失敗時にエラーが表示される

---

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

---

## 履歴一覧画面の確認

Backend と Frontend を起動した状態で、生成履歴一覧を確認します。

### 確認内容

- 画面下部に生成履歴一覧が表示される
- 履歴がない場合は「まだ生成履歴はありません。」と表示される
- Backend が停止している場合は履歴取得エラーが表示される
- テスト設計を生成後、「再読み込み」を押すと履歴一覧に表示される
- 履歴ID、タイトル、対象種別、テストレベル、作成日時が表示される
- 対象種別とテストレベルが日本語ラベルで表示される

---

## 履歴詳細画面の確認

Backend と Frontend を起動した状態で、履歴一覧から履歴詳細を確認します。

現時点のローカルMVPでは、専用の `/histories/[id]` ページは作らず、同一ページ内で履歴詳細を表示します。

### 確認内容

- 履歴一覧から任意の履歴を選択できる
- 選択した履歴の詳細が表示される
- 履歴ID、タイトル、対象種別、テストレベル、作成日時が表示される
- 仕様本文が表示される
- 補足事項が表示される
- テスト観点が表示される
- テストケースが表示される
- Markdown形式の生成結果が表示される
- 保存済みMarkdownをコピーできる
- 履歴詳細取得中の状態が表示される
- 履歴詳細取得に失敗した場合はエラーが表示される
- 履歴未選択時は、履歴を選択する案内が表示される

---

## 日時表示

履歴一覧・履歴詳細の作成日時は、Frontend側でJST表示に変換します。

方針は以下です。

- Backend / DB: UTC基準
- Frontend表示: JST

例：

```text
UTC: 2026/05/22 07:35
JST: 2026/05/22 16:35
```

---

## CORS

Frontend と Backend は別ポートで起動するため、Backend 側で CORS を設定します。

許可オリジンはローカル開発用に限定します。

```text
http://localhost:3000
```

`allow_origins=["*"]` は使用しません。

---

## 確認コマンド

### Frontend

```powershell
cd frontend
pnpm lint
pnpm build
```

### Backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest
```

---

## Git 管理対象外

以下は Git 管理対象に含めません。

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

`.gitignore` には、少なくとも以下を含めます。

```gitignore
# Environment
.env
.env.local

# Frontend
node_modules/
.next/

# Python
.venv/
__pycache__/
.pytest_cache/

# SQLite
*.db
*.sqlite
*.sqlite3
```

commit 前に以下を確認します。

```powershell
git status --short
```

環境変数ファイル、ビルド成果物、依存関係ディレクトリ、SQLite DBファイルが Git 管理対象に含まれていないことを確認します。

```powershell
git ls-files | Select-String -Pattern "\.env$|\.env\.local$|node_modules|\.next|\.db$|\.sqlite$|\.sqlite3$"
```

何も表示されなければ、対象ファイルは Git 管理対象に含まれていません。

---

## セキュリティ・守秘義務上の注意

動作確認には、架空のサンプル仕様のみを使用してください。

以下の情報は入力しないでください。

```text
顧客名、個人情報、APIキー、パスワード、本番環境情報、業務機密を含む情報は入力しないでください。
必要に応じてマスキングしてから利用してください。
```

開発・動作確認では、以下を徹底します。

- 実案件の仕様は使用しない
- 顧客情報は使用しない
- 個人情報は使用しない
- APIキー、パスワード、アクセストークンは入力しない
- 本番環境情報は入力しない
- 業務機密は入力しない
- `.env.local` は Git 管理対象に含めない
- `node_modules/`、`.next/` は Git 管理対象に含めない

---

## Frontendで扱わないもの

現時点のローカルMVPでは、以下は扱いません。

- 認証
- 課金
- マルチテナント
- ファイルアップロード
- Excel出力
- Markdownレンダリングライブラリ導入
- 履歴検索
- 履歴編集
- 履歴削除
- 専用の履歴詳細ページ作成
- AWSデプロイ
- OpenAI API連携
- Amazon Bedrock連携

まずはローカル環境で、仕様入力から生成結果表示、Markdownコピー、履歴一覧、履歴詳細確認までを確認できる状態を優先します。