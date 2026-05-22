import { TestDesignForm } from "@/components/TestDesignForm";

export default function Home() {
  return (
    <main className="page-shell">
      <section className="hero-card">
        <p className="section-label">AI Test Design Support</p>
        <h1>業務系SE向け AIテスト設計支援ツール</h1>
        <p>
          機能概要、画面仕様、API仕様、バッチ仕様などをもとに、テスト観点・テストケース・確認事項の生成を支援する
          Webアプリケーションです。
        </p>
      </section>

      <section className="status-card">
        <h2>現在の実装範囲</h2>
        <ul>
          <li>Next.js / React / TypeScript の Frontend 土台作成済み</li>
          <li>仕様入力フォームを Frontend 単体で実装</li>
          <li>Backend API 接続は次タスクで実装予定</li>
        </ul>
      </section>

      <TestDesignForm />
    </main>
  );
}