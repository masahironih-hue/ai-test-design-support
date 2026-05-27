# AWSデプロイ手順

## 1. 目的

このドキュメントは、AIテスト設計支援ツールの Phase 2：AWS低コスト版における、S3 + CloudFront Frontend静的配信のデプロイ手順を整理するためのものです。

Issue #23では、AWS CDKを用いて以下を構築・確認しました。

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

## 2. 関連Issue

- GitHub Issue: #22 AWSデプロイ・削除手順
- GitHub Issue: #23 S3 CloudFront Frontend配信

## 3. 前提

- Windows / PowerShellで作業する
- AWS CLI v2 が利用できる
- AWS CDK が利用できる
- `pnpm` が利用できる
- AWS認証情報がローカルに設定済みである
- リージョンは `ap-northeast-1` を使用する
- AWSアカウントID、S3 Bucket名、CloudFront Distribution IDなどの実値はREADME/docsへ記載しない

## 4. 重要な分離方針

本プロジェクトでは、既存のプライベート用VPC/EC2と同一AWSアカウントを使用します。

ただし、以下は使用・変更しません。

- 既存VPC
- 既存EC2
- 既存Security Group
- 既存IAM Role
- 既存Route 53設定

今回作成するのは、本プロジェクト用CDK Stackに含まれるS3 Bucket、S3 Bucket Policy、CloudFront OAC、CloudFront Distributionのみです。

## 5. デプロイ対象

| 対象 | 内容 |
|---|---|
| Frontend静的ファイル | `frontend/out` |
| IaC | TypeScript CDK |
| CDK Stack | `AiTestDesignSupportFrontendStack` |
| 配置先 | Private S3 Bucket |
| 配信 | CloudFront Distribution |
| S3アクセス制御 | CloudFront OAC |

Backend API、API Gateway、Lambda、DynamoDB、Route 53、ACM、WAFは今回対象外です。

## 6. リージョン確認

```powershell
aws configure get region
```

必要に応じて、PowerShellで一時設定します。

```powershell
$env:AWS_DEFAULT_REGION="ap-northeast-1"
$env:AWS_REGION="ap-northeast-1"
```

プロファイルを使う場合は、以下で確認します。

```powershell
aws configure get region --profile <YOUR_PROFILE>
```

## 7. AWS認証確認

```powershell
aws sts get-caller-identity
```

プロファイルを使う場合は以下です。

```powershell
aws sts get-caller-identity --profile <YOUR_PROFILE>
```

この出力にはAWSアカウントIDが含まれるため、README/docs/GitHub Issue/ChatGPTへ貼り付ける場合はマスキングします。

## 8. CDK bootstrap

東京リージョンで初回デプロイする場合、CDK bootstrap が必要です。

```powershell
cd infra
pnpm cdk bootstrap
```

プロファイル指定ありの場合は以下です。

```powershell
pnpm cdk bootstrap --profile <YOUR_PROFILE>
```

bootstrapにより作成される `CDKToolkit` Stackは、CDK管理用リソースです。アプリケーション本体の `AiTestDesignSupportFrontendStack` とは分けて扱います。

## 9. Frontend静的build確認

```powershell
cd ..rontend
pnpm install
pnpm lint
pnpm build
```

`frontend/out` が生成されることを確認します。

```powershell
Test-Path .\out
Get-ChildItem .\out
```

## 10. CDK synth / diff

```powershell
cd ..\infra
pnpm install
pnpm cdk synth
pnpm cdk diff
```

プロファイル指定ありの場合は以下です。

```powershell
pnpm cdk diff --profile <YOUR_PROFILE>
```

差分に以下が含まれることを確認します。

```text
AWS::S3::Bucket
AWS::S3::BucketPolicy
AWS::CloudFront::OriginAccessControl
AWS::CloudFront::Distribution
CloudFormation Outputs
```

以下が含まれる場合は、今回の対象外のためデプロイ前に確認します。

```text
AWS::EC2::VPC
AWS::EC2::Instance
AWS::EC2::SecurityGroup
AWS::RDS::DBInstance
AWS::ElasticLoadBalancingV2::LoadBalancer
AWS::ECS::Cluster
AWS::Route53::HostedZone
AWS::Lambda::Function
AWS::ApiGateway::*
AWS::DynamoDB::*
```

## 11. CDK deploy

```powershell
pnpm cdk deploy
```

プロファイル指定ありの場合は以下です。

```powershell
pnpm cdk deploy --profile <YOUR_PROFILE>
```

CloudFront Distributionの作成には時間がかかる場合があります。  
CloudFormation Stackが `CREATE_COMPLETE` になるまで待ちます。

## 12. CloudFormation Output確認

### S3 Bucket名取得

```powershell
$bucketName = aws cloudformation describe-stacks `
  --stack-name AiTestDesignSupportFrontendStack `
  --region ap-northeast-1 `
  --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" `
  --output text

Write-Host $bucketName
```

### CloudFront DomainName取得

```powershell
$cloudFrontDomainName = aws cloudformation describe-stacks `
  --stack-name AiTestDesignSupportFrontendStack `
  --region ap-northeast-1 `
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDomainName'].OutputValue" `
  --output text

Write-Host $cloudFrontDomainName
```

### CloudFront Distribution ID取得

```powershell
$distributionId = aws cloudformation describe-stacks `
  --stack-name AiTestDesignSupportFrontendStack `
  --region ap-northeast-1 `
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" `
  --output text

Write-Host $distributionId
```

取得した実値はREADME/docs/GitHub Issueへ記載しません。

## 13. S3へ静的ファイル配置

```powershell
cd ..rontend
pnpm build
aws s3 sync .\out "s3://$bucketName/" --delete
```

プロファイル指定ありの場合は以下です。

```powershell
aws s3 sync .\out "s3://$bucketName/" --delete --profile <YOUR_PROFILE>
```

## 14. CloudFrontキャッシュ削除

```powershell
aws cloudfront create-invalidation `
  --distribution-id $distributionId `
  --paths "/*"
```

プロファイル指定ありの場合は以下です。

```powershell
aws cloudfront create-invalidation `
  --distribution-id $distributionId `
  --paths "/*" `
  --profile <YOUR_PROFILE>
```

## 15. 表示確認

ブラウザで以下を確認します。

```text
https://<CloudFrontDomainName>/
```

確認観点は以下です。

- CloudFront URLでFrontend画面が表示される
- S3 BucketがPublic公開されていない
- CloudFront OAC経由でS3へアクセスできる
- Backend API未AWS化による制約があることを確認する

## Backend Serverless構成のデプロイ方針

現時点では、S3 + CloudFront による Frontend 静的配信まで完了している。

```text
Frontend：S3 + CloudFront で静的配信済み
Backend API：未AWS化
履歴保存：ローカルSQLite
```

Backend APIをAWS化する場合は、以下の構成を候補とする。

```text
API Gateway HTTP API
↓
Python Lambda
↓
DynamoDB
```

本章は、Backend Serverless構成のデプロイ方針を整理するものであり、現時点ではまだCDK実装・AWSリソース作成・`cdk deploy` 実行手順は確定していない。

---

## Stack分割方針

Frontend配信とBackend Serverless構成は、責務を分けるためStackを分割する方針とする。

想定例：

```text
Frontend：
AiTestDesignSupportFrontendHostingStack

Backend：
AiTestDesignSupportBackendStack
```

Stackを分割する理由は以下。

- Frontend配信とBackend APIを独立して変更しやすくする
- 削除対象を明確にする
- Backendだけを後続で作成・削除しやすくする
- 既存AWS環境との混同を避ける
- README / docsで構成を説明しやすくする

---

## Backend Stackで作成する候補リソース

Backend Stackでは、以下の作成を候補とする。

| リソース | 用途 |
|---|---|
| API Gateway HTTP API | FrontendからBackend APIを呼び出す |
| Lambda | テスト設計生成API、履歴APIを実行する |
| DynamoDB Table | 生成履歴を保存する |
| IAM Role / Policy | LambdaからDynamoDBへ必要最小限のアクセスを許可する |
| CloudWatch Logs Log Group | Lambdaログを保存する |
| CORS設定 | CloudFront配信FrontendからのAPI呼び出しを許可する |

初期段階では、以下は作成しない。

- VPC
- Subnet
- Security Group
- NAT Gateway
- ALB
- ECS Fargate
- RDS
- WAF
- Cognito
- Secrets Manager
- OpenAI API / Amazon Bedrock連携用の秘密情報

---

## Frontendとの接続方針

FrontendからBackend APIを呼び出す場合は、API GatewayのエンドポイントURLをFrontend側で参照できるようにする。

候補は以下。

```text
NEXT_PUBLIC_API_BASE_URL
```

ローカル開発時とAWS配信時で接続先を切り替える。

```text
ローカル開発：
http://localhost:8000

AWS配信：
API Gateway HTTP API のURL
```

ただし、Frontendが静的export構成の場合、ビルド時に環境変数が埋め込まれる点に注意する。  
API URLを変更する場合は、Frontend再build・再deployが必要になる可能性がある。

---

## CORS方針

Backend APIでは、CloudFront配信Frontendからの呼び出しを許可する。

初期方針は以下。

| 項目 | 方針 |
|---|---|
| 許可Origin | CloudFront URLを候補とする |
| 許可Method | `GET`, `POST`, `OPTIONS` |
| 許可Header | 必要最小限 |
| 認証 | 初期段階ではなし |
| Cookie | 初期段階では使わない |

検証目的で一時的に広めのCORS設定を使う場合も、README / docsでは検証用であることを明記する。

---

## 実装前の確認事項

Backend Serverless構成を実装する前に、以下を確認する。

- [ ] AWS Pricing Calculatorで料金を再確認した
- [ ] AWS Budgetsまたはコスト監視方針を確認した
- [ ] CloudWatch Logs保持期間を7日にする方針を確認した
- [ ] DynamoDBテーブル削除時に履歴データが消えることを理解した
- [ ] 既存VPC / EC2 / Security Group / Route 53 を使用・変更しない方針を確認した
- [ ] 本プロジェクト用Stack名・リソース名・タグを決めた
- [ ] AWSアカウントID、VPC ID、EC2 ID、IPアドレス、IAM認証情報をdocsへ記載していない
- [ ] `.env`、AWS認証情報、APIキーをGit管理対象に含めない
- [ ] 実案件情報、顧客情報、業務機密をサンプルデータに使っていない

---

## デプロイ手順の詳細化タイミング

具体的な `cdk deploy` 手順は、Backend Stack実装Issueで整理する。

この時点では、以下を確定させる。

- 採用構成
- Stack分割方針
- 作成候補リソース
- CORS方針
- Frontend接続方針
- 料金・ログ・削除・分離方針

CDKコード実装後に、実際のコマンド、確認手順、出力値、削除手順を追記する。

## 16. Backend APIについて

現時点では、Backend APIはAWS化していません。

そのため、CloudFrontで配信されるFrontend上では画面表示まで確認できますが、以下の機能を利用するには、ローカルBackendまたは後続のAWS Backend構成が必要です。

- テスト設計生成API
- 履歴一覧API
- 履歴詳細API

未実装のBackend AWS化を、実装済みのようにREADME/docsへ記載しません。

## 17. セキュリティ確認

デプロイ前後に以下を確認します。

- AWSアカウントIDをREADME/docsへ記載していない
- IAM ARNをREADME/docsへ記載していない
- 実S3 Bucket名をREADME/docsへ記載していない
- CloudFront Distribution IDをREADME/docsへ記載していない
- `.env` / `.env.local` / AWS認証情報をGit管理対象に含めていない
- 既存VPC / EC2 / Security Group / Route 53を使用・変更していない
- S3 BucketをPublic公開していない

## 18. 実施結果

Issue #23では、以下を確認済みです。

- `pnpm lint` 成功
- `pnpm build` 成功
- `pnpm cdk synth` 成功
- `pnpm cdk diff` 確認
- `pnpm cdk deploy` 成功
- S3 Bucket作成
- CloudFront Distribution作成
- CloudFront OACによるS3 private配信
- CloudFront URLでFrontend画面表示確認
- `pnpm cdk destroy` による削除確認

## 19. 次アクション

- READMEへAWS低コスト版の検証結果を反映する
- `docs/aws-destroy.md` へ削除確認済み手順を反映する
- `docs/aws-cost-estimate.md` と整合させる
- Git管理対象に不要ファイル・秘密情報が含まれていないことを確認する
- Issue #23 closeコメントを作成する
