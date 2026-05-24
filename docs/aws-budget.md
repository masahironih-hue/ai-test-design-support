# AWS Budgets・コスト制御方針

## 1. 目的

このドキュメントは、AIテスト設計支援ツールの Phase 2：AWS低コスト版における、AWS Budgets設定方針、コスト監視方針、CloudWatch Logs保持期間、削除漏れ防止方針を整理するためのものです。

Phase 2では、AWSリソースを本格的に作成する前に、個人開発として許容できる範囲にAWS利用料を抑えることを重視します。

このドキュメントでは、AWSリソース作成やデプロイ作業は扱いません。

## 2. 関連Issue

- GitHub Issue: #21 AWS Budgets・コスト制御設定

## 3. 前提

Issue #20 で、AWS低コスト構成・料金見積もりを整理しました。

Phase 2初期では、以下の構成を最初のAWS実装対象とします。

```text
S3 + CloudFront による Frontend 静的配信
```

AWS Pricing Calculatorで確認した小規模利用前提の概算は以下です。

| 構成 | 月額概算 |
|---|---:|
| S3 + CloudFront | $0.19 USD |
| Serverless Backend比較用 | $0.15 USD |
| 両方を採用した場合の単純合算 | $0.34 USD |

ただし、実際の料金はアクセス数、データ転送量、CloudFrontリクエスト数、CloudWatch Logs出力量、AWS無料枠の適用状況、既存AWS環境で発生している別用途の費用によって変動します。

## 4. 既存AWS環境との分離方針

本プロジェクトでは、既存のプライベート用VPC/EC2と同一AWSアカウントを使用します。

ただし、既存環境との混同や誤削除を防ぐため、AIテスト設計支援ツール用リソースは以下の方針で分離します。

- 既存プライベートVPCは使用しない
- 既存EC2へ同居デプロイしない
- 既存Security Group、IAM Role、Route 53設定を安易に流用しない
- リソース名には `ai-test-design-support` を含める
- タグ `Project=ai-test-design-support` を付与する
- 初期環境は `Environment=dev` または `Environment=portfolio` とする
- 削除手順では、本プロジェクト用リソースのみを削除対象にする

AWSアカウントID、VPC ID、EC2 ID、IPアドレス、IAMアクセスキー等は、README、docs、GitHub Issueには記載しません。

## 5. AWS Budgets設定方針

### 5.1 Budget種別

初期は、以下を設定候補とします。

| 項目 | 方針 |
|---|---|
| Budget type | Cost budget |
| Period | Monthly |
| Budget method | Fixed |
| Budget amount | 1 USD または 1,000円相当 |
| Scope | 初期はアカウント全体。可能であればタグ `Project=ai-test-design-support` で絞る |
| Notification | メール通知 |
| Budget actions | 初期は使用しない |

初期の見積もりは非常に小さいため、予算額は `1 USD` または `1,000円相当` を候補にします。

既存プライベート用VPC/EC2と同一AWSアカウントを使うため、**アカウント全体のBudgetだけでは既存サーバ費用も含まれる**点に注意します。

### 5.2 アラート閾値

初期設定候補は以下です。

| アラート | 種別 | 閾値 |
|---|---|---:|
| Alert 1 | Actual cost | 50% |
| Alert 2 | Actual cost | 80% |
| Alert 3 | Actual cost | 100% |
| Alert 4 | Forecasted cost | 100% |

Forecasted cost は、月末までに予算超過しそうな場合の検知に使います。

## 6. Budgetスコープの考え方

### 6.1 初期方針

既存プライベート用VPC/EC2と同一AWSアカウントを使うため、Budgetsは以下の2段階で考えます。

| 種別 | 目的 |
|---|---|
| アカウント全体Budget | 想定外の総額増加を検知する |
| 本プロジェクト用Budget | `Project=ai-test-design-support` タグを使い、本プロジェクト分の増加を追跡する |

ただし、S3やCloudFrontなどタグによるコスト配賦・反映には制約や反映遅延があり得るため、初期はアカウント全体Budgetを主、Cost Explorerでのサービス別確認を補助として使います。

### 6.2 同一アカウント利用時の注意

同一アカウント内で管理するため、以下を確認します。

- 既存プライベートサーバ由来の費用と、本プロジェクト追加費用を混同しない
- S3 / CloudFront / CloudWatch Logs など、Phase 2で追加したサービスの増加分を見る
- `Project=ai-test-design-support` タグを付けられるリソースには必ず付与する
- Cost Explorerでは、サービス別、タグ別、期間別に確認する
- 予算超過時に、既存サーバ費用が原因か、本プロジェクト費用が原因かを切り分ける

## 7. CloudWatch Logs保持期間方針

Phase 2初期の S3 + CloudFront 配信では、CloudWatch Logsの利用は限定的です。

Backendを API Gateway + Lambda へ展開する場合は、CloudWatch Logsが発生します。

初期方針は以下です。

| 項目 | 方針 |
|---|---|
| Retention | 7日 |
| 無期限保持 | 避ける |
| ログ内容 | エラー調査に必要な最小限 |
| 機密情報 | 出力しない |
| 削除確認 | Log Groupが残っていないか確認する |

CloudWatch Logsは、デフォルトではログを無期限保持するため、ロググループごとに保持期間を設定します。AWS公式ドキュメントでも、CloudWatch Logsの保持期間は無期限保持から指定期間へ変更できると説明されています。保持期間を過ぎたログイベントは即時削除ではなく、通常最大72時間程度かかる点にも注意します。

## 8. 削除漏れ防止方針

AWSリソースを作成した場合、削除手順では以下を確認します。

| 対象 | 確認内容 |
|---|---|
| S3 | Bucket内のオブジェクトを削除してからBucketを削除する |
| CloudFront | DistributionをDisableしてからDeleteする |
| CloudWatch Logs | Log Groupが残っていないか確認する |
| API Gateway | 後続で作成した場合はAPIを削除する |
| Lambda | 後続で作成した場合はFunctionと関連Roleを確認する |
| DynamoDB | 後続で作成した場合はTableを削除する |
| IAM Role / Policy | CDKまたは手動作成したものだけを確認する |
| CDK Stack | 対象Stack名が本プロジェクト用であることを確認してから削除する |

削除対象は、以下に該当する本プロジェクト用リソースに限定します。

```text
Project=ai-test-design-support
```

または

```text
ai-test-design-support
```

をリソース名に含むもの。

既存プライベート用VPC/EC2、既存Security Group、既存IAM Role、既存Route 53設定は削除対象に含めません。

## 9. コスト確認タイミング

Phase 2では、以下のタイミングでコストを確認します。

| タイミング | 確認内容 |
|---|---|
| AWSリソース作成前 | Budgets設定、想定料金、削除手順 |
| S3 + CloudFront作成後 | S3、CloudFrontの増加有無 |
| 動作確認後 | CloudFrontリクエスト数、データ転送量 |
| 削除後 | S3、CloudFront、CloudWatch Logs等が残っていないか |
| 翌日以降 | Billing / Cost Explorerで課金増加がないか |
| 月末前 | Budgetアラート、Forecasted costを確認 |

Cost Explorerは、AWSのコストと使用量を表示・分析するためのツールです。必要に応じて、サービス別・タグ別・期間別に確認します。

## 10. README / docs へ残す内容

READMEには詳細設定手順を長く書かず、以下を要約して記載します。

- AWS利用料は個人負担であること
- Phase 2では事前にAWS Pricing Calculatorで見積もったこと
- AWS Budgetsで予算アラートを設定する方針であること
- 既存プライベート用VPC/EC2と同一アカウント内で明確に分離すること
- 削除手順を `docs/aws-destroy.md` に記載すること

詳細は以下のdocsへ分離します。

- `docs/aws-cost-estimate.md`
- `docs/aws-budget.md`
- `docs/aws-destroy.md`
- `docs/aws-architecture.md`

## 11. 現時点の結論

Phase 2では、AWSリソース作成前に以下を確認する。

```text
1. AWS Pricing Calculatorで料金見積もりを確認済みであること
2. AWS Budgetsで月額予算アラートを設定すること
3. 既存プライベート用VPC/EC2と本プロジェクト用リソースを混同しないこと
4. CloudWatch Logsは7日保持を初期方針とすること
5. 削除手順では本プロジェクト用リソースのみを対象にすること
```

Phase 2初期の最初の実装対象は、引き続き以下とする。

```text
S3 + CloudFront による Frontend 静的配信
```

## 12. 次アクション

- AWS Budgetsの具体的な設定値を確定する
- AWSコンソール上でBudgetを作成する手順を確認する
- `docs/aws-destroy.md` の初版を後続で作成する
- `docs/aws-deploy.md` の初版を後続で作成する
- S3 + CloudFront配信Issueへ進む
