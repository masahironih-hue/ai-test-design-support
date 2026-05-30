# 業務系SE向け AIテスト設計支援ツール [![CI](https://github.com/masahironih-hue/ai-test-design-support/actions/workflows/ci.yml/badge.svg)](https://github.com/masahironih-hue/ai-test-design-support/actions/workflows/ci.yml)

## 概要

「業務系SE向け AIテスト設計支援ツール」は、機能概要や仕様メモを入力すると、テスト観点・テストケース・確認事項を生成するWebアプリケーションです。

業務系システム開発における、以下のようなテスト設計作業を支援することを目的としています。

- 仕様メモからテスト観点を洗い出す
- 正常系・異常系・境界値などの確認観点を整理する
- テストケース表のたたき台を作成する
- Markdown形式で生成結果をコピーし、設計メモやレビュー資料に転用しやすくする

本アプリは汎用チャットボットではなく、仕様入力からテスト設計出力までの流れに特化した、業務系SE向けのテスト設計支援ツールです。

---

## 開発目的

このプロジェクトは、個人開発のポートフォリオとして、以下を示すことを目的に開発しました。

- Python / FastAPI を用いたBackend API開発
- React / Next.js / TypeScript を用いたFrontend開発
- LLM Mockを維持しつつ、OpenAI APIによる実LLM生成モードを最小連携するAIアプリケーション設計
- 業務系システム開発経験を活かしたテスト設計支援の具体化
- AWS SAAの学習内容を、低コストなAWS Serverless構成として実装に落とし込むこと
- GitHub Actionsによる基本的なCI確認の整備
- README / docs / GitHub Releases を含むポートフォリオ成果物の整備

Phase 1：ローカルMVPでは、仕様入力、LLM Mockによる生成、Markdown表示・コピー、SQLite履歴保存、履歴一覧、履歴詳細まで実装・確認済みです。

Phase 2：AWS低コスト版では、S3 + CloudFront による Frontend静的配信、API Gateway HTTP API + Python Lambda + DynamoDB によるBackend API、CloudFront配信FrontendからAWS Backend APIへの接続まで実装し、画面上で生成・履歴保存・履歴一覧・履歴詳細まで確認済みです。検証後はコスト管理のため、不要なAWSリソースを削除する運用としています。

Phase 3：低コスト運用補強では、GitHub Actionsにより Backend pytest、Frontend lint / build、Infra cdk synth を自動確認するCIを整備しました。CIではAWS deploy / destroyやOpenAI API呼び出しは行いません。

Phase 4：OpenAI API最小連携では、既存のLLM Mockを維持したまま、`APP_LLM_PROVIDER=mock/openai` によるProvider切替を追加しました。デフォルトはMock生成で、`APP_LLM_PROVIDER=openai` の場合のみOpenAI APIを呼び出します。

ただし、本プロジェクトは個人開発ポートフォリオであり、商用SaaS運用、本番運用、高可用性構成、認証付きマルチテナント運用を目的としたものではありません。

---

## 現在の実装状況

### ローカルMVP

ローカルMVPでは、以下を実装・確認済みです。

| 区分 | 内容 |
|---|---|
| Backend | Python / FastAPI |
| Frontend | Next.js / React / TypeScript |
| DB | SQLite |
| LLM | LLM Mock / OpenAI API最小連携 |
| 生成方式 | `APP_LLM_PROVIDER=mock/openai` によるProvider切替 |
| デフォルト | `mock` |
| テスト | pytest / Frontend lint / Frontend build |

確認済みの範囲は以下です。

- 仕様入力
- LLM Mockによるテスト観点・テストケース生成
- OpenAI APIによる実LLM生成モードの最小連携
- 生成結果表示
- Markdownコピー
- SQLiteへの履歴保存
- 履歴一覧表示
- 履歴詳細表示
- 保存済みMarkdownコピー
- APIキー未設定時、不正Provider、不正モデル、APIエラー、タイムアウト時のエラー処理
- pytestではOpenAI APIを実呼び出ししない構成

### AWS低コスト版

AWS低コスト版では、以下を実装・確認済みです。

| 区分 | 内容 |
|---|---|
| Frontend | S3 + CloudFront による静的配信 |
| Backend API | API Gateway HTTP API + Python Lambda |
| 履歴保存 | DynamoDB |
| ログ | CloudWatch Logs |
| IaC | AWS CDK |

確認済みの範囲は以下です。

- S3 + CloudFront によるFrontend静的配信
- CloudFront OAC によるS3 private配信
- API Gateway HTTP API + Python Lambda によるBackend API
- DynamoDBによる履歴保存・一覧取得・詳細取得
- CloudFront配信FrontendからAWS Backend APIへの接続
- 画面上での生成・履歴保存・履歴一覧・履歴詳細確認
- 検証後のAWSリソース削除

AWS版Backendは、現時点ではMock生成API・履歴APIを対象とした低コスト検証構成です。AWS版へのOpenAI API組み込み、Amazon Bedrock連携、認証、課金、マルチテナント、商用SaaS運用、高可用性構成は未実装です。

---

## 主な機能

### ローカルMVP / OpenAI API最小連携

- 仕様入力フォーム
- テスト対象種別の選択
- テストレベルの選択
- LLM Mockによるテスト観点生成
- OpenAI APIによる実LLM生成モードの最小連携
- `APP_LLM_PROVIDER=mock/openai` によるProvider切替
- 未指定時は `mock` をデフォルトにする構成
- `APP_LLM_PROVIDER=openai` の場合のみOpenAI APIを呼び出す構成
- テストケース生成
- Markdown形式の生成結果表示
- Markdownコピー
- SQLiteへの履歴保存
- 履歴一覧表示
- 履歴詳細表示
- 保存済みMarkdownコピー
- セキュリティ注意事項表示
- 日時のJST表示

### AWS低コスト版

- AWS CDKによるインフラ管理
- S3 + CloudFront によるFrontend静的配信
- CloudFront OAC によるS3 private配信
- API Gateway HTTP API + Python Lambda によるBackend API
- DynamoDBによる履歴保存・一覧取得・詳細取得
- CloudWatch Logs保持期間7日方針
- CloudFront配信FrontendからAWS Backend APIへの接続
- 検証後に不要なAWSリソースを削除する運用

---

## 画面イメージ

Phase 1：ローカルMVPで実装した主要画面です。

画面キャプチャには、架空のログイン画面仕様をサンプルとして使用しています。

なお、画面キャプチャ作成時点ではLLM Mockによる生成結果を使用しています。現在のBackendでは、LLM Mockを維持したまま、環境変数によりOpenAI API生成モードへ切り替える最小連携にも対応しています。

### 仕様入力フォーム

機能概要や仕様メモ、テスト対象種別、テストレベル、補足事項を入力し、テスト設計生成を実行します。

![仕様入力フォーム](docs/images/phase1-local-mvp/01-top-form.png)

### テスト設計生成結果

入力された仕様をもとに、テスト観点、テストケース、Markdown形式の出力を生成します。

![テスト設計生成結果](docs/images/phase1-local-mvp/03-generated-result_01.png)

### 生成履歴一覧

生成したテスト設計結果はSQLiteに保存され、履歴一覧から確認できます。

作成日時は画面表示時にJSTへ変換しています。

![生成履歴一覧](docs/images/phase1-local-mvp/05-history-list.png)

### 生成履歴詳細

履歴一覧から選択した生成結果の詳細を確認できます。

保存済みの仕様本文、補足事項、テスト観点、テストケース、Markdown出力を再確認できます。

![生成履歴詳細](docs/images/phase1-local-mvp/06-history-detail_01.png)

---

## 技術スタック

### Local MVP / OpenAI API Minimal Integration

- Python 3.13.x
- FastAPI
- SQLAlchemy
- SQLite
- pytest
- Uvicorn
- Next.js
- React
- TypeScript
- pnpm
- App Router
- LLM Mock
- OpenAI API
- OpenAI Responses API

### AWS Low Cost Version

- AWS CDK
- Amazon S3
- Amazon CloudFront
- CloudFront Origin Access Control
- Amazon API Gateway HTTP API
- AWS Lambda
- Amazon DynamoDB
- Amazon CloudWatch Logs

### Development / Management

- Git / GitHub
- GitHub Issues
- GitHub Actions
- README / docs
- GitHub Releases

### Future Candidates

- Structured Outputs / JSON Schema指定
- プロンプト改善
- Amazon Bedrock連携
- AWS Lambda版OpenAI連携
- LLM Provider設計の拡張
- プロンプトテンプレート管理
- Excel出力
- 履歴検索 / 編集 / 削除
- ファイルアップロード
- RAG
- 認証
- 課金
- マルチテナント

---

## ディレクトリ構成

```text
ai-test-design-support/
├─ backend/
│  ├─ app/
│  ├─ tests/
│  ├─ pyproject.toml
│  └─ README.md
├─ frontend/
│  ├─ src/
│  ├─ package.json
│  ├─ .env.example
│  └─ README.md
├─ infra/
│  ├─ bin/
│  ├─ lib/
│  ├─ package.json
│  └─ cdk.json
├─ docs/
└─ README.md
```

---

## ローカル起動手順

詳細なローカル環境セットアップ手順は、[ローカル開発環境セットアップ](docs/setup-local.md) を参照してください。

### 前提

以下がインストール済みであることを前提とします。

- Python 3.13.x
- Node.js
- pnpm
- Git

---

### Backend起動

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

起動後、以下にアクセスして疎通確認します。

```text
http://localhost:8000/health
```

Backendのデフォルトは `APP_LLM_PROVIDER=mock` です。OpenAI APIを利用しない通常のローカル起動では、`OPENAI_API_KEY` は不要です。

---

### Frontend起動

別のPowerShellを開き、以下を実行します。

```powershell
cd frontend
pnpm.cmd dev
```

起動後、以下にアクセスします。

```text
http://localhost:3000
```

---

## AWS低コスト版

Phase 2では、AWS低コスト版として、Frontendを S3 + CloudFront で静的配信し、API Gateway HTTP API + Python Lambda + DynamoDB によるBackend APIへ接続する構成を追加しています。

構成概要は以下です。

- Next.js / React / TypeScript Frontend を静的export
- 静的ファイルをS3バケットへ配置
- S3バケットはPublic公開せず、CloudFront OAC経由で配信
- AWS CDKでS3 Bucket、S3 Bucket Policy、CloudFront Distribution、CloudFront OACを管理
- AWS CDKでAPI Gateway HTTP API、Python Lambda、DynamoDB、CloudWatch Logsを管理
- AWS上のBackend APIは `POST /test-designs/generate`、`GET /test-designs/histories`、`GET /test-designs/histories/{history_id}` に対応
- DynamoDBはオンデマンド課金、partition keyは `history_id`
- CloudWatch Logs保持期間は7日
- 既存VPC / EC2 / Security Group / Route 53 は使用・変更しない
- 検証後は `cdk destroy` により本プロジェクト用リソースを削除可能

AWS低コスト版では、CloudFront配信FrontendからAWS Backend APIを呼び出し、画面上で生成・履歴保存・履歴一覧・履歴詳細まで確認済みです。

ただし、本構成は個人開発向けの低コスト検証構成です。AWS版BackendへのOpenAI API組み込み、Amazon Bedrock連携、Cognito認証、本格API認証、課金、マルチテナント、商用SaaS運用、高可用性構成は未実装です。

READMEには、API Gateway URL、CloudFront DomainName、S3 Bucket名、DynamoDB Table名などの実値を掲載していません。

詳細は以下を参照してください。

- [AWS構成方針](docs/aws-architecture.md)
- [AWSデプロイ手順](docs/aws-deploy.md)
- [AWS削除手順](docs/aws-destroy.md)
- [AWS低コスト構成・料金見積もり](docs/aws-cost-estimate.md)
- [AWS Budgets・コスト制御](docs/aws-budget.md)
- [ローカルMVPとAWS低コスト版の差分](docs/aws-version-differences.md)

---

## AWS版の現在の対応範囲

AWS版では、現時点で以下まで対応しています。

| 区分 | 対応内容 |
|---|---|
| Frontend | S3 + CloudFront で静的配信 |
| Backend API | API Gateway HTTP API + Python Lambda でMock生成API・履歴APIに対応 |
| 履歴保存 | DynamoDB |
| 画面連携 | CloudFront配信FrontendからAWS Backend APIを呼び出し、生成・履歴保存・履歴一覧・履歴詳細まで確認済み |
| リソース運用 | 検証後はコスト管理のため削除する方針 |

AWS版は、AWS SAAで学習した内容を個人開発プロダクトへ低コストなServerless構成として適用したものです。

ローカルBackendではOpenAI APIによる実LLM生成モードを任意機能として最小連携していますが、AWS版BackendへのOpenAI API組み込みは未対応です。

本番運用、商用SaaS運用、認証、課金、マルチテナント、高可用性構成、Amazon Bedrock連携は未対応です。

---

## AI / LLM機能

本プロジェクトでは、初期MVPではLLM Mockを使用し、Phase 4でOpenAI APIによる実LLM生成モードを最小連携しました。

現在の生成方式は、環境変数 `APP_LLM_PROVIDER` で切り替えます。

| 設定値 | 内容 |
|---|---|
| `mock` | LLM Mockで生成する。デフォルト値 |
| `openai` | OpenAI APIを呼び出して生成する |

未指定時は `mock` として動作します。そのため、通常のローカル起動、テスト、CIではOpenAI APIキーなしで動作確認できます。

OpenAI APIを利用する場合は、`APP_LLM_PROVIDER=openai` と `OPENAI_API_KEY` を設定します。OpenAI API利用時は、APIキー管理、利用料金、入力データ、ログ出力に注意してください。

OpenAI API最小連携で対応している主な内容は以下です。

- `APP_LLM_PROVIDER=mock/openai` によるProvider切替
- 未指定時は `mock` をデフォルト
- 既存LLM Mock生成処理の維持
- `APP_LLM_PROVIDER=openai` の場合のみOpenAI APIを呼び出す構成
- OpenAI Responses APIによる最小連携
- `OPENAI_MODEL` の環境変数化
- `OPENAI_MODEL` allowlist制御
- `OPENAI_MAX_OUTPUT_TOKENS` による出力上限制御
- `OPENAI_TIMEOUT_SECONDS` によるタイムアウト制御
- APIキー未設定、不正Provider、不正モデル、APIエラー、タイムアウト時のエラー処理
- pytestではOpenAI APIを実呼び出ししない構成
- CIではOpenAI APIを呼び出さない方針
- 架空サンプル仕様によるOpenAI実API確認

現時点では、Structured Outputs / JSON Schema指定、Amazon Bedrock連携、RAG、AWS Lambda版OpenAI連携は未実装です。これらは必要性が高まった場合の検討対象です。

---

## 環境変数

Frontendでは、Backend APIの接続先として以下を使用します。

| 変数名 | 用途 | 例 |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Frontendから呼び出すBackend APIのBase URL | `http://localhost:8000` |

設定例は以下のファイルを参照してください。

- `frontend/.env.example`

ローカル開発では、必要に応じて以下のファイルを作成して使用します。

- `frontend/.env.local`

Backendでは、LLM Provider切替とOpenAI API利用時の設定として以下を使用します。

| 変数名 | 用途 | 備考 |
|---|---|---|
| `APP_LLM_PROVIDER` | 生成方式の切替 | `mock` または `openai`。未指定時は `mock` |
| `OPENAI_API_KEY` | OpenAI APIキー | `APP_LLM_PROVIDER=openai` の場合のみ必要 |
| `OPENAI_MODEL` | 使用するOpenAIモデル | allowlist内のモデルのみ許可 |
| `OPENAI_MAX_OUTPUT_TOKENS` | OpenAI API出力トークン上限 | 出力上限制御用 |
| `OPENAI_TIMEOUT_SECONDS` | OpenAI APIタイムアウト秒数 | 外部API呼び出しの待ち時間制御用 |

AWS配信用にFrontendをビルドする場合は、AWS Backend APIの接続先を指定します。ただし、API Gateway URLなどの実値はREADMEやdocsへ記載しません。

注意事項：

- `.env` や `.env.local` はGit管理対象外です
- APIキー、パスワード、アクセストークンなどの秘密情報をGitHubに上げないでください
- Backendのデフォルトは `APP_LLM_PROVIDER=mock` のため、通常のローカル起動では外部LLM APIキーは不要です
- `APP_LLM_PROVIDER=openai` を使う場合のみ `OPENAI_API_KEY` が必要です
- OpenAI API利用時は利用料が発生する可能性があります
- モデル変更時はOpenAI公式の料金、利用可能モデル、品質、速度、利用制限を確認してください

---

## 操作手順

ローカル環境での基本操作手順は以下です。

1. Backendを起動する
2. Frontendを起動する
3. ブラウザで `http://localhost:3000` を開く
4. 仕様入力フォームに架空サンプル仕様を入力する
5. テスト対象種別を選択する
6. テストレベルを選択する
7. テスト設計を生成する
8. 生成結果を確認する
9. Markdownをコピーする
10. 履歴一覧を確認する
11. 履歴詳細を確認する
12. 保存済みMarkdownをコピーする

デフォルトではLLM Mockで動作します。

OpenAI API生成モードを利用する場合は、Backend側で `APP_LLM_PROVIDER=openai` と `OPENAI_API_KEY` を設定します。OpenAI API利用時は、APIキー管理、利用料金、入力データ、ログ出力に注意してください。

AWS版のデプロイ・確認手順は、[AWSデプロイ手順](docs/aws-deploy.md) を参照してください。

---

## サンプル入力

以下は動作確認用の架空サンプルです。

実案件の仕様、顧客情報、個人情報、業務機密は使用しないでください。

```text
タイトル：
ログイン画面

テスト対象種別：
画面

テストレベル：
結合テスト

仕様本文：
利用者IDとパスワードを入力し、認証に成功した場合はメニュー画面へ遷移する。
認証に失敗した場合はエラーメッセージを表示する。

補足事項：
業務系Webアプリのログイン機能を想定する。
```

---

## テスト・確認コマンド

ローカル環境では、以下のコマンドでCI相当の確認を行えます。

### Backend

- `cd backend`
- `python -m pytest`

pytestではOpenAI APIを実呼び出ししない構成です。OpenAI APIに関するテストは、APIキー未設定、不正Provider、不正モデル、APIエラー、タイムアウトなどの挙動確認を対象にします。

### Frontend

- `cd frontend`
- `pnpm.cmd lint`
- `pnpm.cmd build`

PowerShell実行ポリシーにより `pnpm` が失敗する場合は、`pnpm.cmd` を使用します。

### Infra

- `cd infra`
- `pnpm.cmd cdk synth`

`pnpm.cmd cdk synth` はCDKテンプレートの合成確認のみを行います。AWSリソースの作成・更新・削除は行いません。

---

## CI

本リポジトリでは、GitHub Actions により以下を自動確認しています。

- Backend pytest
- Frontend lint
- Frontend build
- Infra cdk synth

CIは品質確認を目的としたものであり、AWS deploy は自動化していません。

GitHub Actionsでは、AWS認証情報、GitHub Secrets、OIDC連携を使用せず、`cdk deploy`、`cdk destroy`、AWSリソースの作成・更新・削除は実行しません。

また、CIではOpenAI APIを呼び出しません。Backendのデフォルトは `APP_LLM_PROVIDER=mock` であり、pytestでもOpenAI APIの実呼び出しは行わない構成です。

AWSリソースの作成・削除は、ローカル環境から手動で確認する前提です。手順は以下を参照してください。

- [AWSデプロイ手順](docs/aws-deploy.md)
- [AWS削除手順](docs/aws-destroy.md)

---

## セキュリティ・守秘義務上の注意

本アプリの利用時は、以下の情報を入力しないでください。

> 顧客名、個人情報、APIキー、パスワード、本番環境情報、業務機密を含む情報は入力しないでください。必要に応じてマスキングしてから利用してください。

開発・動作確認では、以下を徹底します。

- 本業の顧客情報は使用しない
- 実案件の設計書、実コード、実ログは使用しない
- 個人情報は使用しない
- サンプル仕様は架空データのみ使用する
- `.env` / `.env.local` / SQLite DBファイルはGit管理対象外にする
- `OPENAI_API_KEY` 実値をGitHubに上げない
- APIキー、パスワード、アクセストークンをGitHubに上げない
- API Gateway URL、CloudFront DomainName、S3 Bucket名、DynamoDB Table名などのAWSリソース実値をREADME / docsへ記載しない
- OpenAI API利用時も、実案件情報、顧客情報、個人情報、業務機密を入力しない
- 入力本文、補足事項、生成Markdown、OpenAIレスポンス本文、APIキーをログ出力しない方針で扱う
- CIではOpenAI APIを呼び出さない

---

## 現時点の制約

現時点では、以下の制約があります。

### AI / LLM

- デフォルトはLLM Mockを使用する
- OpenAI API連携は任意機能として最小連携済み
- `APP_LLM_PROVIDER=mock/openai` によるProvider切替に対応
- `APP_LLM_PROVIDER=openai` の場合のみOpenAI APIを呼び出す
- OpenAI API利用時は `OPENAI_API_KEY` が必要
- OpenAI API利用時は利用料が発生する可能性がある
- CIではOpenAI APIを呼び出さない
- pytestではOpenAI APIを実呼び出ししない
- Structured Outputs / JSON Schema指定は未実装
- Amazon Bedrock連携は未実装
- AWS Lambda版OpenAI連携は未実装
- RAGは未実装
- 生成根拠表示は未実装
- 実案件情報、顧客情報、個人情報、業務機密は入力しない
- `.env` / `.env.local` の実値はGitHubに載せない

### 認証・利用者管理

- Cognito認証は未実装
- API認証は未実装
- マルチテナントは未実装
- 課金は未実装

### 業務アプリ機能

- 履歴検索・編集・削除は未実装
- ファイルアップロードは未実装
- Excel出力は未実装
- Markdownレンダリングライブラリは未導入
- 本格ページネーションは未実装

### AWS運用

- AWS版BackendへのOpenAI API組み込みは未実装
- 独自ドメインは未設定
- 商用SaaS運用は未対応
- 高可用性構成は未対応
- WAF、ALB、RDS、ECS Fargate、NAT Gatewayは初期構成では使用していない
- 検証用リソースは必要に応じて削除する前提
- 常時公開URLはREADMEに掲載していない

本プロジェクトの区切り時点では、機能を広げすぎず、「仕様入力 → 生成 → 表示 → 保存 → 履歴確認」まで動くこと、低コスト構成でAWS化すること、OpenAI API最小連携まで確認することを優先しました。

---

## 今後の改善候補

以下は、現時点では未実装または追加検討対象です。

本プロジェクトはPhase 4まででいったん開発区切りとしており、以下は必要性が高まった場合に再評価する候補です。

### AI / LLM 強化

- Structured Outputs / JSON Schema指定
- プロンプト改善
- 出力構造化 + Frontend表示改善
- Amazon Bedrock連携
- AWS Lambda版OpenAI連携
- LLM Provider設計の拡張
- プロンプトテンプレート管理
- LLM利用回数制限
- 生成根拠表示

### AWS展開

- AWS構成図の追加
- AWS版BackendへのOpenAI API組み込み検討
- Secrets Manager等を使ったAPIキー管理検討
- GitHub Actionsによるデプロイ自動化検討
- DynamoDB履歴の検索・削除・TTL検討
- API認証方式の検討
- 独自ドメイン適用の検討

### 業務アプリ機能強化

- 画面キャプチャ追加
- Excel出力
- ファイルアップロード
- 履歴検索 / 編集 / 削除
- Markdown表示改善
- 面談用説明文・スキルシート反映

---

## GitHub Releases

| Version | 内容 |
|---|---|
| `v0.1.0-local-mvp` | ローカルMVP。仕様入力、LLM Mock生成、SQLite履歴保存、履歴一覧・詳細まで確認 |
| `v0.2.0-aws-frontend-hosting` | S3 + CloudFrontによるFrontend静的配信 |
| `v0.3.0-aws-low-cost-version` | S3 + CloudFront、API Gateway HTTP API、Python Lambda、DynamoDBを使ったAWS低コスト版 |
| `v0.4.0-openai-api-minimal` | LLM Mockを維持したまま、OpenAI APIによる実LLM生成モードを最小連携 |

---

## 関連docs

詳細な設計・検討内容は以下を参照してください。

- [ローカル開発環境セットアップ](docs/setup-local.md)
- [MVP要件整理](docs/mvp-requirements.md)
- [API設計](docs/api-design.md)
- [DB設計](docs/db-design.md)
- [LLM Mock設計](docs/llm-mock-design.md)
- [画面設計](docs/screen-design.md)
- [Markdown出力設計](docs/markdown-output.md)
- [サンプル仕様](docs/sample-specs.md)
- [Phase 1 実装前チェックリスト](docs/phase1-implementation-checklist.md)
- [ローカルMVP総合動作確認](docs/local-mvp-verification.md)
- [AWS構成方針](docs/aws-architecture.md)
- [AWS低コスト構成・料金見積もり](docs/aws-cost-estimate.md)
- [AWSデプロイ手順](docs/aws-deploy.md)
- [AWS削除手順](docs/aws-destroy.md)
- [AWS Budgets・コスト制御](docs/aws-budget.md)
- [ローカルMVPとAWS低コスト版の差分](docs/aws-version-differences.md)
