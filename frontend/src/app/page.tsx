import { HistorySection } from "@/components/HistorySection";
import { TestDesignForm } from "@/components/TestDesignForm";

export default function Home() {
  return (
    <main className="page">
      <section className="hero">
        <h1>業務系SE向け AIテスト設計支援ツール</h1>
        <p>
          機能概要や仕様メモを入力し、テスト観点・テストケース・確認事項を生成します。
        </p>
      </section>

      <section className="security-notice">
        <h2>利用上の注意</h2>
        <p>
          顧客名、個人情報、APIキー、パスワード、本番環境情報、業務機密を含む情報は入力しないでください。
          必要に応じてマスキングしてから利用してください。
        </p>
      </section>

      <TestDesignForm />

      <HistorySection />
    </main>
  );
}