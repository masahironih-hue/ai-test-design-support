import TestDesignForm from "../components/TestDesignForm";

export default function Home() {
  return (
    <main>
      <h1>業務系SE向け AIテスト設計支援ツール</h1>
      <p>
        仕様メモを入力すると、LLM Mock によりテスト観点・テストケース・確認事項を生成します。
      </p>

      <TestDesignForm />
    </main>
  );
}