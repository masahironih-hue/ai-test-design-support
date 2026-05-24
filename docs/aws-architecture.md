# AWS構成方針

## 1. 目的

このドキュメントは、AIテスト設計支援ツールの Phase 2：AWS低コスト版におけるAWS構成方針を整理するためのものです。

Phase 2では、本格的な本番運用や大規模SaaS構成を目指すのではなく、AWS SAAで学習した内容を個人開発に適用し、低コストで説明可能なAWS構成を作ることを目的とします。

## 2. 関連Issue

- GitHub Issue: #20 AWS低コスト構成・料金見積もり

## 3. 全体方針

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

## 4. 既存AWS環境との分離方針

本プロジェクトでは、既存のプライベート用VPC/EC2と同一AWSアカウントを使用します。

ただし、既存環境との混同や誤削除を防ぐため、AIテスト設計支援ツール用リソースは以下の方針で分離します。

### 4.1 分離方針

- 既存プライベートVPCは使用しない
- 既存EC2へ同居デプロイしない
- 既存Security Groupを流用しない
- 既存IAM Roleを安易に流用しない
- 既存Route 53設定を安易に変更しない
- 既存プライベートサーバの運用設定に影響を与えない
- 削除手順では、本プロジェクト用リソースのみを対象にする

### 4.2 命名方針

本プロジェクト用リソースには、原則として以下のprefixを含めます。

```text
ai-test-design-support
```

例：

```text
ai-test-design-support-frontend-dev
ai-test-design-support-cloudfront-dev
ai-test-design-support-api-dev
ai-test-design-support-history-dev
```

### 4.3 タグ方針

本プロジェクト用AWSリソースには、可能な範囲で以下のタグを付与します。

| Key | Value例 | 用途 |
|---|---|---|
| Project | `ai-test-design-support` | 本プロジェクト用リソース識別 |
| Environment | `dev` | 環境識別 |
| Purpose | `portfolio` | ポートフォリオ用途であることを明示 |
| ManagedBy | `cdk` | CDK管理対象であることを明示 |

### 4.4 削除時の注意

削除時は、以下を確認します。

- 削除対象のリソース名に `ai-test-design-support` が含まれているか
- タグ `Project=ai-test-design-support` が付いているか
- CDK Stack名が本プロジェクト用か
- 既存VPC/EC2/Security Groupが削除対象に含まれていないか
- CloudFront、S3、CloudWatch Logsなどの削除漏れがないか

## 5. Phase 2初期構成

Phase 2初期では、以下の構成を採用候補とします。

```text
Frontend build
↓
S3
↓
CloudFront
↓
Browser
```

### 5.1 構成概要

| 要素 | サービス | 用途 |
|---|---|---|
| Frontend build成果物 | Next.js / React / TypeScript | 静的ファイル生成 |
| 静的ファイル配置 | S3 | build成果物の配置 |
| コンテンツ配信 | CloudFront | HTTPS配信、キャッシュ |
| Backend API | ローカルまたは後続AWS化 | Phase 2初期では対象外 |
| 履歴保存DB | SQLiteまたは後続DynamoDB | Phase 2初期では対象外 |

### 5.2 採用理由

- 低コストで始めやすい
- AWSリソース数を抑えられる
- 既存VPC/EC2に触れずに構成できる
- 同一AWSアカウント内でも分離しやすい
- 削除手順を整理しやすい
- READMEでAWS構成を説明しやすい
- 面談で「AWS SAA学習内容を個人開発に適用した」と説明しやすい

### 5.3 注意点

- BackendはまだAWS化されない
- API接続を含む完全なAWS構成ではない
- ローカルMVPとの差分をREADMEで明確に説明する
- 未実装機能を実装済みのように書かない

## 6. 後続構成候補

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

### 6.1 追加候補サービス

| サービス | 用途 | 検討タイミング |
|---|---|---|
| API Gateway | Backend API公開 | Frontend配信後 |
| Lambda | Backend API実行 | FastAPIのLambda対応検討後 |
| DynamoDB | 履歴保存 | SQLiteからの移行方針整理後 |
| CloudWatch Logs | APIログ確認 | Lambda導入時 |
| AWS Budgets | コスト監視 | AWSリソース作成前 |

### 6.2 Serverless構成の利点

- 常時稼働リソースを避けやすい
- 小規模利用では低コストにしやすい
- 個人開発ポートフォリオとして説明しやすい
- AWS SAAで学んだAPI Gateway、Lambda、DynamoDBを個人開発に適用できる

### 6.3 Serverless構成の注意点

- FastAPIをLambdaで動かすための構成調整が必要
- SQLiteからDynamoDBへ保存方式を変える必要がある
- ログ出力・エラーハンドリング・削除手順が増える
- CloudWatch Logsの保持期間を明示する必要がある
- 料金見積もりとBudgets設定が必要

## 7. Phase 2初期では採用しない構成

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

### 7.1 採用しない理由

| サービス / 構成 | 理由 |
|---|---|
| ALB | 常時稼働コストが発生しやすい |
| ECS Fargate | 実務寄りだが初期には構成が重い |
| RDS | 継続課金・削除漏れリスクがある |
| NAT Gateway | 高コスト化しやすい |
| EKS | 個人開発初期として過剰 |
| WAF | 初期デモ用途では優先度が低い |
| EC2常時起動 | 既存プライベートEC2との混同リスクがある |

### 7.2 後続で再検討する条件

以下の条件を満たした場合、Phase 3以降で再検討します。

- S3 + CloudFront配信が完了している
- Serverless Backend構成を検討済みである
- 削除手順と料金見積もりを明確にできる
- AWS実務寄り構成として説明する価値がある
- 個人負担として許容できる月額コストである

## 8. セキュリティ方針

AWS構成検討・docs作成・README反映では、以下を守ります。

- AWSアカウントIDを記載しない
- VPC ID、Subnet ID、EC2 IDを記載しない
- Public IP、Elastic IPを記載しない
- IAMアクセスキー、シークレットアクセスキーを記載しない
- 実際の顧客情報、個人情報、業務機密を使わない
- APIキーやパスワードをGitHubに載せない
- `.env`、`.env.local`、認証情報ファイルをGit管理対象にしない
- 画面キャプチャにAWSアカウント情報やリソースIDが映らないようにする

## 9. コスト方針

Phase 2では、以下の方針でコストを抑えます。

- AWS Pricing Calculatorで事前に概算する
- AWS Budgetsで予算アラートを設定する
- Free Tier対象サービスを優先する
- 常時稼働リソースを避ける
- 不要なS3オブジェクトを削除する
- CloudWatch Logs保持期間を短くする
- デプロイ後に削除手順を確認する
- 既存プライベートサーバ費用と本プロジェクト費用を混同しない

## 10. CloudWatch Logs方針

Phase 2初期のS3 + CloudFront配信では、CloudWatch Logsの利用は限定的です。

BackendをAPI Gateway + Lambdaへ移行する場合は、以下の方針を採用します。

| 項目 | 方針 |
|---|---|
| ログ保持期間 | 7日を初期候補 |
| ログ内容 | エラー調査に必要な最小限 |
| 機密情報 | 出力しない |
| 削除手順 | Log Group削除または保持期間設定を確認 |

## 11. AWS Budgets方針

AWSリソース作成前に、AWS Budgetsの設定を検討します。

初期候補は以下です。

| 項目 | 方針 |
|---|---|
| Budget種別 | Cost budget |
| 月額予算 | 500円〜1,000円相当 |
| アラート | 50%、80%、100% |
| 通知 | メール通知 |
| 補足 | 既存プライベートサーバ費用と混同しないように確認する |

## 12. READMEへの反映方針

READMEには、AWS構成の詳細をすべて書くのではなく、以下を要約して記載します。

- AWS化の目的
- 現時点でAWS化済みの範囲
- S3 + CloudFrontによるFrontend配信方針
- Backend AWS化は後続検討であること
- 料金見積もりdocsへのリンク
- デプロイ手順docsへのリンク
- 削除手順docsへのリンク
- 本格運用ではなく学習・ポートフォリオ目的であること

## 13. 面談・ポートフォリオでの説明方針

AWS実務経験を過度に盛らず、以下のように説明します。

```text
AWS SAAで学習した内容をもとに、個人開発のローカルMVPを低コストなAWS構成へ段階的に展開しています。
初期段階では、S3 + CloudFrontによる静的Frontend配信から始め、料金見積もり、Budgets、削除手順、既存AWS環境との分離を含めて整理しています。
```

以下のような表現は避けます。

- AWS本番運用経験があります
- ECS / RDS / ALBで本番運用しています
- 実務でAWSアーキテクチャを設計しました
- BedrockやOpenAI APIを本格運用しています

未実装の内容は、未実装または後続検討として明確にします。

## 14. 現時点の結論

Phase 2初期のAWS構成は、以下を採用候補とします。

```text
S3 + CloudFront による Frontend 静的配信
```

Backend API、DynamoDB、CloudWatch Logsの本格利用は、Frontend配信後に別Issueで検討します。

また、既存プライベート用VPC/EC2と同一AWSアカウントを使用するため、命名規則、タグ、Stack名、削除対象確認によって、本プロジェクト用リソースを明確に分離します。

## 15. 次アクション

- `docs/aws-cost-estimate.md` と整合しているか確認する
- AWS Pricing Calculatorで見積もり前提を確認する
- AWS Budgets設定方針を `docs/aws-budget.md` に分離する
- S3 + CloudFront配信の実装Issueを作成する
- AWS削除手順を `docs/aws-destroy.md` として作成する

## AWS Pricing Calculator確認結果との対応

AWS Pricing Calculatorで確認した結果、Phase 2初期候補である S3 + CloudFront 構成は、以下の概算となった。

| 構成 | 月額概算 |
|---|---:|
| S3 + CloudFront | $0.19 USD |
| Serverless Backend比較用 | $0.15 USD |
| 両方を採用した場合の単純合算 | $0.34 USD |

この結果から、Phase 2初期では、まず S3 + CloudFront によるFrontend静的配信を採用候補とする。

Serverless Backend構成も低コストで実現できる可能性はあるが、FastAPIのLambda対応、SQLiteからDynamoDBへの保存方式変更、CloudWatch Logs設計、削除手順整理が必要になるため、Frontend配信後の後続Issueで検討する。