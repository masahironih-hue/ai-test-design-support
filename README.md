# AI Test Design Support

業務系SE向けの AIテスト設計支援ツールです。

仕様メモ、画面仕様、API仕様、バッチ仕様、DB更新仕様、外部連携仕様などを入力し、テスト観点・テストケース・確認事項の生成を支援するWebアプリケーションを目指します。

## 目的

このプロジェクトは、以下を目的とした個人開発ポートフォリオです。

- 業務系SE経験を活かしたWebアプリケーション開発
- Python / FastAPI を用いたバックエンド開発
- React / Next.js / TypeScript を用いたフロントエンド開発
- LLMを活用したテスト設計支援機能の実装
- 将来的なAWS低コスト構成への展開

## 想定機能

初期MVPでは、以下の流れを実現します。

1. 仕様メモを入力する
2. LLM Mockでテスト観点を生成する
3. 生成結果をMarkdown形式で表示する
4. 生成履歴をSQLiteに保存する

## 想定する出力

- 正常系テスト観点
- 異常系テスト観点
- 境界値
- 入力チェック
- DB更新確認
- 外部連携確認
- 権限確認
- ログ確認
- リカバリ観点
- 性能観点
- 追加確認事項
- テストケース表

## 技術スタック

### Backend

- Python
- FastAPI
- Uvicorn
- SQLite
- SQLModel または SQLAlchemy
- pytest

### Frontend

- Next.js
- React
- TypeScript
- Node.js
- pnpm

### AI / LLM

- 初期は LLM Mock
- 後続フェーズで OpenAI API 連携を検討
- 将来的に Amazon Bedrock も検討

### 将来検討

- AWS CDK
- S3 + CloudFront
- API Gateway + Lambda
- DynamoDB
- CloudWatch Logs
- AWS Budgets

## 初期方針

- まずはローカルMVPを優先する
- 初期段階ではDockerを使用しない
- 初期段階ではAWSを使用しない
- 初期段階では認証、課金、マルチテナントは作り込まない
- 初期LLM連携はMockで実装する
- APIキー不要で起動できる状態を優先する

## セキュリティ方針

このプロジェクトでは、以下の情報を使用しません。

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

開発・デモには、サンプル仕様・架空データのみを使用します。

`.env` はGit管理対象外とし、`.env.example` のみ管理します。

## ドキュメント

- [ローカル環境構築手順](docs/setup-local.md)
- [開発運用方針](docs/development-policy.md)
- [セキュリティ方針](docs/security-policy.md)

## 現在のフェーズ

現在は Phase 0：進め方・環境構築 です。

まだ本格的な実装には入らず、開発環境、運用方針、初期ドキュメントを整備しています。
