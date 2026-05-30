# ローカル環境構築手順

このドキュメントでは、AI Test Design Support のローカル開発環境構築手順を整理する。

## 前提

初期MVPでは、Windows + PowerShell + VS Code を前提にする。

Docker、AWS、認証、課金、マルチテナント構成は初期段階では使用しない。  
まずはローカルで動作する最小構成を優先する。

## 推奨環境

- OS: Windows 10 / Windows 11
- Shell: PowerShell
- Editor: VS Code
- Git: 2.x
- Python: 3.13.x
- Node.js: 24 LTS
- Package Manager: pnpm
- DB: SQLite
- LLM: 初期はMock
- Docker: 初期MVPでは使用しない
- AWS: ローカルMVP完成後に検討

## 確認済み環境

現時点の開発PCでは、以下を確認済み。

- Git: 2.53.0.windows.3
- VS Code: 1.117.0
- Python: 3.13.13
- pip: 26.0.1
- Node.js: v24.15.0
- npm: 11.12.1
- Corepack: 0.34.6
- pnpm: 11.1.3
- Git email: GitHub noreply メールを使用

## バージョン確認コマンド

```powershell
git --version
code --version

py -0p
py -3.13 --version
py -3.13 -m pip --version

node -v
npm -v
corepack --version
pnpm -v

git config --global user.name
git config --global user.email
git config --global core.autocrlf
```

## Python環境

本プロジェクトでは Python 3.13.x を使用する。

Windows環境では、Visual Studio付属の古いPythonやPython 2系が残っている場合がある。  
そのため、仮想環境作成時は明示的にPython 3.13を指定する。

```powershell
py -3.13 -m venv .venv
```

仮想環境の有効化:

```powershell
.\.venv\Scripts\Activate.ps1
```

pip更新:

```powershell
python -m pip install --upgrade pip
```

## Node.js / pnpm環境

本プロジェクトでは Node.js 24 LTS を使用する。

パッケージマネージャは pnpm を推奨する。

確認:

```powershell
node -v
npm -v
corepack --version
pnpm -v
```

## PowerShellでnpmが実行できない場合

Node.jsをインストール後、PowerShellで以下のようなエラーが出る場合がある。

```powershell
npm : このシステムではスクリプトの実行が無効になっているため、
C:\Program Files\nodejs\npm.ps1 を読み込むことができません。
```

この場合、PowerShellの実行ポリシーを確認する。

```powershell
Get-ExecutionPolicy -List
```

CurrentUserスコープで変更する。

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

その後、PowerShellを開き直して確認する。

```powershell
npm -v
```

一時的な確認だけであれば、以下でも確認できる場合がある。

```powershell
npm.cmd -v
```

## corepack enable が EPERM になる場合

Windows環境では、Corepackが `C:\Program Files\nodejs` 配下に `pnpm` / `pnpx` のプロキシを作成しようとして、通常ユーザー権限では失敗する場合がある。

例:

```powershell
Internal Error: EPERM: operation not permitted, open 'C:\Program Files\nodejs\pnpx'
Error: EPERM: operation not permitted, open 'C:\Program Files\nodejs\pnpx'
```

この場合、PowerShellを管理者として実行し、以下を実行する。

```powershell
corepack enable
```

その後、通常のPowerShellで確認する。

```powershell
pnpm -v
```

## 開発ディレクトリ

OneDrive配下は避ける。

推奨:

```txt
C:\dev\ai-test-design-support
```

避ける:

```txt
C:\Users\ユーザー名\OneDrive\...
C:\Users\ユーザー名\Desktop\...
```

理由:

- `node_modules`
- `.venv`
- SQLiteファイル
- 一時ファイル

などが同期対象になると、ファイルロックや同期遅延が起きやすいため。

## ローカル起動方針

初期MVPでは、バックエンドとフロントエンドを別ターミナルで起動する。

Backend予定:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

Frontend予定:

```powershell
cd frontend
pnpm dev
```

現時点ではまだ実装前のため、上記は予定手順とする。

## Docker / AWS の扱い

### Docker

初期MVPではDockerを使用しない。

理由:

- Windows環境ではDocker Desktop / WSL2 / 仮想化設定などの論点が増える
- 初期MVPではPython venv + Node.jsの直接起動で十分
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

## セキュリティ注意事項

本プロジェクトでは、以下の情報を使用しない。

- 顧客情報
- 個人情報
- 本業の実コード
- 実ログ
- 実設計書
- APIキー
- パスワード
- アクセストークン
- 本番環境情報
- 業務機密

開発・デモには、サンプル仕様・架空データのみを使用する。

`.env` はGit管理対象外とし、`.env.example` のみ管理する。

Backendの生成方式は `APP_LLM_PROVIDER` で切り替える。

- 未指定時または `APP_LLM_PROVIDER=mock` はMock生成を使う
- `APP_LLM_PROVIDER=openai` の場合のみOpenAI APIを呼び出す
- OpenAI API利用時は `OPENAI_API_KEY` が必要
- `OPENAI_MODEL` は `gpt-5.4-nano` / `gpt-5.4-mini` のallowlist内で指定する
- `OPENAI_MAX_OUTPUT_TOKENS` と `OPENAI_TIMEOUT_SECONDS` を環境変数で設定できる
- OpenAI API利用時は利用料が発生する可能性がある
- モデル変更時はOpenAI公式の料金・品質・速度・利用制限を確認する
- CIではOpenAI APIを呼び出さない

詳細は `docs/security-policy.md` を参照する。
