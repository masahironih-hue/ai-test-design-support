export type TargetType = "screen" | "api" | "batch" | "db" | "external";

export type TestLevel = "unit" | "integration" | "system";

export type TestDesignRequest = {
  title: string;
  target_type: TargetType;
  test_level: TestLevel;
  spec_text: string;
  supplement?: string;
};

export type Viewpoint = {
  category: string;
  items: string[];
};

export type TestCase = {
  case_no: string;
  category: string;
  condition: string;
  expected_result: string;
};

export type TestDesignResponse = {
  id?: number;
  title: string;
  target_type: TargetType;
  test_level: TestLevel;
  viewpoints: Viewpoint[];
  test_cases: TestCase[];
  markdown: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function buildUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

function formatErrorDetail(detail: unknown): string {
  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

        if (
          typeof item === "object" &&
          item !== null &&
          "msg" in item &&
          typeof item.msg === "string"
        ) {
          return item.msg;
        }

        return JSON.stringify(item);
      })
      .join("\n");
  }

  if (typeof detail === "object" && detail !== null) {
    return JSON.stringify(detail);
  }

  return "API呼び出しに失敗しました。";
}

export async function generateTestDesign(
  request: TestDesignRequest,
): Promise<TestDesignResponse> {
  const response = await fetch(buildUrl("/test-designs/generate"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let message = `API呼び出しに失敗しました。status=${response.status}`;

    try {
      const errorBody: unknown = await response.json();

      if (
        typeof errorBody === "object" &&
        errorBody !== null &&
        "detail" in errorBody
      ) {
        message = formatErrorDetail(errorBody.detail);
      }
    } catch {
      // JSON以外のエラーレスポンスの場合は、statusベースのメッセージを使う
    }

    throw new Error(message);
  }

  return response.json() as Promise<TestDesignResponse>;
}