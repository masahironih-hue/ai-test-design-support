# 業務系SE向け AIテスト設計支援ツール

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

このプロジェクトは、個人開発のポートフォリオとして、以下を示すことを目的に開発しています。

- Python / FastAPI を用いたBackend API開発
- React / Next.js / TypeScript を用いたFrontend開発
- LLMを利用した業務支援アプリケーション設計
- 業務系システム開発経験を活かしたテスト設計支援の具体化
- 将来的にAWS SAAの学習内容を、低コストなAWS構成として実装に落とし込むための土台作り

現時点では、ローカルMVPとして主要機能を実装しています。  
AWSデプロイ、OpenAI API連携、Amazon Bedrock連携は今後の拡張候補です。

---

## 主な機能

現時点のローカルMVPでは、以下の機能を実装しています。

- 仕様入力フォーム
- テスト対象種別の選択
- テストレベルの選択
- LLM Mockによるテスト観点生成
- テストケース生成
- Markdown形式の生成結果表示
- Markdownコピー
- SQLiteへの履歴保存
- 履歴一覧表示
- 履歴詳細表示
- 保存済みMarkdownコピー
- セキュリティ注意事項表示
- 日時のJST表示

---

## 画面イメージ

Phase 1：ローカルMVPで実装した主要画面です。  
画面キャプチャには、架空のログイン画面仕様をサンプルとして使用しています。

### 仕様入力フォーム

機能概要や仕様メモ、テスト対象種別、テストレベル、補足事項を入力し、テスト設計生成を実行します。

![仕様入力フォーム](docs/images/phase1-local-mvp/01-top-form.png)

### テスト設計生成結果

入力された仕様をもとに、LLM Mock によりテスト観点、テストケース、Markdown形式の出力を生成します。

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

### Backend

- Python 3.13.x
- FastAPI
- SQLAlchemy
- SQLite
- pytest
- Uvicorn

### Frontend

- Next.js
- React
- TypeScript
- pnpm
- App Router

### その他

- Git / GitHub
- GitHub Issues
- LLM Mock

### 将来の拡張候補

- OpenAI API
- Amazon Bedrock
- AWS CDK
- DynamoDB
- S3 / CloudFront
- API Gateway / Lambda
- CloudWatch Logs

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
├─ docs/
└─ README.md
```

---

## ローカル起動手順

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

---

### Frontend起動

別のPowerShellを開き、以下を実行します。

```powershell
cd frontend
pnpm dev
```

起動後、以下にアクセスします。

```text
http://localhost:3000
```

---

## 環境変数

Frontendでは、Backend APIの接続先として以下を使用します。

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

設定例は以下のファイルを参照してください。

```text
frontend/.env.example
```

ローカル開発では、以下のように `.env.local` を作成して使用します。

```text
frontend/.env.local
```

注意事項：

- `.env.local` はローカル開発用です
- `.env.local` はGit管理対象外です
- APIキー、パスワード、アクセストークンなどの秘密情報をGitHubに上げないでください
- 現時点では外部LLM APIキーは不要です

---

## 操作手順

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

### Backend

```powershell
cd backend
python -m pytest
```

### Frontend

```powershell
cd frontend
pnpm lint
pnpm build
```

---

## SQLite履歴保存仕様

ローカルMVPでは、生成結果をSQLiteに保存します。

主な仕様は以下です。

- 生成結果はSQLiteに保存される
- Backend再起動後も履歴は保持される
- `init_db()` はテーブル作成用であり、既存履歴は削除しない
- 開発中に履歴を初期化したい場合は、Backend停止後に開発用SQLite DBファイルを手動削除する
- SQLite DBファイルはGit管理対象外とする

---

## 日時表示仕様

日時は以下の方針で扱います。

- Backend / DB ではUTC基準で扱う
- Frontend表示時にJSTへ変換する

例：

```text
UTC: 2026/05/22 07:35
JST: 2026/05/22 16:35
```

---

## セキュリティ・守秘義務上の注意

本アプリの利用時は、以下の情報を入力しないでください。

```text
顧客名、個人情報、APIキー、パスワード、本番環境情報、業務機密を含む情報は入力しないでください。
必要に応じてマスキングしてから利用してください。
```

開発・動作確認では、以下を徹底します。

- 本業の顧客情報は使用しない
- 実案件の設計書、実コード、実ログは使用しない
- 個人情報は使用しない
- サンプル仕様は架空データのみ使用する
- `.env` / `.env.local` / SQLite DBファイルはGit管理対象外にする
- APIキー、パスワード、アクセストークンをGitHubに上げない

---

## 現時点の制約

現時点のローカルMVPには、以下の制約があります。

- LLM Mockを使用しており、実際の外部LLM APIは呼び出していない
- OpenAI API連携は未実装
- Amazon Bedrock連携は未実装
- AWSデプロイは未実装
- 認証は未実装
- 履歴検索・編集・削除は未実装
- ファイルアップロードは未実装
- Excel出力は未実装
- Markdownレンダリングライブラリは未導入
- マルチテナント・課金は未実装

初期MVPでは、機能を広げすぎず、まずはローカル環境で「仕様入力 → 生成 → 表示 → 保存 → 履歴確認」まで動くことを優先しています。

---

## 今後の改善候補

### AI / LLM 強化

- OpenAI API連携
- Amazon Bedrock対応
- LLM Provider切替
- プロンプトテンプレート管理
- LLM利用回数制限
- 生成根拠表示

### AWS展開

- AWS低コスト構成への展開
- S3 + CloudFrontによるFrontend配信
- API Gateway + LambdaによるBackend API公開
- DynamoDBによる履歴保存
- CloudWatch Logs確認手順
- AWS CDKによるIaC化
- AWS構成図の追加
- AWSデプロイ手順・削除手順の整備

### 業務アプリ機能強化

- 画面キャプチャ追加
- Excel出力
- ファイルアップロード
- 履歴検索 / 編集 / 削除
- Markdown表示改善
- 面談用説明文・スキルシート反映

---

## 関連docs

詳細な設計・検討内容は以下を参照してください。

- [MVP要件整理](docs/mvp-requirements.md)
- [API設計](docs/api-design.md)
- [DB設計](docs/db-design.md)
- [LLM Mock設計](docs/llm-mock-design.md)
- [画面設計](docs/screen-design.md)
- [Markdown出力設計](docs/markdown-output.md)
- [サンプル仕様](docs/sample-specs.md)
- [Phase 1 実装前チェックリスト](docs/phase1-implementation-checklist.md)
- [ローカルMVP総合動作確認](docs/local-mvp-verification.md)