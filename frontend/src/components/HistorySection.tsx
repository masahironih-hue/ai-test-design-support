"use client";

import { useRef, useState } from "react";
import { HistoryDetail } from "@/components/HistoryDetail";
import { HistoryList } from "@/components/HistoryList";
import {
  fetchTestDesignHistoryDetail,
  type TestDesignHistoryDetail,
} from "@/lib/api";

export function HistorySection() {
  const [selectedHistoryId, setSelectedHistoryId] = useState<string | null>(
    null,
  );
  const [history, setHistory] = useState<TestDesignHistoryDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [copyMessage, setCopyMessage] = useState<string | null>(null);

  const latestRequestIdRef = useRef(0);

  async function handleSelectHistory(historyId: string) {
    const requestId = latestRequestIdRef.current + 1;
    latestRequestIdRef.current = requestId;

    setSelectedHistoryId(historyId);
    setHistory(null);
    setErrorMessage(null);
    setCopyMessage(null);
    setIsLoading(true);

    try {
      const result = await fetchTestDesignHistoryDetail(historyId);

      if (latestRequestIdRef.current !== requestId) {
        return;
      }

      setHistory(result);
    } catch (error) {
      if (latestRequestIdRef.current !== requestId) {
        return;
      }

      setHistory(null);

      if (error instanceof Error && error.message === "NOT_FOUND") {
        setErrorMessage("指定された履歴は見つかりませんでした。");
        return;
      }

      setErrorMessage(
        "履歴詳細の取得に失敗しました。Backendが起動しているか、履歴IDが正しいか確認してください。",
      );
    } finally {
      if (latestRequestIdRef.current === requestId) {
        setIsLoading(false);
      }
    }
  }

  async function handleCopyMarkdown() {
    if (!history?.markdown) {
      setCopyMessage("コピー対象のMarkdownがありません。");
      return;
    }

    try {
      await navigator.clipboard.writeText(history.markdown);
      setCopyMessage("Markdownをコピーしました。");
    } catch {
      setCopyMessage("Markdownのコピーに失敗しました。");
    }
  }

  return (
    <section className="space-y-6">
      <HistoryList
        selectedHistoryId={selectedHistoryId}
        onSelectHistory={handleSelectHistory}
      />

      <HistoryDetail
        selectedHistoryId={selectedHistoryId}
        history={history}
        isLoading={isLoading}
        errorMessage={errorMessage}
        copyMessage={copyMessage}
        onCopyMarkdown={handleCopyMarkdown}
      />
    </section>
  );
}
