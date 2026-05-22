# Frontend

「業務系SE向け AIテスト設計支援ツール」の Frontend です。

## 技術スタック

- Next.js
- React
- TypeScript
- pnpm
- App Router

## 起動手順

リポジトリルートから以下を実行します。

```powershell
cd frontend
pnpm install
pnpm dev
```

ブラウザで以下を開きます。

```text
http://localhost:3000
```

## 確認コマンド

`frontend/` ディレクトリで以下を実行します。

```powershell
pnpm lint
pnpm build
```

## 表示内容

トップページでは、以下を表示します。

- アプリ名
  - 業務系SE向け AIテスト設計支援ツール
- 簡単な説明
  - 仕様メモからテスト観点・テストケース・確認事項を生成する支援ツールであること
- 現在の実装状態
  - Frontend 最小構成
  - Backend API は実装済み
  - API 接続は後続タスクで実装予定
- セキュリティ注意事項

## セキュリティ注意事項

このアプリケーションでは、以下の情報を入力しないでください。

- 顧客名
- 個人情報
- APIキー
- パスワード
- アクセストークン
- 本番環境情報
- 業務機密
- 実際の設計書
- 実際のソースコード
- 実際のログ

デモや検証には、架空データまたはマスキング済みデータのみを使用してください。

## 今回の実装範囲

今回の Frontend 最小構成では、以下のみを実装しています。

- Next.js / React / TypeScript の最小構成
- トップページ表示
- アプリ概要の表示
- 現在の実装状態の表示
- セキュリティ注意事項の表示

以下はまだ実装していません。

- 仕様入力フォーム
- Backend API 接続
- 生成結果表示
- Markdown コピー機能
- 履歴一覧画面
- 履歴詳細画面

## Git 管理上の注意

以下は Git 管理対象に含めません。

- `node_modules/`
- `.next/`
- `.env`
- `.env.local`
- `.env.*.local`

