# AWS低コスト構成・料金見積もり

## 1. 目的

このドキュメントは、AIテスト設計支援ツールの Phase 2：AWS低コスト版におけるAWS利用料の概算、低コスト構成候補、コスト制御方針を整理するためのものです。

AWS利用料は個人負担であるため、最初から高コスト構成にせず、低コスト・削除容易性・説明しやすさを優先します。

## 2. 関連Issue

- GitHub Issue: #20 AWS低コスト構成・料金見積もり
- GitHub Issue: #21 AWS Budgets・コスト制御設定
- GitHub Issue: #22 AWSデプロイ・削除手順
- GitHub Issue: #23 S3 CloudFront Frontend配信

## 3. 現在の前提

Phase 0：進め方・環境構築は完了済みです。  
Phase 1：ローカルMVPも完了済みです。

Phase 1では、以下を実装済みです。

- FastAPI Backend
- LLM Mock API
- SQLite履歴保存
- Next.js / React / TypeScript Frontend
- 仕様入力フォーム
- 生成結果表示
- Markdownコピー
- 履歴一覧
- 履歴詳細
- README / docs整備
- 画面キャプチャ作成

Phase 2では、まずAWS低コスト版としてS3 + CloudFrontによるFrontend静的配信を検証しました。

## 4. 既存AWS環境との分離前提

本プロジェクトでは、既存のプライベート用VPC/EC2と同一AWSアカウントを使用します。

ただし、本プロジェクト用リソースは以下の方針で分離します。

- 既存VPCを使用しない
- 既存EC2を使用しない
- 既存Security Groupを使用しない
- 既存IAM Roleを安易に流用しない
- 既存Route 53設定を変更しない
- 本プロジェクト用リソースには `ai-test-design-support` を含む命名を行う
- 可能な範囲で `Project=ai-test-design-support` タグを付与する
- 削除対象は本プロジェクト用リソースのみに限定する
- AWSアカウントID、VPC ID、EC2 ID、IPアドレス、IAM情報はREADME/docsへ記載しない

## 5. 想定利用量

個人開発ポートフォリオとして、以下の低トラフィック前提で見積もります。

| 項目 | 前提 |
|---|---|
| 利用者 | 主に本人、面談・ポートフォリオ閲覧者 |
| アクセス数 | 少量 |
| データ転送量 | 少量 |
| 保存データ | サンプル仕様・生成結果中心 |
| 可用性要件 | 本番SaaSほど高くしない |
| コスト優先度 | 高い |

## 6. AWS Pricing Calculator確認結果

### 6.1 見積もり作成日

```text
2026-05-24 JST
```

### 6.2 見積もり1：S3 + CloudFront

| 項目 | 内容 |
|---|---|
| 想定用途 | Frontend静的配信 |
| 主なサービス | S3、CloudFront |
| 月額概算 | `$0.19 USD` |
| 採用判断 | Phase 2初期構成として採用 |

備考：

- 低アクセスの個人開発ポートフォリオ前提
- 実際の料金はアクセス数、データ転送量、S3保存容量、リクエスト数により変動する
- CloudFrontキャッシュ削除リクエストの使い方にも注意する

### 6.3 見積もり2：Serverless Backend比較用

| 項目 | 内容 |
|---|---|
| 想定用途 | Backend API / 履歴保存の後続AWS化比較 |
| 主なサービス | API Gateway、Lambda、DynamoDB、CloudWatch Logs |
| 月額概算 | `$0.15 USD` |
| 採用判断 | 後続検討 |

備考：

- FastAPIのLambda対応、SQLiteからDynamoDBへの保存方式変更が必要
- CloudWatch Logs設計、ログ保持期間、削除手順の整理が必要
- Phase 2初期ではFrontend静的配信を優先する

### 6.4 単純合算

| 構成 | 月額概算 |
|---|---:|
| S3 + CloudFront | $0.19 USD |
| Serverless Backend比較用 | $0.15 USD |
| 両方を採用した場合の単純合算 | $0.34 USD |

この結果から、Phase 2初期では、まず S3 + CloudFront によるFrontend静的配信を採用します。

## 7. Issue #23 実施結果との対応

Issue #23では、以下を実際に確認しました。

- AWS CDK TypeScript構成を作成
- S3 Bucketを作成
- S3 BucketをPublic公開しない構成を確認
- CloudFront Distributionを作成
- CloudFront OACでS3へアクセスする構成を確認
- Frontend静的ファイルをS3へ配置
- CloudFront URLでFrontend画面表示を確認
- 対象S3 Bucketの中身を手動削除
- `pnpm cdk destroy` により本プロジェクト用リソース削除を確認

検証後にリソースを削除しているため、継続的なS3 + CloudFront利用料は抑えられます。

## 8. 低コスト観点で初期回避するサービス

以下はPhase 2初期では原則として避けます。

| サービス / 構成 | 回避理由 |
|---|---|
| NAT Gateway | 高コスト化しやすい |
| ALB | 常時稼働コストが発生しやすい |
| RDS | 継続課金、削除漏れリスクがある |
| ECS Fargate | 初期構成としては重い |
| EKS | 個人開発初期には過剰 |
| WAF | 初期デモ用途では優先度が低い |
| EC2常時起動 | 既存プライベートEC2との混同リスクがある |
| Bedrock無制限利用 | 利用料の上振れリスクがある |

## 9. コスト管理方針

Phase 2では、以下を実施します。

- AWS Pricing Calculatorで事前に概算する
- AWS Budgetsで予算アラートを設定する
- Free Tier対象サービスを優先する
- 常時稼働リソースを避ける
- 検証後に不要リソースを削除する
- S3 Bucketの不要オブジェクトを削除する
- CloudWatch Logsを使う場合は保持期間を短くする
- BedrockやOpenAI APIの呼び出し回数を制限する
- README/docsにデプロイ手順だけでなく削除手順も明記する

## 10. CDK bootstrapの扱い

`cdk bootstrap` により作成される `CDKToolkit` Stackは、CDK管理用リソースです。  
アプリケーション本体の `AiTestDesignSupportFrontendStack` とは別に扱います。

`CDKToolkit` には、CDK assets用S3 Bucket、IAM Role、SSM Parameterなどが含まれます。  
これはアプリケーション本体のS3 + CloudFront構成とは別の前提リソースであり、削除対象や運用方針を混同しないようにします。

## 11. 削除手順方針

Issue #23では、以下の削除方針を採用しました。

```text
autoDeleteObjects: false
cdk destroy 前に対象S3 Bucketの中身を手動削除
```

理由は以下です。

- 初期構成を小さく保つため
- `autoDeleteObjects: true` 由来のLambda / IAM / Custom Resourceを増やさないため
- 削除対象を明示的に確認できるため
- 既存AWS環境との誤削除を避けるため

削除対象Bucket名は、CloudFormation Output `FrontendBucketName` から取得します。  
手入力で別Bucketを指定しないよう注意します。

## 12. 現時点の結論

Phase 2初期では、S3 + CloudFront によるFrontend静的配信を採用し、構築・表示確認・削除確認まで完了しました。

Backend AWS化、DynamoDB、CloudWatch Logs本格利用は後続Issueで検討します。

AWS実務経験を過度に盛らず、以下のように説明します。

```text
AWS SAAで学習した内容をもとに、個人開発のローカルMVPを低コストなAWS構成へ段階的に展開しています。
S3 + CloudFrontによる静的Frontend配信をCDKで構築し、料金見積もり、Budgets、削除手順、既存AWS環境との分離を含めて確認しました。
Backend APIのAWS化は後続検討です。
```

## 13. 次アクション

- READMEへS3 + CloudFront検証結果を反映する
- `docs/aws-architecture.md` と整合しているか確認する
- `docs/aws-deploy.md` と整合しているか確認する
- `docs/aws-destroy.md` と整合しているか確認する
- Issue #23 closeコメントを作成する
## Backend Serverless構成の料金再確認観点

Phase 2のBackend Serverless構成では、以下のサービスを候補とする。

```text
API Gateway HTTP API
Lambda
DynamoDB
CloudWatch Logs
```

現時点の料金見積もりでは、Frontend配信とServerless Backend比較用を単純合算した場合、低頻度利用であれば月額は小さく収まる想定である。

```text
S3 + CloudFront：$0.19 USD / 月 程度
Serverless Backend比較用：$0.15 USD / 月 程度
単純合算：$0.34 USD / 月 程度
```

ただし、実際の料金は以下により変動する。

- 利用リージョン
- API Gatewayのリクエスト数
- Lambdaの実行回数
- Lambdaのメモリサイズ
- Lambdaの実行時間
- DynamoDBの読み書き回数
- DynamoDBの保存容量
- CloudWatch Logsのログ取り込み量
- CloudWatch Logsの保存期間
- データ転送量
- Free Tierの適用状況
- AWS Pricing Calculator上の前提条件

そのため、Backend実装前にAWS Pricing Calculatorで再確認する。

---

## API Gateway HTTP API

Backend API公開には、API Gateway HTTP APIを優先する。

確認観点は以下。

| 項目 | 確認内容 |
|---|---|
| API種別 | HTTP API |
| 想定リクエスト数 | 個人開発・ポートフォリオ確認用途の低頻度利用を前提 |
| データ転送量 | 仕様本文・生成結果が大きくなりすぎない前提 |
| CORS | CloudFront配信Frontendからの呼び出しを許可 |
| REST APIとの差分 | REST APIの高度な機能は初期段階では使わない |

初期段階では、APIキー、Usage Plan、WAF、Private APIは利用しない。

---

## Lambda

Backend処理にはPython Lambdaを利用する。

確認観点は以下。

| 項目 | 初期方針 |
|---|---|
| ランタイム | Python |
| メモリ | 小さめから開始し、必要に応じて調整 |
| タイムアウト | LLM Mock相当なら短めに設定 |
| 実行回数 | 個人開発・ポートフォリオ確認用途の低頻度利用を前提 |
| VPC | 使用しない |
| 環境変数 | 必要最小限 |
| 秘密情報 | 初期段階では扱わない |
| ログ | CloudWatch Logsへ出力。ただし本文・生成結果全文は出さない |

将来OpenAI APIやAmazon Bedrockを利用する場合は、APIキー、Secrets管理、利用回数制限、失敗時制御、ログ方針を別途検討する。

---

## DynamoDB

履歴保存にはDynamoDBを利用する。

初期方針は以下。

| 項目 | 方針 |
|---|---|
| 課金モード | オンデマンド |
| テーブル用途 | 生成履歴保存 |
| パーティションキー | `history_id` |
| ソートキー | なし |
| 検索 | 初期段階では実装しない |
| TTL | 後続検討 |
| バックアップ | 初期段階では作り込みすぎない |

想定テーブル名は以下。

```text
ai-test-design-support-histories
```

初期段階では、履歴検索、編集、削除、ページネーション、ユーザー別管理、マルチテナントは対象外とする。

---

## CloudWatch Logs

Lambda実行ログはCloudWatch Logsへ出力される。

初期方針は以下。

```text
CloudWatch Logs保持期間：7日
```

ログ料金は、主に以下で増加する可能性がある。

- ログ取り込み量
- ログ保存期間
- リクエスト本文や生成結果全文を出力してしまうこと
- エラー時に大きなスタックトレースや入力本文を出してしまうこと

そのため、以下はログに出力しない。

- 仕様本文
- 補足事項全文
- Markdown全文
- APIキー
- AWS認証情報
- AWSアカウントID
- VPC ID
- EC2 ID
- IPアドレス
- 将来のLLMプロンプト全文
- 顧客情報
- 個人情報
- 業務機密

ログに出してよい情報は以下に限定する。

- request_id
- endpoint
- status_code
- error_type
- history_id
- 処理時間

---

## 料金増加リスク

Backend Serverless構成で注意する料金リスクは以下。

| リスク | 内容 | 対策 |
|---|---|---|
| APIリクエスト増加 | 外部から大量アクセスされる | 初期は公開範囲・CORS・利用導線を限定する |
| Lambda実行時間増加 | 処理が重くなる | タイムアウトを短めに設定し、不要処理を避ける |
| DynamoDB保存量増加 | 仕様本文やMarkdownを大量保存する | 入力文字数制限、保存件数の運用方針を検討する |
| CloudWatch Logs増加 | 本文や生成結果をログ出力する | ログ出力を最小化し、保持期間7日にする |
| 削除漏れ | API Gateway / Lambda / DynamoDB / Logsが残る | `docs/aws-destroy.md` に削除確認手順を明記する |

---

## 再確認タイミング

以下のタイミングで料金見積もりを再確認する。

- Backend実装前
- API Gateway / Lambda / DynamoDB をCDKで追加する前
- CloudWatch Logs保持期間を設定する前
- OpenAI API / Amazon Bedrock連携を検討する前
- READMEやdocsに料金目安を追記する前
- AWSリソースを削除せず継続利用する判断をしたとき