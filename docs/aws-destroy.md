# AWS削除手順

## 1. 目的

このドキュメントは、AIテスト設計支援ツールの Phase 2：AWS低コスト版における、S3 + CloudFront Frontend静的配信用リソースの削除手順を整理するためのものです。

Issue #23では、S3 + CloudFront構成を作成し、CloudFront URLで画面表示を確認した後、対象S3 Bucketの中身を手動削除し、`pnpm cdk destroy` による削除まで確認しました。

## 2. 関連Issue

- GitHub Issue: #22 AWSデプロイ・削除手順
- GitHub Issue: #23 S3 CloudFront Frontend配信

## 3. 前提

- Windows / PowerShellで作業する
- AWS CLI v2 が利用できる
- AWS CDK が利用できる
- リージョンは `ap-northeast-1` を使用する
- AWS認証情報がローカルに設定済みである
- 削除対象は本プロジェクト用CDK Stackのみとする
- AWSアカウントID、S3 Bucket名、CloudFront Distribution IDなどの実値はREADME/docsへ記載しない

## 4. 削除対象

削除対象は、CDK Stack `AiTestDesignSupportFrontendStack` に含まれる以下です。

- S3 Bucket
- S3 Bucket Policy
- CloudFront Origin Access Control
- CloudFront Distribution
- CloudFormation Outputs

## 5. 削除対象外

以下は削除対象に含めません。

- 既存VPC
- 既存EC2
- 既存Security Group
- 既存IAM Role
- 既存Route 53設定
- 本プロジェクト以外のS3 Bucket
- 本プロジェクト以外のCloudFront Distribution
- 本プロジェクト以外のCloudFormation Stack

CDK bootstrapにより作成される `CDKToolkit` Stackは、CDK管理用リソースです。  
アプリケーション本体の `AiTestDesignSupportFrontendStack` とは別に扱います。

## 6. 削除前チェック

削除前に以下を確認します。

- 削除対象Stack名が `AiTestDesignSupportFrontendStack` である
- 対象S3 BucketがCloudFormation Output `FrontendBucketName` から取得したものである
- 対象CloudFront DistributionがCloudFormation Output `CloudFrontDistributionId` から取得したものである
- 既存VPC / EC2 / Security Group / Route 53が削除対象に含まれていない
- 本プロジェクト以外のS3 Bucketを指定していない

## 7. 対象S3 Bucket名を取得

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

実値をREADME/docs/GitHub Issueへ記載しません。

## 8. 対象S3 Bucketの中身を確認

```powershell
aws s3 ls "s3://$bucketName/" --recursive
```

プロファイル指定ありの場合は以下です。

```powershell
aws s3 ls "s3://$bucketName/" --recursive --profile <YOUR_PROFILE>
```

## 9. 対象S3 Bucketの中身を削除

このプロジェクトでは、初期構成をシンプルに保つため、`autoDeleteObjects: true` は使用しません。  
`cdk destroy` 前に、対象S3 Bucketの中身を手動で削除します。

```powershell
aws s3 rm "s3://$bucketName/" --recursive
```

プロファイル指定ありの場合は以下です。

```powershell
aws s3 rm "s3://$bucketName/" --recursive --profile <YOUR_PROFILE>
```

## 10. 空になったことを確認

```powershell
aws s3 ls "s3://$bucketName/" --recursive
```

出力がなければ空です。

## 11. CDK destroy

```powershell
cd infra
pnpm cdk destroy
```

プロファイル指定ありの場合は以下です。

```powershell
pnpm cdk destroy --profile <YOUR_PROFILE>
```

確認プロンプトが表示された場合は、削除対象Stackが `AiTestDesignSupportFrontendStack` であることを確認してから続行します。

## 12. 削除確認

CloudFormation Stackの削除状態を確認します。

```powershell
aws cloudformation describe-stacks `
  --stack-name AiTestDesignSupportFrontendStack `
  --region ap-northeast-1
```

Stack削除後は、Stackが存在しない旨のエラーになる場合があります。  
その場合、`AiTestDesignSupportFrontendStack` は削除済みと判断できます。

プロファイル指定ありの場合は以下です。

```powershell
aws cloudformation describe-stacks `
  --stack-name AiTestDesignSupportFrontendStack `
  --region ap-northeast-1 `
  --profile <YOUR_PROFILE>
```

## 13. 削除後チェック

削除後に以下を確認します。

- `AiTestDesignSupportFrontendStack` が削除済みである
- 対象S3 Bucketが削除済みである
- 対象CloudFront Distributionが削除済みである
- 既存VPC / EC2 / Security Group / Route 53に影響していない
- 本プロジェクト以外のS3 Bucketを削除していない

## 14. 手動削除を採用する理由

`autoDeleteObjects: true` を使用すると、S3 Bucket削除時にオブジェクトを削除するためのCDK管理カスタムリソースが追加されます。  
その場合、Lambda、IAM Role、IAM Policy、Custom Resourceなどが増える可能性があります。

Issue #23では、S3 + CloudFront構成を小さく保つことを優先し、以下の方針を採用します。

```text
autoDeleteObjects: false
cdk destroy 前に対象S3 Bucketの中身を手動削除
```

## Backend Serverless構成の削除方針

Backend Serverless構成を実装した場合、以下のリソースが削除対象になる。

```text
API Gateway HTTP API
Lambda
DynamoDB Table
CloudWatch Logs Log Group
IAM Role / Policy
```

現時点ではBackend Serverless構成は未実装であるため、本章は削除方針の整理であり、具体的な削除コマンドはBackend実装後に確定する。

---

## 削除対象の確認方針

削除前に、必ず対象が本プロジェクト用リソースであることを確認する。

確認する観点は以下。

- Stack名に `AiTestDesignSupport` または本プロジェクト用の命名が含まれていること
- リソース名に `ai-test-design-support` が含まれていること
- 可能な範囲で `Project=ai-test-design-support` タグが付与されていること
- 既存プライベート環境のVPC / EC2 / Security Group / Route 53 が削除対象に含まれていないこと
- AWSアカウントID、VPC ID、EC2 ID、IPアドレスなどをdocsへ記載していないこと

---

## DynamoDB削除時の注意

Backend Serverless構成では、生成履歴をDynamoDBへ保存する想定である。

DynamoDBテーブルを削除すると、保存済みの生成履歴は削除される。

削除前に以下を確認する。

- [ ] 削除対象テーブルが本プロジェクト用である
- [ ] テーブル名に `ai-test-design-support` が含まれている
- [ ] 保存済み履歴が消えて問題ない
- [ ] 必要な検証結果や画面キャプチャは別途保存済みである
- [ ] 実案件情報・顧客情報・業務機密を保存していない

想定テーブル名：

```text
ai-test-design-support-histories
```

---

## CloudWatch Logs削除時の注意

Lambdaを作成すると、CloudWatch Logsにロググループが作成される。

初期方針では、ログ保持期間を7日に設定する。

削除時は以下を確認する。

- [ ] Lambda用ロググループが本プロジェクト用である
- [ ] ログ保持期間が7日になっている
- [ ] 不要なロググループが残っていない
- [ ] ログに仕様本文、Markdown全文、APIキー、認証情報、AWS識別子、個人情報、顧客情報、業務機密が出力されていない

---

## 削除対象に含めないもの

以下は本プロジェクトのBackend Serverless構成では使用しないため、削除対象に含めない。

- 既存VPC
- 既存EC2
- 既存Security Group
- 既存IAM Role
- 既存Route 53設定
- 既存プライベート環境のリソース
- NAT Gateway
- ALB
- RDS
- ECS Fargate

本プロジェクト用に作成していないリソースを削除対象に含めない。

---

## Backend Stack削除前チェック

Backend Stackを削除する前に、以下を確認する。

- [ ] 削除対象Stack名が本プロジェクト用である
- [ ] API Gatewayが本プロジェクト用である
- [ ] Lambdaが本プロジェクト用である
- [ ] DynamoDBテーブルが本プロジェクト用である
- [ ] CloudWatch Logsロググループが本プロジェクト用である
- [ ] IAM Role / Policyが本プロジェクト用である
- [ ] 既存VPC / EC2 / Security Group / Route 53が対象に含まれていない
- [ ] DynamoDB履歴データが削除されても問題ない
- [ ] `.env`、AWS認証情報、APIキー、DBファイルがGit管理対象に含まれていない
- [ ] README / docsにAWSアカウントID、VPC ID、EC2 ID、IPアドレス、IAM認証情報を記載していない

---

## 削除手順の詳細化タイミング

具体的な削除コマンドは、Backend Stack実装後に確定する。

現時点では、以下を方針として残す。

```text
Backend Stackを作成した場合は、Frontend Stackとは分けて削除できるようにする。
削除手順では、本プロジェクト用Stackと本プロジェクト用リソースのみを対象にする。
DynamoDBテーブル削除による履歴データ消失を明記する。
CloudWatch Logsロググループの保持期間と削除漏れを確認する。
```

## 15. 注意事項

削除コマンドでは、必ずCloudFormation Outputから取得した本プロジェクト用S3 Bucket名を使用します。

手入力で別バケットを指定すると、別用途のS3 Bucketを削除するリスクがあります。

以下はREADME/docs/GitHub Issueへ記載しません。

- AWSアカウントID
- IAM ARN
- 実S3 Bucket名
- CloudFront Distribution ID
- CloudFront DomainName
- VPC ID
- EC2 ID
- IPアドレス

## 16. 実施結果

Issue #23では、以下を確認済みです。

- 対象S3 Bucketの中身を手動削除
- `pnpm cdk destroy` 成功
- 本プロジェクト用S3 + CloudFront構成の削除確認
- 既存VPC / EC2 / Security Group / Route 53を使用・変更していないことの確認

## 17. 次アクション

- READMEへ削除確認済みであることを反映する
- Issue #23 closeコメントへ削除確認結果を記載する
- 後続のBackend AWS化時も、デプロイ手順と削除手順をセットで整備する
