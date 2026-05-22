import type { TestDesignHistoryDetail } from "@/lib/api";
import { formatDateTimeJst } from "@/lib/date";

type HistoryDetailProps = {
  selectedHistoryId: number | null;
  history: TestDesignHistoryDetail | null;
  isLoading: boolean;
  errorMessage: string | null;
  copyMessage: string | null;
  onCopyMarkdown: () => void;
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

function formatLabel(labels: Record<string, string>, value: string): string {
  return labels[value] ?? value;
}

//function formatDateTime(value: string): string {
//  const date = new Date(value);
//
//  if (Number.isNaN(date.getTime())) {
//    return value;
//  }
//
//  return date.toLocaleString("ja-JP");
//}

export function HistoryDetail({
  selectedHistoryId,
  history,
  isLoading,
  errorMessage,
  copyMessage,
  onCopyMarkdown,
}: HistoryDetailProps) {
  if (selectedHistoryId === null) {
    return (
      <section className="rounded-lg border p-4">
        <h2 className="text-xl font-bold">履歴詳細</h2>
        <p className="mt-2 text-sm text-gray-600">
          履歴を選択すると詳細が表示されます。
        </p>
      </section>
    );
  }

  if (isLoading) {
    return (
      <section className="rounded-lg border p-4">
        <h2 className="text-xl font-bold">履歴詳細</h2>
        <p className="mt-2 text-sm text-gray-600">
          履歴詳細を読み込み中です...
        </p>
      </section>
    );
  }

  if (errorMessage !== null) {
    return (
      <section className="rounded-lg border border-red-300 bg-red-50 p-4">
        <h2 className="text-xl font-bold">履歴詳細</h2>
        <p className="mt-2 text-sm text-red-700">{errorMessage}</p>
      </section>
    );
  }

  if (history === null) {
    return (
      <section className="rounded-lg border p-4">
        <h2 className="text-xl font-bold">履歴詳細</h2>
        <p className="mt-2 text-sm text-gray-600">
          履歴詳細が取得されていません。
        </p>
      </section>
    );
  }

  return (
    <section className="rounded-lg border p-4">
      <div className="flex flex-col gap-2">
        <p className="text-sm text-gray-500">履歴ID: #{history.id}</p>
        <h2 className="text-2xl font-bold">{history.title}</h2>

        <div className="grid gap-1 text-sm text-gray-700">
          <p>
            対象種別：
            {formatLabel(targetTypeLabels, history.target_type)}
          </p>
          <p>
            テストレベル：
            {formatLabel(testLevelLabels, history.test_level)}
          </p>
          <p>作成日時：{formatDateTimeJst(history.created_at)}</p>
        </div>
      </div>

      <div className="mt-6 space-y-6">
        <section>
          <h3 className="text-lg font-bold">仕様本文</h3>
          <p className="mt-2 whitespace-pre-wrap rounded bg-gray-50 p-3 text-sm">
            {history.spec_text}
          </p>
        </section>

        <section>
          <h3 className="text-lg font-bold">補足事項</h3>
          <p className="mt-2 whitespace-pre-wrap rounded bg-gray-50 p-3 text-sm">
            {history.supplement || "補足事項はありません。"}
          </p>
        </section>

        <section>
          <h3 className="text-lg font-bold">テスト観点</h3>
          <div className="mt-2 space-y-3">
            {history.viewpoints.length === 0 ? (
              <p className="text-sm text-gray-600">
                テスト観点は登録されていません。
              </p>
            ) : (
              history.viewpoints.map((viewpoint) => (
                <div key={viewpoint.category} className="rounded bg-gray-50 p-3">
                  <h4 className="font-semibold">{viewpoint.category}</h4>
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
                    {viewpoint.items.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ))
            )}
          </div>
        </section>

        <section>
          <h3 className="text-lg font-bold">テストケース</h3>
          <div className="mt-2 space-y-3">
            {history.test_cases.length === 0 ? (
              <p className="text-sm text-gray-600">
                テストケースは登録されていません。
              </p>
            ) : (
              history.test_cases.map((testCase) => (
                <div
                  key={testCase.case_no}
                  className="rounded border bg-gray-50 p-3 text-sm"
                >
                  <p className="font-semibold">
                    {testCase.case_no} / {testCase.category}
                  </p>
                  <p className="mt-2">条件：{testCase.condition}</p>
                  <p className="mt-1">
                    期待結果：{testCase.expected_result}
                  </p>
                </div>
              ))
            )}
          </div>
        </section>

        <section>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <h3 className="text-lg font-bold">Markdown</h3>
            <button
              type="button"
              onClick={onCopyMarkdown}
              disabled={!history.markdown}
              className="rounded bg-gray-900 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-gray-400"
            >
              Markdownをコピー
            </button>
          </div>

          {copyMessage !== null && (
            <p className="mt-2 text-sm text-gray-600">{copyMessage}</p>
          )}

          <pre className="mt-2 overflow-x-auto whitespace-pre-wrap rounded bg-gray-50 p-3 text-sm">
            {history.markdown}
          </pre>
        </section>
      </div>
    </section>
  );
}