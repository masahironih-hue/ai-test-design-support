# ローカルMVP総合動作確認メモ

## 1. 目的

Phase 1：ローカルMVPの主要機能について、Backend / Frontend を通した一連の動作が成立していることを確認する。

確認対象は以下の流れとする。

```text
Backend起動
Frontend起動
仕様入力
Backend API呼び出し
LLM Mockによるテスト設計生成
SQLiteへの履歴保存
生成結果表示
Markdownコピー
履歴一覧表示
履歴詳細表示
保存済みMarkdownコピー
```

---

## 2. 確認環境

- OS：Windows
- Shell：PowerShell
- Backend：FastAPI
- Frontend：Next.js / React / TypeScript
- DB：SQLite
- Package Manager：pnpm
- Backend URL：http://localhost:8000
- Frontend URL：http://localhost:3000

---

## 3. 総合動作確認結果

| No | 確認項目 | 結果 | 備考 |
|---:|---|---|---|
| 1 | Backend起動 | OK | `uvicorn app.main:app --reload` で起動確認 |
| 2 | `GET /health` | OK | `status: ok` を確認 |
| 3 | Frontend起動 | OK | `pnpm dev` で起動確認 |
| 4 | トップページ表示 | OK | 仕様入力フォーム、履歴一覧、履歴詳細エリアを確認 |
| 5 | 必須入力チェック | OK | `title` / `target_type` / `test_level` / `spec_text` のバリデーションを確認 |
| 6 | 仕様入力から生成 | OK | 画面から `POST /test-designs/generate` を呼び出し確認 |
| 7 | 生成結果表示 | OK | テスト観点、テストケース、Markdown表示を確認 |
| 8 | Markdownコピー | OK | 生成結果のMarkdownコピーを確認 |
| 9 | SQLite履歴保存 | OK | 生成後に履歴一覧へ反映されることを確認 |
| 10 | 履歴一覧表示 | OK | タイトル、対象種別、テストレベル、作成日時を確認 |
| 11 | 履歴詳細表示 | OK | 仕様本文、補足事項、観点、テストケース、Markdownを確認 |
| 12 | 保存済みMarkdownコピー | OK | 履歴詳細側のMarkdownコピーを確認 |
| 13 | Backend再起動後の履歴保持 | OK | SQLite DBに保存された履歴が保持されることを確認 |

---

## 4. コマンド確認結果

| コマンド | 結果 | 備考 |
|---|---|---|
| `python -m pytest` | OK | Backend主要APIテスト成功 |
| `pnpm lint` | OK | ESLintエラーなし |
| `pnpm build` | OK | TypeScript / Next.js build成功 |

---

## 5. Git管理・セキュリティ確認結果

| 確認項目 | 結果 | 備考 |
|---|---|---|
| `.env` がGit管理対象外 | OK | 実値ファイルをGit管理しない |
| `.env.local` がGit管理対象外 | OK | Frontendローカル設定用 |
| `.venv/` がGit管理対象外 | OK | Python仮想環境をGit管理しない |
| `node_modules/` がGit管理対象外 | OK | npm/pnpm依存物をGit管理しない |
| `.next/` がGit管理対象外 | OK | Next.js生成物をGit管理しない |
| SQLite DBファイルがGit管理対象外 | OK | ローカルDBファイルをGit管理しない |
| APIキー混入なし | OK | 実値なし |
| パスワード混入なし | OK | 実値なし |
| アクセストークン混入なし | OK | 実値なし |
| 顧客情報・個人情報・業務機密混入なし | OK | 架空データのみ使用 |

---

## 6. 総合動作確認中に見つかった課題と対応

### 6.1 履歴一覧・履歴詳細の日時表示

#### 事象

履歴一覧の作成日時がUTCのまま表示されていた。

```text
NG：2026/05/22 07:35
OK：2026/05/22 16:35
```

#### 対応方針

Backend / DB の保存値はUTC基準のままとし、Frontend表示時にJSTへ変換する方針とした。

#### 理由

- DB保存値はUTC基準の方が将来のAWS移行やログ確認と整合しやすい
- 今回の要件は画面表示上のJST化であり、保存値の変更は不要
- 既存履歴やBackendテストへの影響を抑えられる

#### 対応結果

履歴一覧・履歴詳細の作成日時をJST表示に修正した。

---

## 7. 現状仕様として扱う内容

### 7.1 SQLite履歴保持

Backendを再起動しても履歴は削除されない。

これは、SQLite DBファイルに履歴を保存しているためであり、現状仕様として扱う。

開発中に履歴を初期化したい場合は、Backend停止後に開発用SQLite DBファイルを手動削除する。

---

## 8. README / docs 反映候補

後続タスク `[Docs] ローカルMVP README整備` で、以下を反映候補とする。

- Backend起動手順
- Frontend起動手順
- `.env.example` / `.env.local` の扱い
- ローカルMVPでできること
- 仕様入力からテスト設計生成までの操作手順
- Markdownコピー手順
- 履歴一覧・履歴詳細の確認手順
- `python -m pytest`
- `pnpm lint`
- `pnpm build`
- SQLite履歴保存の仕様
- Backend再起動後も履歴が保持される仕様
- 開発中の履歴初期化方法
- 機密情報入力禁止の注意事項
- 現時点の制約
- 今後の改善候補

---

## 9. 既知の制約

Phase 1：ローカルMVP時点では、以下は未実装とする。

- OpenAI API連携
- Amazon Bedrock連携
- AWSデプロイ
- Docker構成
- 認証
- 課金
- マルチテナント
- 履歴検索
- 履歴編集
- 履歴削除
- ページネーション
- ファイルアップロード
- Excel出力
- RAG
- Markdownレンダリングライブラリ導入

---

## 10. 完了判定

以下を満たしたため、ローカルMVP総合動作確認は完了扱いとする。

- Backendが起動できる
- Frontendが起動できる
- `GET /health` が正常応答する
- 仕様入力フォームが正常に動作する
- 必須入力チェックが正常に動作する
- 画面から `POST /test-designs/generate` を呼び出せる
- 生成結果が画面に表示される
- Markdownコピーができる
- SQLiteに履歴保存される
- 履歴一覧が表示される
- 履歴詳細が表示される
- 保存済みMarkdownコピーができる
- Backend再起動後も履歴が保持される
- `python -m pytest` が成功する
- `pnpm lint` が成功する
- `pnpm build` が成功する
- Git管理対象に不要ファイルや機密情報が含まれていない
- README / docs に反映すべき内容を整理できている

---

## 11. 次タスク

次は以下に進む。

```text
[Docs] ローカルMVP README整備
```

この次タスクでは、今回の総合動作確認結果をもとに、README、起動手順、操作手順、注意事項、既知の制約を整理する。