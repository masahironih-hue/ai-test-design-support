# AWSデプロイ手順

## 1. 目的

このドキュメントは、AIテスト設計支援ツールの Phase 2：AWS低コスト版における、AWSデプロイ手順の初版を整理するためのものです。

Phase 2初期では、ローカルMVP全体を一気にAWS化するのではなく、まず以下の構成を対象とします。

```text
S3 + CloudFront による Frontend 静的配信
```

本ドキュメントでは、AWSリソース作成前に、デプロイ対象、作成予定リソース、事前確認、デプロイ後確認、削除手順との対応を整理します。

## 2. 関連Issue

- GitHub Issue: #22 AWSデプロイ・削除手順

## 3. 前提

Phase 1：ローカルMVPでは、以下の一連の流れがローカル環境で動作確認済みです。

```text
仕様入力
↓
LLM Mockによるテスト観点生成
↓
生成結果表示
↓
Markdownコピー
↓
SQLite履歴保存
↓
履歴一覧表示
↓
履歴詳細表示
↓
保存済みMarkdownコピー
```

Phase 2初期では、まずFrontendの静的配信をAWSへ展開します。

Backend API、SQLite履歴保存、DynamoDB、API Gateway、Lambdaは本ドキュメントの初期対象外です。

## 4. 重要な分離方針

本プロジェクトでは、既存のプライベート用VPC/EC2と同一AWSアカウントを使用します。

ただし、既存環境との混同や誤変更を防ぐため、AIテスト設計支援ツール用リソースは以下の方針で分離します。

- 既存プライベートVPCは使用しない
- 既存EC2へ同居デプロイしない
- 既存Security Groupを流用しない
- 既存IAM Roleを安易に流用しない
- 既存Route 53設定を安易に変更しない
- リソース名には `ai-test-design-support` を含める
- タグ `Project=ai-test-design-support` を付与する
- 削除手順では、本プロジェクト用リソースのみを削除対象にする

AWSアカウントID、VPC ID、EC2 ID、IPアドレス、IAMアクセスキー等は、このドキュメントには記載しません。

## 5. デプロイ対象

Phase 2初期のデプロイ対象は、Frontendのbuild成果物です。

| 項目 | 内容 |
|---|---|
| 対象 | Frontend build成果物 |
| 技術 | Next.js / React / TypeScript |
| 配置先 | S3 Bucket |
| 配信 | CloudFront |
| Backend API | 初期対象外 |
| DB | 初期対象外 |
| LLM API | 初期対象外 |

## 6. 作成予定リソース

Phase 2初期で作成予定のAWSリソースは以下です。

| リソース | 用途 |
|---|---|
| S3 Bucket | Frontend build成果物の配置 |
| S3 Object | HTML / CSS / JavaScript / 画像などの静的ファイル |
| CloudFront Distribution | S3上のFrontendをHTTPS配信 |
| CloudFront Origin Access Control | CloudFrontからS3へ安全にアクセスするための制御 |
| IAM Role / Policy | CDKまたはサービス連携で必要な場合のみ |
| CDK Stack | CDKで構築する場合の管理単位 |

Phase 2初期では、以下は作成しません。

- VPC
- Subnet
- EC2
- Security Group
- NAT Gateway
- ALB
- RDS
- ECS Fargate
- API Gateway
- Lambda
- DynamoDB
- Bedrock
- OpenAI API連携

## 7. 命名方針

本プロジェクト用リソースには、原則として以下を含めます。

```text
ai-test-design-support
```

命名例：

```text
ai-test-design-support-frontend-dev
ai-test-design-support-cloudfront-dev
ai-test-design-support-cdk-dev
```

CDK Stack名の例：

```text
AiTestDesignSupportFrontendDevStack
```

既存プライベート用VPC/EC2関連の名前や既存リソース名は流用しません。

## 8. タグ方針

可能な範囲で、以下のタグを付与します。

| Key | Value例 | 用途 |
|---|---|---|
| Project | `ai-test-design-support` | 本プロジェクト用リソースの識別 |
| Environment | `dev` | 開発・検証環境であることを明示 |
| Purpose | `portfolio` | ポートフォリオ用途であることを明示 |
| ManagedBy | `cdk` | CDK管理対象であることを明示 |

タグが付けられない、またはコスト配賦に反映されにくいサービスについては、リソース名とCDK Stack名で補完します。

## 9. 事前確認

AWSリソース作成前に、以下を確認します。

```text
- AWS Pricing Calculatorで料金見積もりを確認済みである
- AWS Budgets・コスト制御方針を整理済みである
- AWS削除手順を作成済みである
- 既存VPC/EC2を使用しない方針が明確である
- 作成予定リソース名に ai-test-design-support を含める方針である
- Project=ai-test-design-support タグを付与する方針である
- AWSアカウントID、VPC ID、EC2 ID、IPアドレス、IAM情報をdocsに記載していない
```

関連docs：

- `docs/aws-cost-estimate.md`
- `docs/aws-budget.md`
- `docs/aws-destroy.md`
- `docs/aws-architecture.md`

## 10. Frontend build確認

AWSへ配置する前に、ローカルでFrontendのbuildが成功することを確認します。

```powershell
cd frontend
pnpm lint
pnpm build
```

確認観点：

```text
- lintが成功すること
- buildが成功すること
- build成果物に機密情報が含まれていないこと
- .env.local やAPIキーがbuild成果物やGit管理対象に含まれていないこと
```

## 11. デプロイ方式

Phase 2では、AWS CDKを優先候補とします。

理由は以下です。

- 作成リソースをコードで管理できる
- Stack単位で削除対象を把握しやすい
- README / docsで構成を説明しやすい
- 既存AWS環境と分離するための命名・タグ管理を反映しやすい

ただし、本IssueではCDK実装は行いません。

CDK実装は、後続Issue `[AWS] S3 CloudFront Frontend配信` で扱います。

## 12. デプロイ時に作成する構成

想定構成は以下です。

```text
Browser
↓
CloudFront
↓
S3 Bucket
↓
Frontend build files
```

S3 Bucketは、原則として直接public公開せず、CloudFront経由で配信する構成を候補とします。

CloudFrontからS3へのアクセス制御には、Origin Access Controlを候補とします。

## 13. デプロイ後確認

S3 + CloudFront配信後は、以下を確認します。

```text
- CloudFrontのURLでFrontend画面が表示できる
- トップページが表示できる
- 静的ファイルが正しく配信されている
- ブラウザコンソールに明らかなエラーが出ていない
- Backend API未接続部分の扱いが想定どおりである
- S3 Bucketが意図せずpublic公開されていない
- CloudFront DistributionのOriginが本プロジェクト用S3 Bucketである
- 作成リソース名に ai-test-design-support が含まれている
- 可能な範囲で Project=ai-test-design-support タグが付与されている
```

## 14. Backend APIについて

Phase 2初期では、Backend APIはAWS化しません。

そのため、FrontendからBackend APIを呼び出す箇所については、以下のいずれかの扱いを後続実装時に検討します。

```text
- ローカルBackend接続前提のままとする
- AWS配信用にAPI接続部分を一時的に無効化する
- デモ用に静的表示へ切り替える
- 後続でAPI Gateway + Lambda化する
```

未実装のBackend AWS化を、実装済みのようにREADMEや面談で表現しません。

## 15. セキュリティ確認

デプロイ前後で、以下を確認します。

```text
- APIキー、パスワード、アクセストークンをGitHubに載せていない
- .env、.env.local をGit管理対象にしていない
- build成果物に秘密情報を含めていない
- 実案件情報、顧客情報、個人情報、業務機密を使用していない
- AWSアカウントID、VPC ID、EC2 ID、IPアドレス、IAM情報をdocsやREADMEに記載していない
- AWSコンソール画面キャプチャを使う場合、アカウント情報やリソースIDの映り込みに注意する
```

## 16. コスト確認

デプロイ後は、以下を確認します。

```text
- AWS Budgetsの通知設定が有効である
- S3とCloudFrontの利用量が想定範囲内である
- 既存プライベートサーバ費用と本プロジェクト追加費用を混同していない
- Cost Explorerでサービス別の増加を確認できる
- 不要なS3 ObjectやCloudFront Distributionが残っていない
```

## 17. 削除手順との対応

デプロイ後は、必ず `docs/aws-destroy.md` の削除手順で削除できる状態にします。

削除対象は以下です。

```text
- S3 Bucket
- S3 Object
- CloudFront Distribution
- CloudFront Origin Access Control
- CloudWatch Logs
- CDK Stack
- IAM Role / Policy
```

削除手順では、本プロジェクト用リソースのみを対象にします。

既存プライベート用VPC/EC2、既存Security Group、既存IAM Role、既存Route 53設定は削除対象に含めません。

## 18. READMEへ反映する内容

READMEには、詳細なAWS操作手順ではなく、以下を要約して記載します。

```text
Phase 2では、S3 + CloudFrontによるFrontend静的配信を低コストAWS構成として追加予定です。
AWSリソース作成前に、料金見積もり、Budgets、デプロイ手順、削除手順をdocsへ整理しています。
既存プライベート用VPC/EC2と同一AWSアカウントを使用しますが、本プロジェクト用リソースは命名・タグ・Stack名で分離します。
```

## 19. 現時点の結論

Phase 2初期のデプロイ対象は、以下とします。

```text
S3 + CloudFront による Frontend 静的配信
```

AWSリソース作成前に、以下を満たす必要があります。

```text
- 料金見積もりが整理済みである
- Budgets・コスト制御方針が整理済みである
- 削除手順が整理済みである
- 既存VPC/EC2と混同しない方針が明確である
- 本プロジェクト用リソースの命名・タグ方針が明確である
```

## 20. 次アクション

- `docs/aws-destroy.md` と整合しているか確認する
- 後続Issue `[AWS] S3 CloudFront Frontend配信` に進む
- CDKでS3 + CloudFront構成を作成する
- デプロイ後、READMEへAWS構成概要を反映する