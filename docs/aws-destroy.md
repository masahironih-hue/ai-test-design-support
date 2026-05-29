# AWS削除手順

## 1. 目的

このドキュメントは、AIテスト設計支援ツールの Phase 2：AWS低コスト版で作成したAWSリソースを、安全に削除するための手順を整理するものです。

対象は、S3 + CloudFront による Frontend静的配信用リソースと、API Gateway HTTP API + Python Lambda + DynamoDB による Backend APIリソースです。

削除手順では、以下を重視します。

- 本プロジェクト用リソースだけを削除する
- 既存プライベート用AWSリソースを削除・変更しない
- 削除前にStack名・削除対象・削除対象外を確認する
- DynamoDB削除により履歴データが消えることを明確にする
- S3 Bucket内オブジェクト削除を誤って別Bucketに対して実行しない
- CloudWatch Logsの削除漏れ・保持期間を確認する
- AWSアカウントID、ARN、実リソース名、URLなどの実値をREADME/docs/GitHub上の記録へ記載しない

## 2. 関連タスク

このドキュメントは、以下の作業内容に関連します。

- AWS低コスト構成・料金見積もり
- AWS Budgets・コスト制御方針整理
- AWSデプロイ・削除手順整理
- S3 CloudFront Frontend配信
- Backend Serverless構成検討
- Lambda API Gateway Backend実装
- DynamoDB履歴保存
- Frontend AWS Backend接続切替
- README最終整備

## 3. 前提

- Windows / PowerShellで作業する
- AWS CLI v2 が利用できる
- AWS CDK が利用できる
- Node.js / pnpm が利用できる
- リージョンは `ap-northeast-1` を使用する
- AWS認証情報がローカルに設定済みである
- 削除対象は本プロジェクト用CDK Stackのみとする
- CDK Stack名、CloudFormation Output、タグ、命名規則を確認してから削除する
- AWSアカウントID、ARN、S3 Bucket実名、CloudFront Distribution ID、CloudFront DomainName、API Gateway URL実値、DynamoDB Table実名、IAM情報、VPC ID、EC2 ID、IPアドレスはREADME/docs/GitHub上の記録へ記載しない

## 4. 本プロジェクト用Stack

Phase 2：AWS低コスト版では、主に以下のCDK Stackを削除対象候補とします。

```text
AiTestDesignSupportFrontendStack
AiTestDesignSupportBackendApiStack
```

削除前に、必ずローカルのCDK構成でStack一覧を確認します。

```powershell
cd infra
pnpm cdk list
```

プロファイル指定ありの場合は以下です。

```powershell
cd infra
pnpm cdk list --profile <YOUR_PROFILE>
```

`CDKToolkit` StackはCDK bootstrap用の管理Stackであり、アプリケーション本体Stackとは別に扱います。通常、本プロジェクトの削除対象には含めません。

## 5. 削除対象

### 5.1 Frontend Stackの削除対象

`AiTestDesignSupportFrontendStack` に含まれる主な削除対象は以下です。

- S3 Bucket
- S3 Bucket Policy
- S3 Bucket内のFrontend静的ファイル
- CloudFront Origin Access Control
- CloudFront Distribution
- CloudFormation Outputs

### 5.2 Backend Stackの削除対象

`AiTestDesignSupportBackendApiStack` に含まれる主な削除対象は以下です。

- API Gateway HTTP API
- Python Lambda Function
- Lambda用 IAM Role / Policy
- DynamoDB Table
- CloudWatch Logs Log Group
- CloudFormation Outputs

Backend Stack削除時、DynamoDB Tableは削除対象になります。保存済みの履歴データも削除されます。

## 6. 削除対象外

以下は削除対象に含めません。

- 既存VPC
- 既存EC2
- 既存Security Group
- 既存IAM Role
- 既存Route 53設定
- 既存S3 Bucket
- 既存CloudFront Distribution
- 既存DynamoDB Table
- 既存Lambda Function
- 既存API Gateway
- 既存CloudFormation Stack
- 既存プライベート環境のリソース
- `CDKToolkit` Stack
- NAT Gateway
- ALB
- RDS
- ECS Fargate
- EKS
- WAF

本プロジェクト用に作成していないリソースは削除対象に含めません。

## 7. 削除前チェック

削除前に以下を確認します。

- [ ] `pnpm cdk list` で本プロジェクト用Stack名を確認した
- [ ] 削除対象Stackが `AiTestDesignSupportFrontendStack` または `AiTestDesignSupportBackendApiStack` である
- [ ] `CDKToolkit` Stackを削除対象にしていない
- [ ] 既存VPC / EC2 / Security Group / IAM Role / Route 53が削除対象に含まれていない
- [ ] 本プロジェクト以外のS3 Bucketを指定していない
- [ ] 本プロジェクト以外のCloudFront Distributionを指定していない
- [ ] 本プロジェクト以外のDynamoDB Tableを指定していない
- [ ] 本プロジェクト以外のLambda Functionを指定していない
- [ ] DynamoDB Table削除により履歴データが消えることを理解している
- [ ] README/docs/GitHub上の記録にAWSアカウントID、ARN、実リソース名、URLなどを記載していない
- [ ] `.env`、`.env.local`、AWS認証情報、APIキー、DBファイルがGit管理対象に含まれていない

## 8. 全体削除時の推奨順序

Phase 2：AWS低コスト版のFrontend / Backendを両方削除する場合は、以下の順序を推奨します。

```text
1. CDK Stack一覧確認
2. Backend Stack削除
3. Backend Stack削除確認
4. Backend関連リソースの残存確認
5. Frontend S3 Bucket名取得
6. Frontend S3 Bucket内オブジェクト確認
7. Frontend S3 Bucket内オブジェクト削除
8. Frontend S3 Bucket空確認
9. Frontend Stack削除
10. Frontend Stack削除確認
11. Frontend関連リソースの残存確認
12. CloudWatch Logs / Billing / Budgets確認
```

Backendを先に削除すると、Frontendが一時的にBackend APIを呼び出せない状態になります。最終的にFrontendも削除する前提であれば問題ありません。

Frontendだけを削除する場合、Backend Stackは残ります。Backendだけを削除する場合、Frontend Stackは残ります。削除する範囲を明確にしてから実行してください。

## 9. Backend Stack削除手順

### 9.1 Backend Stack削除前確認

```powershell
cd infra
pnpm cdk list
```

削除対象Stackが `AiTestDesignSupportBackendApiStack` であることを確認します。

必要に応じて差分を確認します。

```powershell
pnpm cdk diff AiTestDesignSupportBackendApiStack
```

プロファイル指定ありの場合は以下です。

```powershell
pnpm cdk diff AiTestDesignSupportBackendApiStack --profile <YOUR_PROFILE>
```

### 9.2 Backend Stack削除

```powershell
cd infra
pnpm cdk destroy AiTestDesignSupportBackendApiStack
```

プロファイル指定ありの場合は以下です。

```powershell
cd infra
pnpm cdk destroy AiTestDesignSupportBackendApiStack --profile <YOUR_PROFILE>
```

確認プロンプトが表示された場合は、削除対象Stackが `AiTestDesignSupportBackendApiStack` であることを確認してから続行します。

### 9.3 Backend Stack削除確認

CloudFormation Stackの削除状態を確認します。

```powershell
aws cloudformation describe-stacks `
  --stack-name AiTestDesignSupportBackendApiStack `
  --region ap-northeast-1
```

プロファイル指定ありの場合は以下です。

```powershell
aws cloudformation describe-stacks `
  --stack-name AiTestDesignSupportBackendApiStack `
  --region ap-northeast-1 `
  --profile <YOUR_PROFILE>
```

Stack削除後は、Stackが存在しない旨のエラーになる場合があります。その場合、`AiTestDesignSupportBackendApiStack` は削除済みと判断できます。

### 9.4 Backend関連リソースの残存確認

必要に応じて、以下でBackend関連リソースの残存を確認します。

```powershell
aws apigatewayv2 get-apis --region ap-northeast-1
aws lambda list-functions --region ap-northeast-1
aws dynamodb list-tables --region ap-northeast-1
aws logs describe-log-groups --region ap-northeast-1
```

プロファイル指定ありの場合は以下です。

```powershell
aws apigatewayv2 get-apis --region ap-northeast-1 --profile <YOUR_PROFILE>
aws lambda list-functions --region ap-northeast-1 --profile <YOUR_PROFILE>
aws dynamodb list-tables --region ap-northeast-1 --profile <YOUR_PROFILE>
aws logs describe-log-groups --region ap-northeast-1 --profile <YOUR_PROFILE>
```

出力にAWSアカウントID、ARN、API URL、実リソース名などが含まれる場合があります。README/docs/GitHub上の記録へ貼り付ける場合は、必ずマスキングしてください。

## 10. DynamoDB削除時の注意

DynamoDBはBackend Stackで作成します。

Backend Stack削除時、DynamoDB Tableと保存済みの履歴データは削除対象に含まれます。

削除前に、以下を確認してください。

- [ ] DynamoDB Tableが本プロジェクト用Stackに含まれるものである
- [ ] 保存済み履歴データが削除されることを理解している
- [ ] DynamoDB Table実名をREADME/docs/GitHub上の記録へ記載していない
- [ ] 本プロジェクト以外のDynamoDB Tableを削除対象にしていない

## 11. CloudWatch Logs削除時の注意

Lambdaを作成すると、CloudWatch Logsにロググループが作成されます。

初期方針では、ログ保持期間を7日に設定します。

削除時は以下を確認します。

- [ ] Lambda用ロググループが本プロジェクト用である
- [ ] ログ保持期間が7日になっている
- [ ] 不要なロググループが残っていない
- [ ] ログに仕様本文、Markdown全文、APIキー、認証情報、AWS識別子、個人情報、顧客情報、業務機密が出力されていない

CloudWatch Logs Log GroupがStack削除後に残る場合は、対象が本プロジェクト用であることを確認したうえで、削除要否を判断します。判断に迷う場合は、ログ保持期間7日で自然削除される運用も選択肢です。

## 12. Frontend Stack削除手順

### 12.1 Frontend Stack削除前確認

```powershell
cd infra
pnpm cdk list
```

削除対象Stackが `AiTestDesignSupportFrontendStack` であることを確認します。

必要に応じて差分を確認します。

```powershell
pnpm cdk diff AiTestDesignSupportFrontendStack
```

プロファイル指定ありの場合は以下です。

```powershell
pnpm cdk diff AiTestDesignSupportFrontendStack --profile <YOUR_PROFILE>
```

### 12.2 対象S3 Bucket名を取得

対象S3 Bucket名は、CloudFormation Output `FrontendBucketName` から取得します。

```powershell
$bucketName = aws cloudformation describe-stacks `
  --stack-name AiTestDesignSupportFrontendStack `
  --region ap-northeast-1 `
  --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" `
  --output text

Write-Host $bucketName
```

プロファイル指定ありの場合は以下です。

```powershell
$bucketName = aws cloudformation describe-stacks `
  --stack-name AiTestDesignSupportFrontendStack `
  --region ap-northeast-1 `
  --profile <YOUR_PROFILE> `
  --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" `
  --output text

Write-Host $bucketName
```

実S3 Bucket名はREADME/docs/GitHub上の記録へ記載しません。

### 12.3 対象S3 Bucketの中身を確認

```powershell
aws s3 ls "s3://$bucketName/" --recursive
```

プロファイル指定ありの場合は以下です。

```powershell
aws s3 ls "s3://$bucketName/" --recursive --profile <YOUR_PROFILE>
```

対象Bucketが本プロジェクト用であることを確認してから、次の削除手順へ進みます。

### 12.4 対象S3 Bucketの中身を削除

このプロジェクトでは、初期構成をシンプルに保つため、`autoDeleteObjects: true` は使用しません。

`cdk destroy` 前に、対象S3 Bucketの中身を手動で削除します。

```powershell
aws s3 rm "s3://$bucketName/" --recursive
```

プロファイル指定ありの場合は以下です。

```powershell
aws s3 rm "s3://$bucketName/" --recursive --profile <YOUR_PROFILE>
```

手入力で別Bucketを指定すると、別用途のS3 Bucketを削除するリスクがあります。必ずCloudFormation Outputから取得した本プロジェクト用S3 Bucket名を使用してください。

### 12.5 空になったことを確認

```powershell
aws s3 ls "s3://$bucketName/" --recursive
```

プロファイル指定ありの場合は以下です。

```powershell
aws s3 ls "s3://$bucketName/" --recursive --profile <YOUR_PROFILE>
```

出力がなければ空です。

### 12.6 Frontend Stack削除

```powershell
cd infra
pnpm cdk destroy AiTestDesignSupportFrontendStack
```

プロファイル指定ありの場合は以下です。

```powershell
cd infra
pnpm cdk destroy AiTestDesignSupportFrontendStack --profile <YOUR_PROFILE>
```

確認プロンプトが表示された場合は、削除対象Stackが `AiTestDesignSupportFrontendStack` であることを確認してから続行します。

### 12.7 Frontend Stack削除確認

CloudFormation Stackの削除状態を確認します。

```powershell
aws cloudformation describe-stacks `
  --stack-name AiTestDesignSupportFrontendStack `
  --region ap-northeast-1
```

プロファイル指定ありの場合は以下です。

```powershell
aws cloudformation describe-stacks `
  --stack-name AiTestDesignSupportFrontendStack `
  --region ap-northeast-1 `
  --profile <YOUR_PROFILE>
```

Stack削除後は、Stackが存在しない旨のエラーになる場合があります。その場合、`AiTestDesignSupportFrontendStack` は削除済みと判断できます。

### 12.8 Frontend関連リソースの残存確認

必要に応じて、以下でFrontend関連リソースの残存を確認します。

```powershell
aws s3 ls
aws cloudfront list-distributions
```

プロファイル指定ありの場合は以下です。

```powershell
aws s3 ls --profile <YOUR_PROFILE>
aws cloudfront list-distributions --profile <YOUR_PROFILE>
```

出力に実Bucket名、CloudFront Distribution ID、CloudFront DomainNameなどが含まれる場合があります。README/docs/GitHub上の記録へ貼り付ける場合は、必ずマスキングしてください。

## 13. 手動削除を採用する理由

`autoDeleteObjects: true` を使用すると、S3 Bucket削除時にオブジェクトを削除するためのCDK管理カスタムリソースが追加されます。

その場合、Lambda、IAM Role、IAM Policy、Custom Resourceなどが増える可能性があります。

このプロジェクトでは、S3 + CloudFront構成を小さく保つことを優先し、以下の方針を採用します。

```text
autoDeleteObjects: false
cdk destroy 前に対象S3 Bucketの中身を手動削除
```

## 14. 削除対象の確認方針

削除前に、必ず対象が本プロジェクト用リソースであることを確認します。

確認する観点は以下です。

- Stack名に `AiTestDesignSupport` または本プロジェクト用の命名が含まれていること
- リソース名に `ai-test-design-support` が含まれていること
- 可能な範囲で `Project=ai-test-design-support` タグが付与されていること
- 既存プライベート環境のVPC / EC2 / Security Group / IAM Role / Route 53が削除対象に含まれていないこと
- AWSアカウントID、ARN、VPC ID、EC2 ID、IPアドレスなどをREADME/docs/GitHub上の記録へ記載していないこと

## 15. 削除後チェック

削除後に以下を確認します。

- [ ] `AiTestDesignSupportBackendApiStack` が削除済み、または意図的に残す判断をしている
- [ ] `AiTestDesignSupportFrontendStack` が削除済み、または意図的に残す判断をしている
- [ ] 対象S3 Bucketが削除済みである
- [ ] 対象CloudFront Distributionが削除済みである
- [ ] 対象API Gateway HTTP APIが削除済みである
- [ ] 対象Lambda Functionが削除済みである
- [ ] 対象DynamoDB Tableが削除済みである
- [ ] 対象CloudWatch Logs Log Groupが削除済み、または保持期間7日で残す判断をしている
- [ ] 既存VPC / EC2 / Security Group / IAM Role / Route 53に影響していない
- [ ] 本プロジェクト以外のS3 Bucketを削除していない
- [ ] 本プロジェクト以外のCloudFront Distributionを削除していない
- [ ] 本プロジェクト以外のAPI Gateway / Lambda / DynamoDBを削除していない
- [ ] AWS Budgets / Billingで想定外の課金見込みがない

## 16. README / docs / Release表現への影響

AWSリソースを削除した場合でも、以下の表現は可能です。

```text
AWS低コスト版では、S3 + CloudFront、API Gateway HTTP API、Python Lambda、DynamoDB を使い、画面上で生成・履歴保存・履歴一覧・履歴詳細まで確認しました。
```

削除後は、必要に応じて以下のように表現します。

```text
AWS低コスト版は構築・動作確認済みです。検証後はコスト管理のため、不要なAWSリソースを削除する運用としています。
```

以下のような表現は避けます。

```text
現在もAWS上で稼働中です。
公開URLで常時利用可能です。
本番環境として運用中です。
商用SaaSとして運用中です。
```

## 17. 過去の削除確認結果

S3 CloudFront Frontend配信タスクでは、Frontend Stackについて以下を確認済みです。

- 対象S3 Bucketの中身を手動削除
- `pnpm cdk destroy AiTestDesignSupportFrontendStack` 相当の削除確認
- 本プロジェクト用S3 + CloudFront構成の削除確認
- 既存VPC / EC2 / Security Group / Route 53を使用・変更していないことの確認

Backend Stackを含むPhase 2全体の削除確認は、この手順に従って別途実施します。

## 18. 注意事項

削除コマンドでは、必ずCloudFormation OutputやCDK Stack名から確認した本プロジェクト用リソースを対象にします。

手入力で別Bucket、別Stack、別リソース名を指定すると、本プロジェクト以外のAWSリソースを削除するリスクがあります。

以下はREADME/docs/GitHub上の記録へ記載しません。

- AWSアカウントID
- IAM ARN
- 実S3 Bucket名
- CloudFront Distribution ID
- CloudFront DomainName
- API Gateway URL実値
- DynamoDB Table実名
- VPC ID
- EC2 ID
- IPアドレス
- AWS認証情報
- APIキー
- `.env` / `.env.local` の実値

## 19. 次アクション

削除作業を実施する場合は、以下の順で進めます。

1. `pnpm cdk list` でStack一覧を確認する
2. 削除対象Stackと削除対象外Stackを確認する
3. Backend Stackを削除するか判断する
4. Backend Stackを削除する場合、DynamoDB履歴データが削除されることを確認する
5. Backend Stackを削除する
6. Backend関連リソースの残存を確認する
7. Frontend Stackを削除するか判断する
8. Frontend Stackを削除する場合、対象S3 Bucket名をCloudFormation Outputから取得する
9. 対象S3 Bucketの中身を削除する
10. Frontend Stackを削除する
11. Frontend関連リソースの残存を確認する
12. CloudWatch Logs / Billing / Budgetsを確認する
13. README / docs / Release表現の修正要否を確認する
14. `[管理] タスク管理` へ戻す完了サマリを作成する
