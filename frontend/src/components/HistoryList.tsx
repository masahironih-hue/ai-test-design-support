"use client";

import { useCallback, useEffect, useState } from "react";

import {
  fetchTestDesignHistories,
  type TargetType,
  type TestDesignHistory,
  type TestLevel,
} from "@/lib/api";

const targetTypeLabels: Record<TargetType, string> = {
  screen: "画面",
  api: "API",
  batch: "バッチ",
  db: "DB更新",
  external: "外部連携",
};

const testLevelLabels: Record<TestLevel, string> = {
  unit: "単体テスト",
  integration: "結合テスト",
  system: "システムテスト",
};

const formatDateTime = (value: string): string => {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("ja-JP", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
};

export default function HistoryList() {
  const [histories, setHistories] = useState<TestDesignHistory[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string>("");

  useEffect(() => {
    let isMounted = true;

    const loadInitialHistories = async () => {
      try {
        const fetchedHistories = await fetchTestDesignHistories();

        if (!isMounted) {
          return;
        }

        setHistories(fetchedHistories);
      } catch {
        if (!isMounted) {
          return;
        }

        setErrorMessage(
          "履歴の取得に失敗しました。Backendが起動しているか確認してください。",
        );
        setHistories([]);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    void loadInitialHistories();

    return () => {
      isMounted = false;
    };
  }, []);

  const reloadHistories = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage("");

    try {
      const fetchedHistories = await fetchTestDesignHistories();
      setHistories(fetchedHistories);
    } catch {
      setErrorMessage(
        "履歴の取得に失敗しました。Backendが起動しているか確認してください。",
      );
      setHistories([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <section className="history-section">
      <div className="section-header">
        <div>
          <h2>生成履歴</h2>
          <p>
            保存済みのテスト設計生成履歴を表示します。詳細表示は後続タスクで実装します。
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={() => void reloadHistories()}
          disabled={isLoading}
        >
          再読み込み
        </button>
      </div>

      {isLoading && <p className="info-message">履歴を読み込み中です...</p>}

      {!isLoading && errorMessage && (
        <p className="error-message">{errorMessage}</p>
      )}

      {!isLoading && !errorMessage && histories.length === 0 && (
        <div className="empty-message">
          <p>まだ生成履歴はありません。</p>
          <p>
            仕様を入力してテスト設計を生成すると、ここに履歴が表示されます。
          </p>
        </div>
      )}

      {!isLoading && !errorMessage && histories.length > 0 && (
        <div className="history-list">
          {histories.map((history) => (
            <article className="history-card" key={history.id}>
              <h3>
                #{history.id} {history.title}
              </h3>

              <dl>
                <div>
                  <dt>対象種別</dt>
                  <dd>
                    {targetTypeLabels[history.target_type] ??
                      history.target_type}
                  </dd>
                </div>

                <div>
                  <dt>テストレベル</dt>
                  <dd>
                    {testLevelLabels[history.test_level] ?? history.test_level}
                  </dd>
                </div>

                <div>
                  <dt>作成日時</dt>
                  <dd>{formatDateTime(history.created_at)}</dd>
                </div>
              </dl>

              <p className="future-note">
                詳細表示は次タスク「履歴詳細画面」で実装予定です。
              </p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}