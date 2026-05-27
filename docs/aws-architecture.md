# AWS構成方針

## 1. 目的

このドキュメントは、AIテスト設計支援ツールの Phase 2：AWS低コスト版におけるAWS構成方針を整理するためのものです。

Phase 2では、本格的な本番運用や大規模SaaS構成を目指すのではなく、AWS SAAで学習した内容を個人開発に適用し、低コストで説明可能なAWS構成を作ることを目的とします。

## 2. 関連Issue

- GitHub Issue: #20 AWS低コスト構成・料金見積もり
- GitHub Issue: #21 AWS Budgets・コスト制御設定
- GitHub Issue: #22 AWSデプロイ・削除手順
- GitHub Issue: #23 S3 CloudFront Frontend配信

## 3. 現在の到達点

Phase 2初期では、S3 + CloudFront による Frontend静的配信を検証済みです。

確認済みの内容は以下です。

- Next.js / React / TypeScript Frontend の静的export
- `frontend/out` の生成
- TypeScript CDK構成の作成
- S3 Bucket作成
- S3 Bucket Public Access Block有効化
- CloudFront Distribution作成
- CloudFront OACによるS3 private配信
- CloudFront URLでのFrontend画面表示
- Backend API未AWS化による制約の整理
- 既存VPC / EC2 / Security Group / Route 53を使用・変更しないことの確認
- 対象S3 Bucketの中身を手動削除したうえでの `pnpm cdk destroy` 確認

検証後、作成した本プロジェクト用AWSリソースは削除済みです。  
そのため、READMEやdocsには常時公開URLを掲載しません。

## 4. 全体方針

Phase 2では、以下の順でAWS化を進めます。

```text
1. AWS低コスト構成・料金見積もり
2. AWS構成docs作成
3. AWS Budgets・コスト制御設定
4. S3 + CloudFrontによるFrontend配信
5. AWS削除手順整備
6. READMEへのAWS構成概要反映
7. Backend AWS化の検討
```

最初からBackend、DB、認証、LLM API連携まで一気にAWS化するのではなく、まずはFrontend配信をAWS化します。

## 5. 既存AWS環境との分離方針

本プロジェクトでは、既存のプライベート用VPC/EC2と同一AWSアカウントを使用します。

ただし、既存環境との混同や誤削除を防ぐため、AIテスト設計支援ツール用リソースは以下の方針で分離します。

- 既存プライベートVPCは使用しない
- 既存EC2へ同居デプロイしない
- 既存Security Groupを流用しない
- 既存IAM Roleを安易に流用しない
- 既存Route 53設定を変更しない
- 既存プライベートサーバの運用設定に影響を与えない
- 削除手順では、本プロジェクト用リソースのみを対象にする

## 6. 命名・タグ方針

本プロジェクト用リソースには、原則として以下の文字列を含めます。

```text
ai-test-design-support
```

CDK Stack名は以下です。

```text
AiTestDesignSupportFrontendStack
```

本プロジェクト用AWSリソースには、可能な範囲で以下のタグを付与します。

| Key | Value例 | 用途 |
|---|---|---|
| Project | `ai-test-design-support` | 本プロジェクト用リソース識別 |
| Environment | `dev` | 環境識別 |
| Purpose | `portfolio` | ポートフォリオ用途であることを明示 |
| ManagedBy | `cdk` | CDK管理対象であることを明示 |

## 7. Phase 2初期構成

Phase 2初期では、以下の構成を採用しました。

```text
Next.js / React / TypeScript Frontend
  ↓ static export
frontend/out
  ↓ aws s3 sync
Private S3 Bucket
  ↓ CloudFront OAC
CloudFront Distribution
  ↓
Browser
```

### 7.1 作成対象

| 要素 | サービス / 構成 | 用途 |
|---|---|---|
| Frontend build成果物 | Next.js / React / TypeScript | 静的ファイル生成 |
| 静的ファイル配置 | S3 | `frontend/out` の配置 |
| コンテンツ配信 | CloudFront | HTTPS配信、キャッシュ |
| S3アクセス制御 | CloudFront OAC | S3 BucketをPublic公開せずCloudFront経由で配信 |
| IaC | AWS CDK TypeScript | S3 / CloudFront構成の管理 |
| Backend API | ローカルまたは後続AWS化 | Phase 2初期では対象外 |
| 履歴保存DB | SQLiteまたは後続DynamoDB | Phase 2初期では対象外 |

### 7.2 採用理由

- 低コストで始めやすい
- AWSリソース数を抑えられる
- 既存VPC/EC2に触れずに構成できる
- 同一AWSアカウント内でも分離しやすい
- 削除手順を整理しやすい
- READMEでAWS構成を説明しやすい
- 面談で「AWS SAA学習内容を個人開発に適用した」と説明しやすい

### 7.3 セキュリティ方針

S3 BucketはPublic公開しません。  
CloudFront OACを使用し、CloudFront DistributionからのみS3オブジェクトを参照できる構成にします。

また、S3 Bucket Policyでは、非HTTPSアクセスを拒否します。

### 7.4 Backend API未AWS化による制約

現時点では、Backend APIはAWS化していません。

そのため、CloudFrontで配信されるFrontend上では画面表示を確認できますが、以下の機能を利用するには、ローカルBackendまたは後続のAWS Backend構成が必要です。

- テスト設計生成API
- 履歴一覧API
- 履歴詳細API

この制約は、READMEおよびデプロイ手順に明記します。

## 8. Phase 2初期では採用しない構成

以下はPhase 2初期では採用しません。

```text
CloudFront
↓
ALB
↓
ECS Fargate
↓
RDS PostgreSQL
```

| サービス / 構成 | 理由 |
|---|---|
| ALB | 常時稼働コストが発生しやすい |
| ECS Fargate | 実務寄りだが初期には構成が重い |
| RDS | 継続課金・削除漏れリスクがある |
| NAT Gateway | 高コスト化しやすい |
| EKS | 個人開発初期として過剰 |
| WAF | 初期デモ用途では優先度が低い |
| EC2常時起動 | 既存プライベートEC2との混同リスクがある |

## 9. 後続構成候補

Phase 2後半またはPhase 3以降で、以下を検討します。

```text
Frontend
  ↓
S3 + CloudFront

Backend API
  ↓
API Gateway + Lambda

履歴保存
  ↓
DynamoDB
```

| サービス | 用途 | 検討タイミング |
|---|---|---|
| API Gateway | Backend API公開 | Frontend配信後 |
| Lambda | Backend API実行 | FastAPIのLambda対応検討後 |
| DynamoDB | 履歴保存 | SQLiteからの移行方針整理後 |
| CloudWatch Logs | APIログ確認 | Lambda導入時 |
| AWS Budgets | コスト監視 | AWSリソース作成前 |

## 10. コスト方針

Phase 2では、以下の方針でコストを抑えます。

- AWS Pricing Calculatorで事前に概算する
- AWS Budgetsで予算アラートを設定する
- Free Tier対象サービスを優先する
- 常時稼働リソースを避ける
- 不要なS3オブジェクトを削除する
- CloudWatch Logs保持期間を短くする
- デプロイ後に削除手順を確認する
- 既存プライベートサーバ費用と本プロジェクト費用を混同しない

AWS Pricing Calculatorで確認した結果、Phase 2初期候補である S3 + CloudFront 構成は、以下の概算です。

| 構成 | 月額概算 |
|---|---:|
| S3 + CloudFront | $0.19 USD |
| Serverless Backend比較用 | $0.15 USD |
| 両方を採用した場合の単純合算 | $0.34 USD |

## 11. 削除方針

Issue #23では、検証後に以下の削除を確認しました。

```text
1. CloudFormation Outputから対象S3 Bucket名を取得
2. 対象S3 Bucketの中身を手動削除
3. pnpm cdk destroy を実行
4. 本プロジェクト用Stackの削除を確認
```

`autoDeleteObjects: true` は使用せず、初期構成をシンプルに保ちます。  
S3 Bucket削除時は、対象Bucketが本プロジェクト用であることをCloudFormation Outputから確認してから空にします。

## 12. READMEへの反映方針

READMEには、AWS構成の詳細をすべて書くのではなく、以下を要約して記載します。

- AWS化の目的
- S3 + CloudFront Frontend静的配信を検証済みであること
- Backend AWS化は後続検討であること
- 検証後にリソース削除済みであり、常時公開URLは掲載しないこと
- 料金見積もりdocsへのリンク
- デプロイ手順docsへのリンク
- 削除手順docsへのリンク
- 本格運用ではなく学習・ポートフォリオ目的であること

## 13. 面談・ポートフォリオでの説明方針

AWS実務経験を過度に盛らず、以下のように説明します。

```text
AWS SAAで学習した内容をもとに、個人開発のローカルMVPを低コストなAWS構成へ段階的に展開しています。
初期段階では、S3 + CloudFrontによる静的Frontend配信をCDKで構築し、料金見積もり、Budgets、削除手順、既存AWS環境との分離を含めて確認しました。
Backend APIのAWS化は後続検討です。
```

以下のような表現は避けます。

- AWS本番運用経験があります
- ECS / RDS / ALBで本番運用しています
- 実務でAWSアーキテクチャを設計しました
- BedrockやOpenAI APIを本格運用しています

## 14. 現時点の結論

Phase 2初期のAWS構成として、以下を検証済みです。

```text
S3 + CloudFront による Frontend 静的配信
```

Backend API、DynamoDB、CloudWatch Logsの本格利用は、Frontend配信後に別Issueで検討します。

また、既存プライベート用VPC/EC2と同一AWSアカウントを使用するため、命名規則、タグ、Stack名、削除対象確認によって、本プロジェクト用リソースを明確に分離します。

## 15. 次アクション

- READMEへS3 + CloudFront検証結果を反映する
- `docs/aws-deploy.md` へ実施済みデプロイ手順を反映する
- `docs/aws-destroy.md` へ確認済み削除手順を反映する
- Git管理対象にAWS識別子や秘密情報が含まれていないことを確認する
- Issue #23 close用コメントを作成する
## Backend Serverless構成方針

Phase 2では、S3 + CloudFront による Frontend 静的配信まで完了している。

現時点のAWS版は、以下の状態である。

```text
Frontend：S3 + CloudFront で静的配信済み
Backend API：未AWS化
履歴保存：ローカルSQLite
```

そのため、現時点のAWS版を「AWS上で全機能が動作する構成」とは扱わない。  
Backend APIと履歴保存のAWS化は、後続タスクで段階的に対応する。

---

## Backend Serverless推奨構成

Backend AWS化では、以下のServerless構成を優先候補とする。

```text
Browser
↓
CloudFront
↓
S3 Static Frontend
↓
API Gateway HTTP API
↓
Python Lambda
↓
DynamoDB
↓
CloudWatch Logs
```

初期方針は以下とする。

| 項目 | 方針 |
|---|---|
| API Gateway | HTTP APIを優先する |
| Backend実行環境 | Python Lambda |
| DB | DynamoDB オンデマンド |
| ログ | CloudWatch Logs |
| ログ保持期間 | 7日 |
| VPC | 使用しない |
| 認証 | 初期段階では実装しない |
| LLM API | 初期段階ではMock相当を維持し、OpenAI API / Bedrock連携は後続検討 |

---

## HTTP APIを優先する理由

API Gatewayには、主にHTTP APIとREST APIがある。

初期Backend Serverless構成では、以下の理由からHTTP APIを優先する。

- Lambda連携のシンプルなAPIに向いている
- REST APIより低コストになりやすい
- 初期MVPに必要な機能を満たしやすい
- APIキー、利用量プラン、WAF、Private APIなどの高度な機能を初期段階では使わない

REST APIは、以下が必要になった段階で再検討する。

- APIキー
- Usage Plan
- リクエスト検証
- AWS WAF連携
- Private API
- より細かいAPI Gateway機能

---

## FastAPI on Lambda案を初期採用しない理由

既存ローカルMVPでは FastAPI + SQLite を利用している。

FastAPIをLambdaへ載せる案には、以下のメリットがある。

- 既存FastAPIコード資産を活かしやすい
- Python / FastAPI案件向けの説明につながる
- ローカルMVPとの連続性がある

一方で、Phase 2初期のBackend AWS化としては、以下の懸念がある。

- Mangum等のASGIアダプタ検討が必要になる
- Lambda向けの起動方式・依存関係調整が必要になる
- パッケージサイズやcold startへの注意が必要になる
- SQLite / SQLAlchemy前提をDynamoDBへ差し替える設計が必要になる
- シンプルなAPIに対して構成がやや重くなる

そのため、Phase 2初期ではFastAPI on Lambdaを採用せず、薄いPython Lambda APIとして実装する方針とする。

FastAPI on Lambdaは、後続の改善候補として残す。

---

## 薄いLambda API案を採用する理由

Phase 2では、低コスト・削除容易性・説明しやすさを優先する。

そのため、Backend AWS化では以下の方針を採用する。

```text
API Gateway HTTP API
↓
Python Lambda
↓
DynamoDB
```

この構成のメリットは以下である。

- Serverless構成としてシンプル
- API Gateway + Lambda + DynamoDB の説明がしやすい
- 常時稼働リソースを避けられる
- VPCを使用しないため、既存VPC / EC2に影響しない
- NAT Gateway、ALB、RDS、ECS Fargateを使わずに済む
- CDK Stack単位で削除対象を管理しやすい
- 個人開発として低コストで維持しやすい

一方で、以下のデメリットがある。

- ローカルMVPのFastAPI Backendとは別実装になる
- API仕様やレスポンス形式の二重管理に注意が必要になる
- 将来的にFastAPIへ寄せるか、Serverless専用Backendとして維持するか再判断が必要になる

このデメリットは、API仕様・データ項目・Markdown生成方針をdocsで管理することで抑制する。

---

## 初期API候補

Backend Serverless化で扱う初期APIは以下とする。

```text
POST /test-designs/generate
GET  /test-designs/histories
GET  /test-designs/histories/{history_id}
```

初期段階では、以下は作り込みすぎない。

```text
DELETE /test-designs/histories/{history_id}
履歴検索
履歴編集
ページネーション
認証
マルチテナント
APIキー
Usage Plan
WAF
OpenAI API連携
Amazon Bedrock連携
```

---

## 既存AWS環境との分離

Backend Serverless構成では、VPCを使用しない。

そのため、以下の既存リソースは使用・変更しない。

- 既存VPC
- 既存EC2
- 既存Security Group
- 既存IAM Role
- 既存Route 53設定
- 既存プライベート環境のリソース

本プロジェクト用リソースには、以下の命名・タグ方針を適用する。

```text
Stack名例：
AiTestDesignSupportBackendStack

リソース名例：
ai-test-design-support-backend-*
ai-test-design-support-histories
ai-test-design-support-generate-function

タグ：
Project=ai-test-design-support
Environment=portfolio
```

削除手順でも、本プロジェクト用Stack・本プロジェクト用リソースのみを削除対象とする。