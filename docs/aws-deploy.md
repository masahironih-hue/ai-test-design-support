# AWSデプロイ手順

## 1. 目的

このドキュメントは、AIテスト設計支援ツールの Phase 2：AWS低コスト版における、S3 + CloudFront Frontend静的配信と Backend最小API のデプロイ手順を整理するためのものです。

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

今回作成するのは、本プロジェクト用CDK Stackに含まれるS3 Bucket、S3 Bucket Policy、CloudFront OAC、CloudFront Distribution、API Gateway HTTP API、Lambda、DynamoDB、CloudWatch Logsです。

## 5. デプロイ対象

| 対象 | 内容 |
|---|---|
| Frontend静的ファイル | `frontend/out` |
| IaC | TypeScript CDK |
| CDK Stack | `AiTestDesignSupportFrontendStack` |
| 配置先 | Private S3 Bucket |
| 配信 | CloudFront Distribution |
| S3アクセス制御 | CloudFront OAC |

Backend最小APIは、別Stack `AiTestDesignSupportBackendApiStack` で管理します。Route 53、ACM、WAFは今回対象外です。

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
cd ../frontend
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

Frontend Stackのみを確認している場合、以下が含まれる場合はデプロイ前に確認します。Backend Stackを同時に確認している場合、Lambda、API Gateway、DynamoDBは作成対象です。

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
cd ../frontend
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
- Frontend接続切替が未対応であることを確認する

## Backend最小APIのデプロイ手順

Phase 2 Backend最小APIとして、API Gateway HTTP API + Python Lambda + DynamoDB によるMock生成APIと履歴保存APIを追加する。

```text
Frontend：S3 + CloudFront で静的配信済み
Backend API：API Gateway HTTP API + Python Lambda でMock生成API・履歴APIを追加
履歴保存：DynamoDB
```

構成は以下とする。

```text
API Gateway HTTP API
↓
Python Lambda
↓
LLM Mock相当の固定生成処理
↓
DynamoDB履歴保存
↓
JSONレスポンス返却
```

今回、OpenAI API連携、Amazon Bedrock連携、FastAPI on Lambda、Frontend接続切替、Cognito認証、本格API認証は行わない。

---

## Stack分割方針

Frontend配信とBackend Serverless構成は、責務を分けるためStackを分割する方針とする。

想定例：

```text
Frontend：
AiTestDesignSupportFrontendStack

Backend：
AiTestDesignSupportBackendApiStack
```

Stackを分割する理由は以下。

- Frontend配信とBackend APIを独立して変更しやすくする
- 削除対象を明確にする
- Backendだけを後続で作成・削除しやすくする
- 既存AWS環境との混同を避ける
- README / docsで構成を説明しやすくする

---

## Backend Stackで作成するリソース

Backend Stackでは、以下を作成する。

| リソース | 用途 |
|---|---|
| API Gateway HTTP API | `POST /test-designs/generate`、履歴取得APIを公開する |
| Python Lambda | LLM Mock相当の固定生成処理を実行する |
| DynamoDB Table | 生成履歴を保存する |
| Lambda Integration | HTTP APIとLambdaを接続する |
| Lambda実行Role | Lambda実行とCloudWatch Logs出力を許可する |
| CloudWatch Logs Log Group | Lambdaログを保存する |
| CORS設定 | 将来のFrontend接続切替に備えて設定する |

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

CDK context `allowedOrigin` を指定した場合、そのOriginのみを許可する。

```powershell
pnpm cdk deploy AiTestDesignSupportBackendApiStack `
  -c allowedOrigin=https://example.cloudfront.net
```

context未指定時は初期検証用として `*` を許可する。これは本番向け設定ではない。

---

## Backend Stack synth / diff

```powershell
cd infra
pnpm install
pnpm cdk synth
pnpm cdk diff AiTestDesignSupportBackendApiStack
```

diffでは、以下が作成されることを確認する。

- API Gateway HTTP API
- Lambda
- Lambda用IAM Role
- CloudWatch Logs Log Group、保持期間7日
- Lambda Integration
- `POST /test-designs/generate` route
- `GET /test-designs/histories` route
- `GET /test-designs/histories/{history_id}` route
- DynamoDB Table
- Lambda環境変数 `HISTORIES_TABLE_NAME`
- Lambda IAM権限 `dynamodb:PutItem`、`dynamodb:GetItem`、`dynamodb:Scan`

以下が作成・変更されないことを確認する。

- 既存VPC
- 既存EC2
- 既存Security Group
- 既存Route 53設定
- NAT Gateway
- ALB
- RDS
- ECS Fargate / EKS
- WAF

## Backend Stack deploy

diff確認後、問題がなければBackend Stackのみdeployする。

```powershell
pnpm cdk deploy AiTestDesignSupportBackendApiStack
```

deploy後に出力されるAPI Gateway URL実値は、README/docs/GitHub Issueへ記載しない。

疎通確認ではローカルPowerShell変数としてのみ扱う。

## Backend API単体疎通確認

API Gateway URLは実値をローカル変数に設定する。

```powershell
$ApiUrl = "https://<api-id>.execute-api.<region>.amazonaws.com/test-designs/generate"

$Body = @{
  title = "ログイン画面"
  target_type = "screen"
  test_level = "integration"
  spec_text = "利用者IDとパスワードを入力し、認証に成功した場合はメニュー画面へ遷移する。認証に失敗した場合はエラーメッセージを表示する。"
  supplement = "業務系Webアプリのログイン機能を想定する。"
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Uri $ApiUrl `
  -Method Post `
  -ContentType "application/json; charset=utf-8" `
  -Body $Body
```

確認観点は以下。

- HTTP 200で返る
- `title`、`target_type`、`test_level` が返る
- `viewpoints`、`test_cases`、`markdown` が返る
- `history_id`、`created_at` が返る
- レスポンスがJSONとして扱える

履歴一覧APIは以下で確認する。

```powershell
$HistoriesUrl = "https://<api-id>.execute-api.<region>.amazonaws.com/test-designs/histories"

$Histories = Invoke-RestMethod `
  -Uri $HistoriesUrl `
  -Method Get

$Histories
```

履歴詳細APIは、生成APIまたは履歴一覧APIで取得した `history_id` を使って確認する。

```powershell
$HistoryId = "<history_id>"
$HistoryDetailUrl = "https://<api-id>.execute-api.<region>.amazonaws.com/test-designs/histories/$HistoryId"

Invoke-RestMethod `
  -Uri $HistoryDetailUrl `
  -Method Get
```

存在しない履歴IDでは404系レスポンスになることを確認する。

異常系は必須項目不足で確認する。

```powershell
$InvalidBody = @{
  title = "ログイン画面"
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Uri $ApiUrl `
  -Method Post `
  -ContentType "application/json; charset=utf-8" `
  -Body $InvalidBody
```

確認観点は以下。

- 400系エラーが返る
- エラーレスポンスがJSONで返る
- 内部例外やスタックトレースをそのまま返していない

## CloudWatch Logs確認

Lambdaログでは以下を確認する。

- ログ保持期間が7日である
- request body全体が出ていない
- `spec_text` が出ていない
- `supplement` が出ていない
- `markdown` が出ていない
- DynamoDB item全体が出ていない
- 認証情報やAWS識別子が出ていない
- エラー時に過剰な詳細を出していない

---

## 実装・deploy前の確認事項

Backend Serverless構成をデプロイする前に、以下を確認する。

- [ ] AWS Pricing Calculatorで料金を再確認した
- [ ] AWS Budgetsまたはコスト監視方針を確認した
- [ ] CloudWatch Logs保持期間を7日にする方針を確認した
- [ ] DynamoDB Tableが作成対象であり、削除時に履歴データが失われることを確認した
- [ ] 既存VPC / EC2 / Security Group / Route 53 を使用・変更しない方針を確認した
- [ ] Backend Stack名が `AiTestDesignSupportBackendApiStack` であることを確認した
- [ ] AWSアカウントID、VPC ID、EC2 ID、IPアドレス、IAM認証情報をdocsへ記載していない
- [ ] `.env`、AWS認証情報、APIキーをGit管理対象に含めない
- [ ] 実案件情報、顧客情報、業務機密をサンプルデータに使っていない

---

## Backend deploy時の注意

Backend StackはFrontend Stackとは分けてdeployする。

```powershell
pnpm cdk deploy AiTestDesignSupportBackendApiStack
```

出力されたAPI Gateway URL実値は、README/docs/GitHub Issueへ記載しない。

実値を使う場合は、PowerShell変数やローカル作業メモに限定する。

## 16. Backend APIについて

現時点では、AWS上のBackend APIはMock生成APIとDynamoDB履歴保存APIの単体疎通確認を目的とした最小構成です。

以下は未実装です。

- Frontend接続切替
- OpenAI API連携
- Amazon Bedrock連携

未実装の機能を、実装済みのようにREADME/docsへ記載しません。

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
