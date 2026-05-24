# AWS削除手順

## 1. 目的

このドキュメントは、AIテスト設計支援ツールの Phase 2：AWS低コスト版で作成するAWSリソースの削除手順を整理するためのものです。

Phase 2では、既存のプライベート用VPC/EC2と同一AWSアカウントを使用します。

そのため、削除手順では、本プロジェクト用リソースのみを削除対象とし、既存プライベート用VPC/EC2を誤って変更・削除しないことを最優先とします。

## 2. 関連Issue

- GitHub Issue: #22 AWSデプロイ・削除手順

## 3. 前提

Phase 2初期では、以下の構成を最初のAWS実装対象とします。

```text
S3 + CloudFront による Frontend 静的配信
```

本ドキュメントでは、まず以下の削除手順を対象とします。

- S3 Bucket
- S3 Object
- CloudFront Distribution
- CloudFront Origin Access Control
- CloudWatch Logs
- CDK Stack
- IAM Role / Policy

API Gateway、Lambda、DynamoDBは、Phase 2後続で作成した場合に削除対象へ追加します。

## 4. 重要な分離方針

本プロジェクトでは、既存のプライベート用VPC/EC2と同一AWSアカウントを使用します。

ただし、既存環境との混同や誤削除を防ぐため、AIテスト設計支援ツール用リソースは以下の方針で分離します。

- 既存プライベートVPCは使用しない
- 既存EC2へ同居デプロイしない
- 既存Security Groupを流用しない
- 既存IAM Roleを安易に流用しない
- 既存Route 53設定を安易に変更しない
- リソース名には `ai-test-design-support` を含める
- タグ `Project=ai-test-design-support` を付与する
- 削除手順では、本プロジェクト用リソースのみを削除対象にする

AWSアカウントID、VPC ID、EC2 ID、IPアドレス、IAMアクセスキー等は、このドキュメントには記載しません。

## 5. 削除対象の判定基準

削除対象は、以下のいずれかに該当する本プロジェクト用リソースに限定します。

```text
リソース名に ai-test-design-support を含む
```

または

```text
タグ Project=ai-test-design-support が付与されている
```

または

```text
CDK Stack名が本プロジェクト用である
```

以下は削除対象に含めません。

- 既存プライベート用VPC
- 既存プライベート用EC2
- 既存Security Group
- 既存IAM Role
- 既存Route 53 Hosted Zone
- 既存Elastic IP
- 既存Key Pair
- 本プロジェクトと無関係なS3 Bucket
- 本プロジェクトと無関係なCloudFront Distribution

## 6. 削除前チェック

削除作業前に、以下を確認します。

```text
- 作業対象AWSアカウントが想定どおりである
- 作業リージョンが想定どおりである
- 削除対象リソース名に ai-test-design-support が含まれている
- 削除対象リソースに Project=ai-test-design-support タグがある
- 既存VPC/EC2が削除対象に含まれていない
- S3 Bucket名が本プロジェクト用である
- CloudFront DistributionのOriginが本プロジェクト用S3 Bucketである
- CDK Stack名が本プロジェクト用である
```

## 7. 削除順序

Phase 2初期のS3 + CloudFront構成では、以下の順で削除します。

```text
1. CloudFront DistributionをDisableする
2. CloudFront DistributionがDisabledになるまで待つ
3. CloudFront DistributionをDeleteする
4. CloudFront Origin Access Controlを削除する
5. S3 Bucket内のObjectを削除する
6. S3 Bucketを削除する
7. CloudWatch Logsが残っていないか確認する
8. CDK Stackが残っていないか確認する
9. Billing / Cost Explorerで課金状況を確認する
```

CDKで構築している場合は、原則として本プロジェクト用Stackを対象に `cdk destroy` を使用します。

ただし、`cdk destroy` 実行前に、対象Stack名と削除対象リソースを必ず確認します。

## 8. CloudFront Distribution削除手順

### 8.1 対象確認

CloudFront Distributionを削除する前に、以下を確認します。

```text
- DistributionのCommentまたはTagが本プロジェクト用である
- Originが本プロジェクト用S3 Bucketである
- 既存プライベート用サーバや既存ドメイン向けのDistributionではない
```

### 8.2 Disable

CloudFront Distributionは、削除前にDisableします。

```text
CloudFront
↓
Distributions
↓
対象Distributionを選択
↓
Disable
```

Disable後、Distributionの状態が反映されるまで待ちます。

### 8.3 Delete

DistributionがDisabledになったら、対象を再確認してDeleteします。

削除後は復元できないため、以下を再確認します。

```text
- Distribution IDが本プロジェクト用である
- Originが本プロジェクト用S3 Bucketである
- 既存プライベート環境向けDistributionではない
```

## 9. S3 Bucket削除手順

### 9.1 対象確認

S3 Bucketを削除する前に、以下を確認します。

```text
- Bucket名に ai-test-design-support が含まれている
- 本プロジェクト用Frontend build成果物の配置先である
- 既存プライベート用途のBucketではない
- 重要なバックアップデータを含んでいない
```

### 9.2 Object削除

S3 Bucketは、中身が残っていると削除できません。

そのため、先にBucket内のObjectを削除します。

```text
S3
↓
Buckets
↓
対象Bucketを選択
↓
Objects
↓
全Objectを削除
```

### 9.3 Bucket削除

Object削除後、Bucketを削除します。

```text
S3
↓
Buckets
↓
対象Bucketを選択
↓
Delete
```

削除時は、Bucket名を再確認します。

## 10. CloudWatch Logs確認

Phase 2初期のS3 + CloudFront構成では、CloudWatch Logsの利用は限定的です。

ただし、後続でAPI Gateway / Lambdaを追加した場合、CloudWatch LogsのLog Groupが作成される可能性があります。

確認対象例：

```text
/aws/lambda/ai-test-design-support-*
API-Gateway-Execution-Logs_*
```

CloudWatch Logsを使う場合、保持期間は7日を初期方針とします。

削除時は、以下を確認します。

```text
- 本プロジェクト用Log Groupが残っていないか
- 保持期間が無期限になっていないか
- 不要なLog Groupが残っていないか
```

## 11. IAM Role / Policy確認

CDKやAWSサービスによってIAM Role / Policyが作成された場合、以下を確認します。

```text
- Role名に ai-test-design-support が含まれている
- CDK Stackによって作成されたRoleである
- 既存プライベート環境で使っているRoleではない
```

既存IAM Roleを削除対象に含めません。

## 12. CDK Stack削除手順

CDKを使う場合、削除前にStack名を確認します。

```powershell
cdk list
```

対象Stackが本プロジェクト用であることを確認してから削除します。

```powershell
cdk destroy <本プロジェクト用Stack名>
```

削除前に確認すること：

```text
- Stack名が本プロジェクト用である
- 削除対象リソースが本プロジェクト用である
- 既存VPC/EC2が削除対象に含まれていない
```

## 13. 削除後チェック

削除後、以下を確認します。

```text
- 本プロジェクト用CloudFront Distributionが残っていない
- 本プロジェクト用S3 Bucketが残っていない
- 本プロジェクト用CloudWatch Logsが残っていない
- 本プロジェクト用CDK Stackが残っていない
- 既存プライベート用VPC/EC2に変更がない
- Billing / Cost Explorerで想定外の課金が増えていない
```

## 14. 削除対象外リスト

以下は削除対象外です。

| 対象 | 理由 |
|---|---|
| 既存プライベート用VPC | 本プロジェクトでは使用しない |
| 既存プライベート用EC2 | 本プロジェクトでは同居デプロイしない |
| 既存Security Group | 既存サーバ運用に影響する可能性がある |
| 既存IAM Role | 権限管理の混同を避ける |
| 既存Route 53設定 | 既存サービス影響を避ける |
| 既存Elastic IP | 既存サーバ影響を避ける |
| 既存Key Pair | 本プロジェクトでは使用しない |

## 15. READMEへ反映する内容

READMEには、詳細手順ではなく以下を要約して記載します。

```text
AWSリソースを作成する場合は、デプロイ手順だけでなく削除手順もdocsに記載します。
既存プライベート用VPC/EC2と同一AWSアカウントを使用しますが、本プロジェクト用リソースは命名・タグ・Stack名で分離し、削除手順では本プロジェクト用リソースのみを対象にします。
```

## 16. 現時点の結論

Phase 2初期では、AWSリソース作成前に削除手順を明確化します。

最初のAWS実装対象は以下です。

```text
S3 + CloudFront による Frontend 静的配信
```

ただし、実装前に以下を満たす必要があります。

```text
- 削除対象が本プロジェクト用リソースに限定されている
- 既存VPC/EC2を削除対象に含めない
- CloudFront Distribution削除手順が明確である
- S3 Bucket削除手順が明確である
- 削除後の課金確認手順がある
```

## 17. 次アクション

- `docs/aws-deploy.md` の初版を作成する
- `docs/aws-destroy.md` と `docs/aws-deploy.md` の整合を確認する
- 後続Issue `[AWS] S3 CloudFront Frontend配信` に進む
