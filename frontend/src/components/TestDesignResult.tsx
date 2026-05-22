"use client";

import { useState } from "react";
import type { TestDesignResponse } from "../lib/api";

type TestDesignResultProps = {
  result: TestDesignResponse;
};

const targetTypeLabels: Record<string, string> = {
  screen: "画面",
  api: "API",
  batch: "バッチ",
  db: "DB",
  external: "外部連携",
};

const testLevelLabels: Record<string, string> = {
  unit: "単体テスト",
  integration: "結合テスト",
  system: "総合テスト",
};

export default function TestDesignResult({ result }: TestDesignResultProps) {
  type CopyStatus = "idle" | "success" | "error";

  const [copyStatus, setCopyStatus] = useState<CopyStatus>("idle");

  const markdown = result.markdown ?? "";
  const canCopyMarkdown = markdown.trim().length > 0;

  const handleCopyMarkdown = async () => {
    if (!canCopyMarkdown) {
      setCopyStatus("error");
      return;
    }

    if (!navigator.clipboard) {
      setCopyStatus("error");
      return;
    }

    try {
      await navigator.clipboard.writeText(markdown);
      setCopyStatus("success");
    } catch {
      setCopyStatus("error");
    }
  };

  return (
    <section>
      <h2>生成結果</h2>

      <div>
        <p>
          <strong>タイトル:</strong> {result.title}
        </p>
        <p>
          <strong>テスト対象種別:</strong>{" "}
          {targetTypeLabels[result.target_type] ?? result.target_type}
        </p>
        <p>
          <strong>テストレベル:</strong>{" "}
          {testLevelLabels[result.test_level] ?? result.test_level}
        </p>
        {result.id !== undefined && (
          <p>
            <strong>履歴ID:</strong> {result.id}
          </p>
        )}
      </div>

      <section>
        <h3>テスト観点</h3>

        {result.viewpoints.length === 0 ? (
          <p>テスト観点はありません。</p>
        ) : (
          result.viewpoints.map((viewpoint) => (
            <div key={viewpoint.category}>
              <h4>{viewpoint.category}</h4>
              <ul>
                {viewpoint.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ))
        )}
      </section>

      <section>
        <h3>テストケース</h3>

        {result.test_cases.length === 0 ? (
          <p>テストケースはありません。</p>
        ) : (
          <div>
            {result.test_cases.map((testCase) => (
              <article key={testCase.case_no}>
                <h4>
                  {testCase.case_no}：{testCase.category}
                </h4>
                <p>
                  <strong>条件:</strong> {testCase.condition}
                </p>
                <p>
                  <strong>期待結果:</strong> {testCase.expected_result}
                </p>
              </article>
            ))}
          </div>
        )}
      </section>

      <section>
        <h3>Markdown</h3>
        <pre>{result.markdown}</pre>
      </section>

      <div className="result-section-header">
        <h3>Markdown形式の生成結果</h3>

        <button
          type="button"
          onClick={handleCopyMarkdown}
          disabled={!canCopyMarkdown}
          className="copy-button"
        >
          Markdownをコピー
        </button>
      </div>

      {copyStatus === "success" && (
        <p className="copy-message" role="status">
          Markdownをコピーしました。
        </p>
      )}

      {copyStatus === "error" && (
        <p className="copy-message copy-message-error" role="alert">
          Markdownのコピーに失敗しました。
        </p>
      )}

      <pre className="markdown-preview">{markdown}</pre>

    </section>
  );
}