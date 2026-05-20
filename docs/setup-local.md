- OS: Windows 10 / Windows 11
- Shell: PowerShell
- Editor: VS Code
- Git: 2.x
- Python: 3.13.x 推奨
- Node.js: 24 LTS 推奨
- Package Manager: pnpm 推奨
- Backend: FastAPI
- Frontend: Next.js / React / TypeScript
- DB: SQLite
- LLM: 初期はMock
- Docker: 初期MVPでは使用しない
- AWS: ローカルMVP完成後に検討

## 環境確認結果

### 確認済み

- Git: `2.53.0.windows.3`
- VS Code: `1.117.0`
- Node.js: `v24.15.0`
- Corepack: `0.34.6`

### 要対応

- Python が `3.6.6` になっている
  - Visual Studio 付属の古い Python が参照されている
  - 本プロジェクトでは使用しない
  - Python 3.13.x を別途導入する

- npm が PowerShell の実行ポリシーでブロックされている
  - `npm.ps1` が実行できない状態
  - CurrentUser スコープで実行ポリシー変更が必要

- pnpm が未認識
  - Corepack 有効化後に確認する
  - `corepack enable` 実行時に権限エラーが出る場合あり
  
## 必須ツール

- Git
- GitHubアカウント
- VS Code
- Python 3.13.x
- pip
- venv
- Node.js 24 LTS
- npm
- pnpm
- SQLite

## 実装開始後に使用するツール

- FastAPI
- Uvicorn
- SQLModel または SQLAlchemy
- pytest
- Next.js
- React
- TypeScript

## 推奨ツール

- Ruff
- ESLint
- Prettier
- GitHub CLI

## 後回しでよいツール

- Docker Desktop
- WSL2本格利用
- AWS CLI
- AWS CDK
- DynamoDB Local
- OpenAI APIキー
- Amazon Bedrock関連設定

git --version
code --version

python --version
py --version
py -0p
python -m pip --version

node -v
npm -v
pnpm -v
corepack --version

where git
where code
where python
where py
where node
where npm

## Python環境の注意点

Windows環境では、Visual Studio 付属の古い Python が参照される場合がある。

例:

```powershell
Python 3.6.6
pip 18.0 from C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python36_86\...


---

## 6. Node.js / npm / pnpm の注意点

```md
## Node.js環境の注意点

本プロジェクトでは Node.js 24 LTS を推奨する。

確認コマンド:

```powershell
node -v
npm -v
corepack --version


---

## 7. PowerShellで npm が実行できない場合

```md
## PowerShellでnpmが実行できない場合

Node.jsをインストール後、PowerShellで以下のようなエラーが出る場合がある。

```powershell
npm : このシステムではスクリプトの実行が無効になっているため、
C:\Program Files\nodejs\npm.ps1 を読み込むことができません。


---

## 8. corepack enable が EPERM になる場合

```md
## Windowsで `corepack enable` がEPERMになる場合

Windows環境では、Corepackが `C:\Program Files\nodejs` 配下に `pnpm` / `pnpx` のプロキシを作成しようとして、通常ユーザー権限では失敗する場合がある。

例:

```powershell
Internal Error: EPERM: operation not permitted, open 'C:\Program Files\nodejs\pnpx'
Error: EPERM: operation not permitted, open 'C:\Program Files\nodejs\pnpx'


---

## 9. pnpm導入方針

```md
## pnpm導入方針

本プロジェクトでは、フロントエンドのパッケージマネージャとして pnpm を推奨する。

理由:

- Next.js / React 開発で利用しやすい
- npmより高速・省容量になりやすい
- `pnpm-lock.yaml` により依存関係を固定しやすい
- ポートフォリオとして現代的な構成に見せやすい

基本方針:

```powershell
corepack enable
pnpm -v


---

## 10. Windows環境での注意点

```md
## Windows環境での注意点

### PowerShellを標準にする

本プロジェクトのREADMEでは、Windows + PowerShell を標準手順として記載する。

理由:

- Windows利用者に説明しやすい
- Git Bash / WSL / CMD の差異を避けられる
- Python venv の有効化手順を統一しやすい

### OneDrive配下は避ける

開発ディレクトリは OneDrive 同期対象外に置く。

推奨例:

```txt
C:\dev\ai-test-design-support

---

## 11. Git設定メモ

```md
## Git設定

Gitのユーザー名とメールアドレスを確認する。

```powershell
git config --global user.name
git config --global user.email


---

## 12. セキュリティ・守秘義務メモ

```md
## セキュリティ・守秘義務

本プロジェクトでは、以下の情報を使用しない。

- 顧客名
- 個人情報
- 本業の実コード
- 実ログ
- 実設計書
- APIキー
- パスワード
- アクセストークン
- 本番環境情報
- 業務機密
- 契約上公開できない情報

開発・デモには、サンプル仕様・架空データのみを使用する。

`.env` はGit管理対象にしない。

`.env.example` のみGit管理対象にする。

## 環境変数管理方針

実値を含む `.env` はGit管理対象外とする。

Git管理するのは `.env.example` のみ。

例:

```env
OPENAI_API_KEY=
DATABASE_URL=sqlite:///./app.db
APP_ENV=local


---

## 14. Docker / AWS の扱い

```md
## Docker / AWS の扱い

### Docker

初期MVPでは Docker は使用しない。

理由:

- Windows環境では Docker Desktop / WSL2 / 仮想化設定などの論点が増える
- 初期MVPでは Python venv + Node.js の直接起動で十分
- まずローカルで動く状態を優先する

Dockerは、必要になった段階で環境再現性向上のために検討する。

### AWS

AWSはローカルMVP完成後に検討する。

初期段階では以下を使わない。

- NAT Gateway
- ALB
- RDS
- ECS Fargate
- Bedrock
- WAF
- Secrets Manager

理由:

- 個人開発ではコスト管理が重要
- 常時稼働リソースを避ける
- まずローカルで説明可能なMVPを作る

## ローカル構成方針

初期MVPでは以下の構成を想定する。

```txt
ai-test-design-support/
  backend/
    FastAPI
    SQLite
    LLM Mock
    pytest

  frontend/
    Next.js
    React
    TypeScript

  docs/
    setup-local.md
    development-policy.md
    security-policy.md

  README.md
  .gitignore
  .env.example
  

---

## 16. Codex利用時の注意点

```md
## Codex利用方針

Codexは開発補助ツールとして使用する。

CodexをMVPアプリの機能には含めない。

### Codexに依頼してよい作業

- ファイル作成
- テスト追加
- lint修正
- 型エラー修正
- README更新
- リファクタ
- PR前のセルフレビュー

### Codexに渡してはいけない情報

- 本業の実コード
- 実ログ
- 顧客名
- 個人情報
- APIキー
- パスワード
- 本番環境情報
- 実際の設計書
- 業務機密

### Codex用プロンプトに含める注意書き

```txt
このプロジェクトでは実データ・顧客情報・APIキー・業務機密を使用しない。
サンプルデータ・架空仕様のみを前提に実装する。
.env は作成してよいが、実値は入れない。
.env.example のみGit管理対象にする。


---

## 17. 次に実施すべき確認作業

```md
## 次に実施する作業

1. Python 3.13.x を導入する
2. `py -0p` でPythonの導入状況を確認する
3. `py -3.13 --version` を確認する
4. `py -3.13 -m pip --version` を確認する
5. PowerShellの実行ポリシーを確認する
6. npm が実行できる状態にする
7. Corepack を有効化する
8. pnpm が実行できる状態にする
9. Gitの `user.name` / `user.email` を確認・設定する
10. 開発用ディレクトリを `C:\dev\...` 配下に作成する

## 現時点の決定案

- OS: Windows
- Shell: PowerShell
- Editor: VS Code
- Python: 3.13.x
- Node.js: 24 LTS
- Package Manager: pnpm
- Backend仮想環境: venv
- DB: SQLite
- LLM: 初期はMock
- Docker: 初期MVPでは使わない
- WSL2: 任意。まずはWindows + PowerShellで進める
- AWS CLI / CDK: Phase 2まで後回し
- OpenAI API: 初期MVPでは呼ばない

