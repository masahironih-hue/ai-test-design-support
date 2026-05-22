"use client";

import { FormEvent, useState } from "react";

type TargetType = "" | "screen" | "api" | "batch" | "db" | "external";
type TestLevel = "" | "unit" | "integration" | "system";

type TestDesignFormValues = {
  title: string;
  target_type: TargetType;
  test_level: TestLevel;
  spec_text: string;
  supplement: string;
};

type ValidationErrors = Partial<Record<keyof TestDesignFormValues, string>>;

const targetTypeOptions: Array<{ value: Exclude<TargetType, "">; label: string }> = [
  { value: "screen", label: "画面" },
  { value: "api", label: "API" },
  { value: "batch", label: "バッチ" },
  { value: "db", label: "DB更新" },
  { value: "external", label: "外部連携" },
];

const testLevelOptions: Array<{ value: Exclude<TestLevel, "">; label: string }> = [
  { value: "unit", label: "単体テスト" },
  { value: "integration", label: "結合テスト" },
  { value: "system", label: "システムテスト" },
];

const initialFormValues: TestDesignFormValues = {
  title: "",
  target_type: "",
  test_level: "",
  spec_text: "",
  supplement: "",
};

function getTargetTypeLabel(value: TargetType): string {
  return targetTypeOptions.find((option) => option.value === value)?.label ?? "-";
}

function getTestLevelLabel(value: TestLevel): string {
  return testLevelOptions.find((option) => option.value === value)?.label ?? "-";
}

function validateForm(values: TestDesignFormValues): ValidationErrors {
  const errors: ValidationErrors = {};

  if (!values.title.trim()) {
    errors.title = "タイトルを入力してください。";
  }

  if (!values.target_type) {
    errors.target_type = "テスト対象種別を選択してください。";
  }

  if (!values.test_level) {
    errors.test_level = "テストレベルを選択してください。";
  }

  if (!values.spec_text.trim()) {
    errors.spec_text = "仕様本文を入力してください。";
  }

  return errors;
}

export function TestDesignForm() {
  const [formValues, setFormValues] = useState<TestDesignFormValues>(initialFormValues);
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [submittedValues, setSubmittedValues] = useState<TestDesignFormValues | null>(null);

  const handleChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = event.target;

    setFormValues((currentValues) => ({
      ...currentValues,
      [name]: value,
    }));
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const validationErrors = validateForm(formValues);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      setSubmittedValues(null);
      return;
    }

    setSubmittedValues(formValues);
  };

  return (
    <section className="form-section" aria-labelledby="test-design-form-title">
      <div className="section-header">
        <p className="section-label">Phase 1 / Frontend</p>
        <h2 id="test-design-form-title">仕様入力フォーム</h2>
        <p>
          テスト設計生成に必要な仕様情報を入力します。今回は Backend API
          には接続せず、入力値の状態管理と最小バリデーションを確認します。
        </p>
      </div>

      <div className="security-notice" role="note">
        <strong>入力時の注意</strong>
        <p>
          顧客名、個人情報、APIキー、パスワード、本番環境情報、業務機密を含む情報は入力しないでください。
          必要に応じてマスキングしてから利用してください。
        </p>
      </div>

      <form className="test-design-form" onSubmit={handleSubmit} noValidate>
        <div className="form-field">
          <label htmlFor="title">タイトル</label>
          <input
            id="title"
            name="title"
            type="text"
            value={formValues.title}
            onChange={handleChange}
            placeholder="例：ログイン画面"
            aria-invalid={Boolean(errors.title)}
          />
          {errors.title && <p className="error-message">{errors.title}</p>}
        </div>

        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="target_type">テスト対象種別</label>
            <select
              id="target_type"
              name="target_type"
              value={formValues.target_type}
              onChange={handleChange}
              aria-invalid={Boolean(errors.target_type)}
            >
              <option value="">選択してください</option>
              {targetTypeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {errors.target_type && <p className="error-message">{errors.target_type}</p>}
          </div>

          <div className="form-field">
            <label htmlFor="test_level">テストレベル</label>
            <select
              id="test_level"
              name="test_level"
              value={formValues.test_level}
              onChange={handleChange}
              aria-invalid={Boolean(errors.test_level)}
            >
              <option value="">選択してください</option>
              {testLevelOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {errors.test_level && <p className="error-message">{errors.test_level}</p>}
          </div>
        </div>

        <div className="form-field">
          <label htmlFor="spec_text">仕様本文</label>
          <textarea
            id="spec_text"
            name="spec_text"
            value={formValues.spec_text}
            onChange={handleChange}
            rows={8}
            placeholder="例：架空のログイン画面仕様、入力チェック、認証処理、エラー表示仕様などを入力してください。"
            aria-invalid={Boolean(errors.spec_text)}
          />
          {errors.spec_text && <p className="error-message">{errors.spec_text}</p>}
        </div>

        <div className="form-field">
          <label htmlFor="supplement">補足事項</label>
          <textarea
            id="supplement"
            name="supplement"
            value={formValues.supplement}
            onChange={handleChange}
            rows={4}
            placeholder="例：確認したい観点、前提条件、特記事項など"
          />
          <p className="field-help">任意入力です。</p>
        </div>

        <div className="form-actions">
          <button type="submit">入力内容を確認する</button>
        </div>
      </form>

      {submittedValues && (
        <div className="submitted-preview" aria-live="polite">
          <h3>入力内容確認</h3>
          <dl>
            <div>
              <dt>タイトル</dt>
              <dd>{submittedValues.title}</dd>
            </div>
            <div>
              <dt>テスト対象種別</dt>
              <dd>
                {getTargetTypeLabel(submittedValues.target_type)}
                <span className="code-value">code: {submittedValues.target_type}</span>
              </dd>
            </div>
            <div>
              <dt>テストレベル</dt>
              <dd>
                {getTestLevelLabel(submittedValues.test_level)}
                <span className="code-value">code: {submittedValues.test_level}</span>
              </dd>
            </div>
            <div>
              <dt>仕様本文</dt>
              <dd className="pre-wrap">{submittedValues.spec_text}</dd>
            </div>
            <div>
              <dt>補足事項</dt>
              <dd className="pre-wrap">{submittedValues.supplement || "未入力"}</dd>
            </div>
          </dl>
        </div>
      )}
    </section>
  );
}