# ローカルMVPとAWS低コスト版の差分

## 1. このドキュメントの目的

このドキュメントは、「業務系SE向け AIテスト設計支援ツール」における、ローカルMVPとAWS低コスト版の違いを整理するための補助資料です。

READMEではプロジェクト全体の概要、起動手順、主な機能、注意事項を簡潔に説明し、このドキュメントでは以下を詳しく整理します。

- ローカルMVPとAWS低コスト版の構成差分
- FastAPI Backend と AWS Lambda Backend の違い
- SQLite と DynamoDB の違い
- ローカルFrontend と CloudFront配信Frontend の違い
- ローカルMVPで確認済みの範囲
- AWS低コスト版で確認済みの範囲
- AWSリソース削除後の扱い
- 未実装範囲
- 外部説明で使える表現
- 避けるべき過大表現
- セキュリティ・守秘義務・AWS実値非公開の方針

このドキュメントは、ポートフォリオ閲覧者、面談前の説明準備、技術記事化準備で参照することを想定しています。

---

## 2. 前提

このプロジェクトでは、以下の2段階で実装を進めています。

| 区分 | 状態 | 目的 |
|---|---|---|
| Phase 1：ローカルMVP | 完了 | FastAPI / Next.js / SQLite / LLM Mock によるローカル動作確認 |
| Phase 2：AWS低コスト版 | 完了 | S3 + CloudFront、API Gateway + Lambda、DynamoDB による低コストServerless構成の検証 |

Phase 2では、AWS低コスト版として以下を構築・確認しました。

- S3 + CloudFront によるFrontend静的配信
- CloudFront OAC によるS3 private配信
- API Gateway HTTP API + Python Lambda によるBackend API
- DynamoDBによる履歴保存
- CloudFront配信FrontendからAWS Backend APIへの接続
- 画面上での生成・履歴保存・履歴一覧・履歴詳細確認
- AWS CDKによる構成管理
- AWSデプロイ手順・削除手順の整理
- コスト管理のためのAWSリソース削除

なお、AWS低コスト版は本番運用中のサービスではありません。  
検証後はコスト管理のため、不要なAWSリソースを削除する運用としています。

---

## 3. 全体比較

| 観点 | ローカルMVP | AWS低コスト版 |
|---|---|---|
| 主目的 | ローカル環境でMVP機能を実装・確認する | AWS上で低コストなServerless構成を検証する |
| Frontend | Next.js / React / TypeScript をローカル起動 | S3 + CloudFront による静的配信 |
| Backend | FastAPI | API Gateway HTTP API + Python Lambda |
| DB | SQLite | DynamoDB |
| 履歴保存 | SQLiteファイル | DynamoDBテーブル |
| API実行方式 | ローカルBackend常駐 | リクエスト単位のLambda実行 |
| 生成処理 | LLM Mock | LLM Mock相当の生成処理 |
| ログ | ローカルログ | CloudWatch Logs |
| IaC | なし、または限定的 | AWS CDK |
| コスト | ほぼなし | 少額のAWS利用料が発生する可能性あり |
| 削除手順 | ローカルファイル削除中心 | CDK destroy、S3、DynamoDB、CloudWatch Logs確認 |
| 説明価値 | FastAPI / Next.js / SQLite の実装説明 | AWS Serverless / CloudFront / Lambda / DynamoDB の構成説明 |

---

## 4. ローカルMVPの構成

ローカルMVPでは、以下の構成で実装しています。

| レイヤー | 技術 |
|---|---|
| Frontend | Next.js / React / TypeScript |
| Backend | Python / FastAPI |
| DB | SQLite |
| 生成処理 | LLM Mock |
| 履歴保存 | SQLite |
| 実行環境 | ローカルPC |

ローカルMVPで確認済みの一連動作は以下です。

1. 仕様入力
2. LLM Mockによる生成
3. 生成結果表示
4. Markdownコピー
5. SQLite履歴保存
6. 履歴一覧表示
7. 履歴詳細表示
8. 保存済みMarkdownコピー

ローカルMVPでは、まず「仕様入力からテスト設計結果の生成・保存・再確認まで成立すること」を優先しました。

---

## 5. AWS低コスト版の構成

AWS低コスト版では、以下の構成で実装・検証しています。

| レイヤー | 技術 |
|---|---|
| Frontend配信 | S3 + CloudFront |
| S3アクセス制御 | CloudFront OAC |
| Backend API | API Gateway HTTP API + Python Lambda |
| DB | DynamoDB |
| ログ | CloudWatch Logs |
| IaC | AWS CDK |
| 生成処理 | LLM Mock相当の生成処理 |

AWS低コスト版で確認済みの一連動作は以下です。

1. CloudFront配信Frontendを表示
2. FrontendからAPI Gateway HTTP APIを呼び出し
3. Python Lambdaで生成処理を実行
4. DynamoDBへ履歴保存
5. 履歴一覧を取得
6. 履歴詳細を取得
7. 画面上で生成結果・履歴一覧・履歴詳細を確認

AWS低コスト版は、常時稼働サーバーを避け、個人開発でも扱いやすい低コストなServerless構成を採用しています。

---

## 6. 機能差分

| 機能 | ローカルMVP | AWS低コスト版 |
|---|---|---|
| 仕様入力 | 対応 | 対応 |
| 生成結果表示 | 対応 | 対応 |
| Markdownコピー | 対応 | 対応 |
| 履歴保存 | 対応 | 対応 |
| 履歴一覧 | 対応 | 対応 |
| 履歴詳細 | 対応 | 対応 |
| 保存済みMarkdownコピー | 対応 | 対応 |
| 実LLM API連携 | 未対応 | 未対応 |
| 認証 | 未対応 | 未対応 |
| 課金 | 未対応 | 未対応 |
| マルチテナント | 未対応 | 未対応 |
| ファイルアップロード | 未対応 | 未対応 |
| Excel出力 | 未対応 | 未対応 |
| RAG | 未対応 | 未対応 |

ローカルMVPとAWS低コスト版で、ユーザー視点の主要なMVP機能は概ね同じです。

一方、内部構成は大きく異なります。  
ローカルMVPではFastAPIとSQLiteを使い、AWS低コスト版ではAPI Gateway、Lambda、DynamoDBを使っています。

---

## 7. 技術構成差分

| 観点 | ローカルMVP | AWS低コスト版 |
|---|---|---|
| アプリ実行 | ローカル起動 | AWS上に静的FrontendとServerless Backendを配置 |
| Backend実装 | FastAPIアプリケーション | Python Lambda handler |
| API公開 | localhost | API Gateway HTTP API |
| DB接続 | SQLiteファイル | DynamoDB API |
| 状態管理 | ローカルファイル中心 | AWSマネージドサービス中心 |
| インフラ管理 | 手動・ローカル中心 | AWS CDK |
| ログ確認 | ローカルコンソール | CloudWatch Logs |
| 削除対象 | DBファイルや生成物 | CDK Stack、S3、DynamoDB、CloudWatch Logsなど |

---

## 8. Backend差分

### ローカルMVP

ローカルMVPでは、BackendにFastAPIを使用しています。

主な特徴は以下です。

- Python / FastAPIでAPIを実装
- ローカルPC上でBackendプロセスを常駐起動
- `POST /test-designs/generate` でテスト設計結果を生成
- 履歴保存・履歴一覧・履歴詳細APIを提供
- SQLiteと連携
- pytestによるテストを実施

### AWS低コスト版

AWS低コスト版では、BackendをAPI Gateway HTTP API + Python Lambdaで構成しています。

主な特徴は以下です。

- API Gateway HTTP APIでエンドポイントを公開
- Python Lambdaで生成・履歴保存・一覧・詳細処理を実行
- DynamoDBと連携
- Lambdaはリクエスト単位で実行
- 常時稼働サーバーを持たない
- CloudWatch Logsでログを確認
- CloudWatch Logsへ入力本文・生成本文を出さない方針

### Backend差分まとめ

| 観点 | FastAPI Backend | AWS Lambda Backend |
|---|---|---|
| 実行方式 | ローカルで常駐 | リクエスト単位で実行 |
| API公開 | ローカルURL | API Gateway |
| DB接続 | SQLite | DynamoDB |
| 開発しやすさ | ローカルで確認しやすい | AWS構成理解が必要 |
| コスト | ほぼなし | リクエスト数・ログ量に応じて課金可能性あり |
| ポートフォリオ価値 | Python / FastAPI実装を説明しやすい | Serverless構成を説明しやすい |

---

## 9. DB / 履歴保存差分

### ローカルMVP

ローカルMVPではSQLiteを使用しています。

主な特徴は以下です。

- ローカルファイルとしてDBを保持
- 開発・検証が容易
- 初期MVPに適している
- ローカル環境の履歴保存確認に使いやすい

### AWS低コスト版

AWS低コスト版ではDynamoDBを使用しています。

主な特徴は以下です。

- AWSマネージドNoSQL DB
- Serverless構成と相性がよい
- Lambdaから履歴保存・一覧取得・詳細取得を実行
- オンデマンド課金により、低頻度利用ではコストを抑えやすい
- テーブル実名はREADME / docsには記載しない

### DB差分まとめ

| 観点 | SQLite | DynamoDB |
|---|---|---|
| 種別 | ローカルRDB | AWSマネージドNoSQL |
| 保存場所 | ローカルファイル | AWS |
| 初期導入 | 容易 | AWS構成・権限設定が必要 |
| スケール | ローカルMVP向け | Serverless構成向け |
| 削除 | DBファイル削除 | DynamoDBテーブル削除 |
| 説明価値 | ローカルMVPの保存処理 | AWS Serverlessのデータ保存 |

---

## 10. Frontend / 配信差分

### ローカルMVP

ローカルMVPでは、Next.js / React / TypeScript のFrontendをローカル起動します。

主な特徴は以下です。

- 開発中の画面確認が容易
- ローカルBackend APIを呼び出す
- フォーム入力、生成結果表示、履歴一覧、履歴詳細を確認可能
- 開発・修正サイクルが速い

### AWS低コスト版

AWS低コスト版では、Frontendを静的出力し、S3 + CloudFrontで配信しています。

主な特徴は以下です。

- S3 BucketはPublic公開せず、CloudFront OAC経由で配信
- CloudFrontから静的Frontendを配信
- FrontendからAWS Backend APIを呼び出す
- 検証後はコスト管理のためAWSリソースを削除
- CloudFront DomainName実値はREADME / docsには記載しない

### Frontend差分まとめ

| 観点 | ローカルFrontend | CloudFront配信Frontend |
|---|---|---|
| 実行場所 | ローカルPC | AWS |
| 配信方式 | 開発サーバー | S3 + CloudFront |
| Backend接続先 | ローカルFastAPI | API Gateway HTTP API |
| 公開範囲 | ローカル確認 | 検証用にAWS配信 |
| セキュリティ | ローカル中心 | S3 private配信 + CloudFront OAC |
| 削除対象 | ローカル生成物 | CloudFront / S3関連リソース |

---

## 11. ログ / セキュリティ差分

| 観点 | ローカルMVP | AWS低コスト版 |
|---|---|---|
| ログ出力先 | ローカルコンソール | CloudWatch Logs |
| 入力本文ログ | 出さない方針 | 出さない方針 |
| 生成本文ログ | 出さない方針 | 出さない方針 |
| 秘密情報管理 | `.env` / `.env.local` をGit管理対象外 | AWS認証情報・API URL実値などをGit管理対象外 |
| 顧客情報 | 使用しない | 使用しない |
| 実案件情報 | 使用しない | 使用しない |
| AWS識別子 | 原則なし | README / docsへ記載しない |

CloudWatch Logsには、以下を出さない方針です。

- request body全体
- `spec_text`
- `supplement`
- `markdown`
- APIキー
- パスワード
- アクセストークン
- 顧客情報
- 個人情報
- 業務機密

---

## 12. コスト / 削除手順差分

### ローカルMVP

ローカルMVPでは、基本的にAWS利用料は発生しません。

主な削除対象は以下です。

- ローカルDBファイル
- 一時生成ファイル
- build成果物
- node_modules
- Python仮想環境

### AWS低コスト版

AWS低コスト版では、利用量が少なくてもAWS利用料が発生する可能性があります。

主なコスト発生要因は以下です。

- S3
- CloudFront
- API Gateway HTTP API
- Lambda
- DynamoDB
- CloudWatch Logs

そのため、AWS低コスト版では以下を重視しています。

- AWS Pricing Calculatorによる料金見積もり
- AWS Budgetsによるコスト監視
- Free Tier対象サービスの優先
- 常時稼働リソースの回避
- CloudWatch Logs保持期間の短縮
- 検証後の不要リソース削除
- `docs/aws-destroy.md` による削除手順整理

---

## 13. AWSリソース削除後の扱い

Phase 2のAWS低コスト版は、構築・動作確認後、コスト管理のためAWSリソースを削除する運用としています。

そのため、以下の表現は可能です。

> AWS低コスト版では、S3 + CloudFront、API Gateway HTTP API、Python Lambda、DynamoDB を使い、画面上で生成・履歴保存・履歴一覧・履歴詳細まで確認しました。

一方で、以下の表現は避けます。

- 現在もAWS上で稼働中です
- 公開URLで常時利用可能です
- 本番環境として運用中です
- 商用SaaSとして運用中です

AWSリソース削除済みであることは、未完成という意味ではなく、個人開発におけるコスト管理・削除手順整備の一部として扱います。

---

## 14. 未実装範囲

現時点で、以下は未実装です。

| 区分 | 未実装項目 |
|---|---|
| LLM連携 | OpenAI API連携、Amazon Bedrock連携 |
| 認証 | Cognito認証、API認証 |
| SaaS機能 | 課金、マルチテナント、商用SaaS運用 |
| インフラ | 独自ドメイン、高可用性構成、WAF、ALB、RDS、ECS Fargate、NAT Gateway |
| 履歴機能 | 履歴検索、履歴編集、履歴削除、本格ページネーション |
| 入出力 | ファイルアップロード、Excel出力 |
| AI強化 | RAG、プロンプトテンプレート管理、生成品質改善 |

これらは、初期MVPおよびAWS低コスト版では意図的に作り込みすぎない範囲としています。

---

## 15. 外部説明で使える表現

README、面談、スキルシート、技術記事では、以下のような表現を使用できます。

### ローカルMVPの説明

> ローカルMVPでは、FastAPI + Next.js + SQLite により、仕様入力、LLM Mock生成、結果表示、Markdownコピー、履歴保存、履歴一覧、履歴詳細までをローカル環境で実装・確認しました。

### AWS低コスト版の説明

> AWS低コスト版では、S3 + CloudFrontで配信したFrontendから、API Gateway HTTP API + Python Lambda + DynamoDB のBackend APIを呼び出し、画面上で生成、履歴保存、履歴一覧、履歴詳細まで確認しました。

### AWSリソース削除後の説明

> AWS低コスト版は構築・動作確認済みです。検証後はコスト管理のため、不要なAWSリソースを削除する運用としています。

### AWS経験の説明

> AWSは本番運用ではなく、AWS SAAで学習した内容を個人開発へ落とし込み、低コストなServerless構成として設計・実装したものです。

### ポートフォリオとしての説明

> 業務系SEとしての設計・テスト観点整理の経験をもとに、仕様メモからテスト観点・テストケース・確認事項を生成するWebアプリを作成しました。ローカルMVPに加えて、AWS低コスト版としてServerless構成への展開も検証しています。

---

## 16. 避けるべき表現

以下のような表現は、実装範囲や運用実態を過大に見せる可能性があるため避けます。

| 避ける表現 | 理由 |
|---|---|
| AWS版が本番運用可能です | 本番運用設計・監視・認証・可用性設計は未対応のため |
| 現在もAWS上で稼働中です | 検証後にAWSリソースを削除しているため |
| 公開URLで常時利用可能です | 常時公開運用ではないため |
| 商用SaaSとして運用中です | 課金・認証・利用規約・運用体制が未対応のため |
| 高可用性構成です | Multi-AZ、冗長化、障害対応設計を本格実装していないため |
| 認証付きSaaSです | Cognito認証・API認証は未実装のため |
| OpenAI API連携済みです | 現時点ではLLM Mockのため |
| Bedrock対応済みです | Amazon Bedrock連携は未実装のため |
| AWS実務経験があります | 個人開発・学習成果としてのAWS利用であり、実務経験とは分けるべきため |
| AWSで本番運用しています | 本番運用ではないため |
| 大規模アクセス対応済みです | 負荷試験・スケール設計は未対応のため |
| マルチテナント対応済みです | マルチテナント設計は未実装のため |
| 実案件の設計書を使って検証しました | 守秘義務上、実案件情報は使用しないため |
| 実顧客データで検証しました | 顧客情報・個人情報は使用しないため |

---

## 17. セキュリティ・公開リスク方針

README、docs、GitHub Issues、GitHub Releasesでは、以下を記載しません。

- API Gateway URL実値
- CloudFront DomainName実値
- S3 Bucket実名
- DynamoDB Table実名
- AWSアカウントID
- IAM ARN
- VPC ID
- EC2 ID
- IPアドレス
- AWS認証情報
- `.env` 実値
- `.env.local` 実値
- APIキー
- パスワード
- アクセストークン
- 実案件情報
- 顧客情報
- 個人情報
- 業務機密

開発・デモ・README・docsでは、架空データ、サンプル仕様、ダミー設計書のみを使用します。

---

## 18. 関連docs

関連するドキュメントは以下です。

| docs | 内容 |
|---|---|
| [setup-local.md](setup-local.md) | ローカル環境構築・起動手順 |
| [mvp-requirements.md](mvp-requirements.md) | MVP要件 |
| [api-design.md](api-design.md) | API設計 |
| [db-design.md](db-design.md) | DB設計 |
| [local-mvp-verification.md](local-mvp-verification.md) | ローカルMVP検証結果 |
| [aws-architecture.md](aws-architecture.md) | AWS構成 |
| [aws-cost-estimate.md](aws-cost-estimate.md) | AWS料金見積もり |
| [aws-budget.md](aws-budget.md) | AWS Budgets・コスト制御方針 |
| [aws-deploy.md](aws-deploy.md) | AWSデプロイ手順 |
| [aws-destroy.md](aws-destroy.md) | AWS削除手順 |

---

## 19. まとめ

ローカルMVPでは、FastAPI、Next.js、SQLiteを使い、仕様入力から生成・保存・履歴確認までの基本機能を実装しました。

AWS低コスト版では、S3 + CloudFront、API Gateway HTTP API、Python Lambda、DynamoDBを使い、ローカルMVP相当の主要機能をServerless構成で確認しました。

ただし、AWS低コスト版は本番運用中のサービスではありません。  
検証後はコスト管理のため、不要なAWSリソースを削除する運用としています。

このプロジェクトでは、実装済み範囲と未実装範囲を明確に分け、AWS実務経験やSaaS運用実績を過度に盛らない形で、個人開発ポートフォリオとして説明できる状態を目指しています。