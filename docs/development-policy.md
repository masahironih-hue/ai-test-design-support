# 開発運用方針

## 1. 目的

本ドキュメントは、「業務系SE向け AIテスト設計支援ツール」開発プロジェクトにおける、開発運用方針を整理するものです。

このプロジェクトでは、個人開発として継続しやすく、GitHub上でポートフォリオとして説明しやすい進め方を優先します。

---

## 2. 基本方針

開発では、以下を基本方針とします。

- MVPを優先する
- 最初から大規模SaaSを作らない
- ローカルで動く状態を先に完成させる
- 実装範囲を段階的に広げる
- 重要な決定事項はREADMEまたはdocsに残す
- ChatGPTスレッドだけを唯一の管理台帳にしない
- GitHub Issues、README、docsへ反映する

---

## 3. フェーズ方針

### Phase 0：進め方・環境構築

- 開発環境を整える
- GitHubリポジトリを作成する
- スレッド運用ルールを決める
- セキュリティ方針を整理する

### Phase 1：ローカルMVP

- FastAPI Backendを作成する
- Next.js Frontendを作成する
- LLM Mockでテスト設計結果を生成する
- SQLiteに履歴保存する
- Markdownコピー、履歴一覧、履歴詳細を確認できるようにする

### Phase 2：AWS低コスト版

- AWS SAAで学習した内容を個人開発に落とし込む
- 常時稼働リソースを避ける
- 料金見積もりと削除手順を整備する

### Phase 3以降

- 必要に応じて実務寄り構成やAI / LLM強化を検討する
- コスト、説明価値、実装難易度を比較して判断する

---

## 4. GitHub運用方針

GitHubでは、以下を管理します。

- ソースコード
- README
- docs
- Issues
- Pull Request
- 作業履歴

commit前には、以下を確認します。

```powershell
git status --short
```

不要ファイルや機密情報が含まれていないことを確認します。

---

## 5. ブランチ・commit方針

初期の個人開発では、過度に複雑なブランチ運用は行いません。

- 小さな単位でcommitする
- commitメッセージは作業内容が分かるようにする
- docs更新は `docs:` を使う
- 実装変更は `feat:` または `fix:` を使う

例：

```text
docs: update README for local MVP
feat: add test design history list
fix: format history created_at in JST
```

---

## 6. ChatGPT / Codex / GitHub の役割

### ChatGPT

- 方針整理
- 設計判断
- タスク分解
- エラー原因整理
- README / docs文案
- 面談説明文案

### Codex

- 実装
- テスト
- リファクタ
- コード修正
- README更新補助

### GitHub

- 正式な成果物管理
- Issues管理
- README / docs管理
- commit / push履歴管理

---

## 7. 実装時の優先順位

実装時は、以下の順で優先します。

1. 動く最小構成を作る
2. テストで確認する
3. README / docsに反映する
4. Git管理対象を確認する
5. commit / pushする

初期MVPでは、認証、課金、マルチテナント、ファイルアップロード、Excel出力、RAGは扱いません。

---

## 8. 品質確認方針

Backendでは以下を確認します。

```powershell
cd backend
python -m pytest
```

Frontendでは以下を確認します。

```powershell
cd frontend
pnpm lint
pnpm build
```

---

## 9. ドキュメント更新方針

以下の変更があった場合は、READMEまたはdocsを更新します。

- APIパスを変更したとき
- DB仕様を変更したとき
- 画面仕様を変更したとき
- 環境変数を追加したとき
- 起動手順を変更したとき
- セキュリティ方針を変更したとき
- AWS構成を追加したとき

---

## 10. 守秘義務との関係

本プロジェクトでは、本業の顧客情報、実設計書、実コード、実ログ、個人情報、APIキー、パスワード、アクセストークン、業務機密を使用しません。

動作確認には架空データのみを使用します。

詳細は以下を参照します。

```text
docs/security-policy.md
```
