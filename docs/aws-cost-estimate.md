# AWS低コスト構成・料金見積もり

## 1. 目的

このドキュメントは、AIテスト設計支援ツールの Phase 2：AWS低コスト版における、AWS構成候補・料金見積もり前提・コスト制御方針を整理するためのメモです。

Phase 2では、ローカルMVPを本格的な本番運用環境へ移行するのではなく、AWS SAAで学習した内容を個人開発に落とし込み、低コストで説明可能なAWS構成を作ることを目的とします。

このドキュメントでは、AWSリソース作成やデプロイ作業は扱いません。

## 2. 関連Issue

- GitHub Issue: #20 AWS低コスト構成・料金見積もり

## 3. 現在の前提

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

Phase 2では、まず以下を整理します。

- AWS低コスト構成候補
- AWS利用料の概算
- AWS Pricing Calculatorで確認する前提
- AWS Budgets設定方針
- CloudWatch Logs保持期間の方針
- 避けるべき高コストサービス
- 削除手順の方針
- 既存AWS環境との分離方針

## 4. 既存AWS環境との分離前提

本プロジェクトでは、既存のプライベート用VPC/EC2と同一AWSアカウントを使用します。

ただし、既存環境との混同や誤削除を防ぐため、AIテスト設計支援ツール用リソースは以下の方針で分離します。

- 既存プライベートVPCは使用しない
- 既存EC2へ同居デプロイしない
- 既存Security Group、IAM Role、Route 53設定を安易に流用しない
- リソース名には `ai-test-design-support` を含める
- タグ `Project=ai-test-design-support` を付与する
- 初期環境は `Environment=dev` または `Environment=portfolio` とする
- CDKを使う場合はStack名で既存環境と明確に分離する
- 削除手順では、本プロジェクト用リソースのみを削除対象にする

AWSアカウントID、VPC ID、EC2 ID、IPアドレス、IAMアクセスキー等は、README、docs、GitHub Issueには記載しません。

## 5. 想定利用量

個人開発ポートフォリオ用途のため、本格的なSaaS運用や多数ユーザー利用は想定しません。

| 項目 | 想定 |
|---|---|
| 利用目的 | README確認、面談デモ、個人検証 |
| 月間アクセス数 | 100〜1,000程度 |
| 月間APIリクエスト数 | 100〜1,000程度 |
| 履歴データ件数 | 100〜1,000件程度 |
| 保存データ量 | 1GB未満 |
| CloudWatch Logs | 少量 |
| LLM API利用 | Phase 2初期では対象外 |
| リージョン候補 | `ap-northeast-1` |

料金はAWSの最新条件に依存するため、最終的な金額はAWS Pricing Calculatorで確認します。

## 6. 構成候補

### 6.1 候補A：FrontendのみAWS配信

```text
Frontend build
↓
S3
↓
CloudFront
```

#### 対象サービス

- Amazon S3
- Amazon CloudFront

#### 評価

| 観点 | 評価 |
|---|---|
| コスト | 低い |
| 実装難易度 | 低い |
| 既存VPC/EC2との分離 | しやすい |
| 削除手順 | 比較的単純 |
| ポートフォリオ説明価値 | あり |
| Backend AWS化 | まだ行わない |

#### コメント

Phase 2初期の第一歩として最も現実的です。

S3 + CloudFront は既存VPC/EC2に触れずに構成できるため、同一AWSアカウント内でも既存プライベート環境と混同しにくいです。

ただし、Backendは引き続きローカルまたは別フェーズ扱いとなるため、完全なAWS化ではありません。

### 6.2 候補B：Frontend + Serverless Backend

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

#### 対象サービス

- Amazon S3
- Amazon CloudFront
- Amazon API Gateway
- AWS Lambda
- Amazon DynamoDB
- Amazon CloudWatch Logs

#### 評価

| 観点 | 評価 |
|---|---|
| コスト | 低〜中 |
| 実装難易度 | 中 |
| 既存VPC/EC2との分離 | しやすいが設計が必要 |
| 削除手順 | 対象リソースが増える |
| ポートフォリオ説明価値 | 高い |
| Backend AWS化 | 可能 |

#### コメント

常時稼働リソースを避けられるため、個人開発向けのAWS構成として有力です。

ただし、FastAPI構成をLambdaで動かすための調整、API Gatewayとの接続、SQLiteからDynamoDBへの保存方式変更が必要になります。

Phase 2初期で一気に実装すると作業量が大きいため、候補Aの後続として検討します。

### 6.3 候補C：実務寄り構成

```text
CloudFront
↓
ALB
↓
ECS Fargate
↓
RDS PostgreSQL
```

#### 対象サービス

- Amazon CloudFront
- Application Load Balancer
- Amazon ECS Fargate
- Amazon RDS
- Amazon CloudWatch Logs

#### 評価

| 観点 | 評価 |
|---|---|
| コスト | 高くなりやすい |
| 実装難易度 | 高い |
| 既存VPC/EC2との分離 | VPC設計が必要 |
| 削除手順 | 複雑 |
| ポートフォリオ説明価値 | 高い |
| Phase 2初期採用 | しない |

#### コメント

実務寄りの構成としては説明価値があります。

一方で、ALB、ECS Fargate、RDSは個人開発ではコストと運用負荷が高くなりやすいため、Phase 2初期では採用しません。

Phase 3以降で、AWS実務寄り構成を検討する段階になったら再評価します。

## 7. Phase 2初期の推奨構成

Phase 2初期では、以下の順で進めます。

```text
1. AWS低コスト構成・料金見積もり
2. AWS構成docs作成
3. AWS Budgets・コスト制御方針整理
4. S3 + CloudFrontによるFrontend配信
5. 削除手順整備
6. READMEへのAWS構成概要反映
```

初期実装対象は、候補Aの **S3 + CloudFrontによるFrontend配信** とします。

理由は以下です。

- 低コストで始めやすい
- 既存VPC/EC2に触れずに進められる
- 同一AWSアカウント内でもリソース分離しやすい
- 削除対象を限定しやすい
- READMEや面談で説明しやすい
- Backend AWS化より先にAWSデプロイ成功体験を得られる

## 8. AWS Pricing Calculatorで確認する項目

### 8.1 S3

確認項目：

- ストレージ容量
- ストレージクラス
- PUTリクエスト数
- GETリクエスト数
- データ転送量
- 不要ファイル削除方針

初期前提：

| 項目 | 値 |
|---|---|
| ストレージクラス | S3 Standard |
| 保存容量 | 1GB未満 |
| 主な用途 | Frontend build成果物の配置 |
| 備考 | 不要なbuild成果物を残し続けない |

### 8.2 CloudFront

確認項目：

- データ転送量
- リクエスト数
- キャッシュ利用
- 価格クラス
- 無料枠またはFree Tier条件
- S3オリジンとの組み合わせ

初期前提：

| 項目 | 値 |
|---|---|
| 月間アクセス | 100〜1,000程度 |
| データ転送量 | 少量 |
| 用途 | 静的Frontend配信 |
| 備考 | WAFは初期では含めない |

### 8.3 API Gateway

確認項目：

- HTTP API / REST API の違い
- リクエスト数
- 認証有無
- CloudWatch Logs出力有無

初期方針：

| 項目 | 方針 |
|---|---|
| API種別 | 後続でHTTP API優先候補 |
| Phase 2初期 | 見積もり対象として確認のみ |
| 実装 | S3 + CloudFront後に検討 |

### 8.4 Lambda

確認項目：

- 月間リクエスト数
- 実行時間
- メモリサイズ
- タイムアウト
- CloudWatch Logs出力量

初期方針：

| 項目 | 方針 |
|---|---|
| 用途 | Backend API候補 |
| Phase 2初期 | 見積もり対象として確認のみ |
| 実装 | 後続で検討 |

### 8.5 DynamoDB

確認項目：

- オンデマンド / プロビジョンド
- 読み込みリクエスト数
- 書き込みリクエスト数
- ストレージ容量
- GSIの有無
- TTLの利用有無

初期方針：

| 項目 | 方針 |
|---|---|
| 用途 | 履歴保存候補 |
| Phase 2初期 | 見積もり対象として確認のみ |
| 実装 | Backend AWS化時に検討 |

### 8.6 CloudWatch Logs

確認項目：

- ログ取り込み量
- ログ保存量
- ログ保持期間
- 不要ログ削除方針

初期方針：

| 項目 | 方針 |
|---|---|
| 保持期間 | 7日を初期候補 |
| 用途 | Lambda / API Gateway導入後の確認 |
| 備考 | 無期限保持は避ける |

### 8.7 AWS Budgets

確認項目：

- 月額予算
- アラート閾値
- 通知先
- 既存プライベートサーバ費用との見分け方

初期方針：

| 項目 | 方針 |
|---|---|
| Budget種別 | Cost budget |
| 月額予算 | 500円〜1,000円相当を初期候補 |
| アラート | 50%、80%、100% |
| 通知 | メール通知 |
| 備考 | 既存AWS環境の費用と混同しないように確認する |

## 9. 低コスト観点で初期回避するサービス

Phase 2初期では、以下を原則として採用しません。

| サービス / 構成 | 回避理由 |
|---|---|
| NAT Gateway | 常時課金になりやすい |
| ALB | 常時稼働コストが発生しやすい |
| RDS | 個人開発初期では継続課金・削除漏れリスクがある |
| ECS Fargate | 実務寄りだが初期には構成が重い |
| EKS | 個人開発初期として過剰 |
| WAF | 初期デモ用途では優先度が低い |
| EC2常時起動 | 既存プライベートEC2との混同リスクがある |
| Bedrock / OpenAI API無制限利用 | API料金とキー管理が必要 |

## 10. コスト管理方針

Phase 2では、AWSリソース作成前に以下を確認します。

- AWS Pricing Calculatorで見積もり前提を確認する
- AWS Budgetsを設定する
- 既存プライベートサーバ費用と、本プロジェクト追加費用を分けて確認する
- CloudWatch Logs保持期間を短くする
- 不要なS3オブジェクトを残さない
- 削除手順をdocsに明記する
- READMEに料金注意事項を記載する

## 11. 削除手順方針

Phase 2では、デプロイ手順だけでなく削除手順も整備します。

削除手順では、以下を明記します。

- 削除対象は `Project=ai-test-design-support` のリソースに限定する
- 既存VPC/EC2を削除対象に含めない
- S3 Bucketは中身を空にしてから削除する
- CloudFront Distributionは無効化してから削除する
- CDKを使う場合は対象Stack名を確認してから `cdk destroy` を実行する
- CloudWatch LogsのLog Groupが残っていないか確認する
- 削除後にAWS Billing / Cost Explorerで課金状況を確認する

## 12. 現時点の結論

Phase 2初期では、以下の方針を採用します。

```text
AWSアカウントは既存プライベート環境と同一アカウントを使用する。
ただし、本プロジェクト用AWSリソースは命名・タグ・Stack名・削除手順で明確に分離する。

最初のAWS実装対象は、S3 + CloudFrontによるFrontend配信とする。
Backend API、DynamoDB、CloudWatch Logsの本格利用は後続で検討する。
```

## 13. 次アクション

- `docs/aws-architecture.md` に、AWS Pricing Calculator確認結果とPhase 2初期の採用方針を反映する
- `docs/aws-budget.md` を後続で作成する
- `docs/aws-destroy.md` を後続で作成する
- S3 + CloudFrontによるFrontend配信の実装Issueを後続で作成する
- Backend API、DynamoDB、CloudWatch Logsの本格利用は、Frontend配信後に別Issueで検討する

## 14. AWS Pricing Calculator確認結果

### 14.1 見積もり作成日

- 作成日：2026年5月24日
- 見積もり名：`ai-test-design-support-phase2-dev`
- リージョン：`ap-northeast-1`

### 14.2 見積もり1：S3 + CloudFront

Phase 2初期で採用候補とする、Frontend静的配信構成の見積もりです。

```text
Frontend build
↓
S3
↓
CloudFront
↓
Browser
```

| サービス | 月額概算 |
|---|---:|
| S3 | $0.00 USD |
| CloudFront | $0.19 USD |
| 合計 | $0.19 USD |

#### 備考

- 個人開発ポートフォリオ用途の小規模アクセスを前提とする
- 既存プライベート用VPC/EC2には接続しない
- 既存AWS環境と同一アカウント内で、命名・タグ・削除手順により分離する
- AWSリソース作成前に、削除手順とBudgets設定方針を確認する

### 14.3 見積もり2：Serverless Backend比較用

後続でBackend APIをAWS化する場合の比較用見積もりです。

```text
API Gateway HTTP API
↓
Lambda
↓
DynamoDB

Logs
↓
CloudWatch Logs
```

| サービス | 月額概算 |
|---|---:|
| API Gateway | $0.00 USD |
| Lambda | $0.00 USD |
| DynamoDB | $0.00 USD |
| CloudWatch Logs | $0.15 USD |
| 合計 | $0.15 USD |

#### 備考

- Phase 2初期では、Serverless Backendはまだ実装しない
- Backend AWS化は、S3 + CloudFrontによるFrontend配信後に別Issueで検討する
- Lambdaは既存VPCに接続しない前提とする
- SQLiteからDynamoDBへの保存方式変更は後続タスクで検討する
- CloudWatch Logsは保持期間7日を初期候補とする

### 14.4 見積もり結果からの判断

AWS Pricing Calculatorの確認結果では、以下の概算となった。

| 構成 | 月額概算 |
|---|---:|
| S3 + CloudFront | $0.19 USD |
| Serverless Backend比較用 | $0.15 USD |
| 両方を採用した場合の単純合算 | $0.34 USD |

この結果から、Phase 2初期は低コストで開始できる見込みがある。

ただし、実際の料金は以下により変動する。

- アクセス数
- データ転送量
- CloudFrontリクエスト数
- CloudWatch Logs出力量
- AWS無料枠の適用状況
- 既存AWS環境で発生している別用途の費用

そのため、AWSリソースを作成する前に、AWS Budgetsを設定し、既存プライベートサーバ費用と本プロジェクト追加費用を混同しないように管理する。

### 14.5 Phase 2初期の採用方針

Phase 2初期では、以下の構成を最初の実装対象とする。

```text
S3 + CloudFront による Frontend 静的配信
```

理由は以下のとおり。

- 月額概算が低い
- 既存VPC/EC2に触れずに構成できる
- 同一AWSアカウント内でも分離しやすい
- 削除対象を限定しやすい
- READMEや面談で説明しやすい
- Backend AWS化より前に、AWSデプロイと削除手順を小さく確認できる

Backend API、DynamoDB、CloudWatch Logsの本格利用は、Frontend配信後に別Issueで検討する。
