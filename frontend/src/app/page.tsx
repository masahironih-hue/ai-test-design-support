export default function Home() {
  return (
    <main className="page">
      <section className="hero">
        <p className="eyebrow">Phase 1 Local MVP</p>
        <h1>業務系SE向け AIテスト設計支援ツール</h1>
        <p className="lead">
          仕様メモから、テスト観点・テストケース・確認事項を生成するための支援ツールです。
        </p>
      </section>

      <section className="card">
        <h2>現在の実装状態</h2>
        <ul>
          <li>Frontend 最小構成を作成中</li>
          <li>Backend API は実装済み</li>
          <li>Backend API 接続は後続タスクで実装予定</li>
          <li>仕様入力フォーム、生成結果表示、履歴画面は後続タスクで実装予定</li>
        </ul>
      </section>

      <section className="card warning">
        <h2>セキュリティ注意事項</h2>
        <p>
          顧客名、個人情報、APIキー、パスワード、本番環境情報、業務機密を含む情報は入力しないでください。
          必要に応じて、架空データへの置き換えやマスキングを行ってから利用してください。
        </p>
      </section>
    </main>
  );
}