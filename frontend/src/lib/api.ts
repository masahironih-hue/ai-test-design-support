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

export type TestDesignHistory = {
  id: number;
  title: string;
  target_type: TargetType;
  test_level: TestLevel;
  created_at: string;
};

type HistoryListResponse =
  | TestDesignHistory[]
  | {
    items?: TestDesignHistory[];
    histories?: TestDesignHistory[];
  };

  export type TestDesignViewpoint = {
  category: string;
  items: string[];
};

export type TestDesignTestCase = {
  case_no: string;
  category: string;
  condition: string;
  expected_result: string;
};

export type TestDesignHistoryDetail = {
  id: number;
  title: string;
  target_type: string;
  test_level: string;
  spec_text: string;
  supplement?: string | null;
  viewpoints: TestDesignViewpoint[];
  test_cases: TestDesignTestCase[];
  markdown: string;
  created_at: string;
};

const getApiBaseUrl = (): string => {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

  if (!apiBaseUrl) {
    throw new Error("NEXT_PUBLIC_API_BASE_URL is not set.");
  }

  return apiBaseUrl;
};

const extractHistories = (
  responseBody: HistoryListResponse,
): TestDesignHistory[] => {
  if (Array.isArray(responseBody)) {
    return responseBody;
  }

  if (Array.isArray(responseBody.items)) {
    return responseBody.items;
  }

  if (Array.isArray(responseBody.histories)) {
    return responseBody.histories;
  }

  return [];
};

export const fetchTestDesignHistories = async (): Promise<
  TestDesignHistory[]
> => {
  const apiBaseUrl = getApiBaseUrl();

  const response = await fetch(`${apiBaseUrl}/test-designs/histories`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch test design histories.");
  }

  const responseBody = (await response.json()) as HistoryListResponse;
  return extractHistories(responseBody);
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

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

export async function fetchTestDesignHistoryDetail(
  historyId: number,
): Promise<TestDesignHistoryDetail> {
  const response = await fetch(
    `${API_BASE_URL}/test-designs/histories/${historyId}`,
    {
      method: "GET",
    },
  );

  if (response.status === 404) {
    throw new Error("NOT_FOUND");
  }

  if (!response.ok) {
    throw new Error("履歴詳細の取得に失敗しました。");
  }

  return response.json();
}