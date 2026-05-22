"use client";

import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";

import { generateTestDesign } from "../lib/api";
import type {
  TargetType,
  TestDesignResponse,
  TestLevel,
} from "../lib/api";
import TestDesignResult from "./TestDesignResult";

type FormTargetType = "" | TargetType;
type FormTestLevel = "" | TestLevel;

type TestDesignFormValues = {
  title: string;
  target_type: FormTargetType;
  test_level: FormTestLevel;
  spec_text: string;
  supplement: string;
};

type ValidationErrors = Partial<Record<keyof TestDesignFormValues, string>>;

const targetTypeOptions: Array<{ value: TargetType; label: string }> = [
  { value: "screen", label: "画面" },
  { value: "api", label: "API" },
  { value: "batch", label: "バッチ" },
  { value: "db", label: "DB更新" },
  { value: "external", label: "外部連携" },
];

const testLevelOptions: Array<{ value: TestLevel; label: string }> = [
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
  const [formValues, setFormValues] =
    useState<TestDesignFormValues>(initialFormValues);
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [apiError, setApiError] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [result, setResult] = useState<TestDesignResponse | null>(null);

  const handleChange = (
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = event.target;

    setFormValues((currentValues) => ({
      ...currentValues,
      [name]: value,
    }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const validationErrors = validateForm(formValues);
    setErrors(validationErrors);
    setApiError("");

    if (Object.keys(validationErrors).length > 0) {
      setResult(null);
      return;
    }

    setIsSubmitting(true);
    setResult(null);

    try {
      const response = await generateTestDesign({
        title: formValues.title,
        target_type: formValues.target_type as TargetType,
        test_level: formValues.test_level as TestLevel,
        spec_text: formValues.spec_text,
        supplement: formValues.supplement,
      });

      setResult(response);
    } catch (error) {
      if (error instanceof Error) {
        setApiError(error.message);
      } else {
        setApiError("API呼び出し中に不明なエラーが発生しました。");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="form-section" aria-labelledby="test-design-form-title">
      <div className="section-header">
        <p className="section-label">Phase 1 / Frontend + Backend API</p>
        <h2 id="test-design-form-title">仕様入力フォーム</h2>
        <p>
          テスト設計生成に必要な仕様情報を入力し、Backend API
          を呼び出してテスト観点・テストケース・Markdown形式の結果を生成します。
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
            {errors.target_type && (
              <p className="error-message">{errors.target_type}</p>
            )}
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
            {errors.test_level && (
              <p className="error-message">{errors.test_level}</p>
            )}
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
            placeholder="例：利用者IDとパスワードを入力し、認証に成功した場合はメニュー画面へ遷移する。認証に失敗した場合はエラーメッセージを表示する。"
            aria-invalid={Boolean(errors.spec_text)}
          />
          {errors.spec_text && (
            <p className="error-message">{errors.spec_text}</p>
          )}
        </div>

        <div className="form-field">
          <label htmlFor="supplement">補足事項</label>
          <textarea
            id="supplement"
            name="supplement"
            value={formValues.supplement}
            onChange={handleChange}
            rows={4}
            placeholder="例：業務系Webアプリのログイン機能を想定する。"
          />
          <p className="field-help">任意入力です。</p>
        </div>

        {apiError && (
          <p className="error-message" role="alert">
            APIエラー: {apiError}
          </p>
        )}

        {isSubmitting && (
          <p className="field-help" aria-live="polite">
            Backend API に接続しています...
          </p>
        )}

        <div className="form-actions">
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "生成中..." : "テスト設計を生成する"}
          </button>
        </div>
      </form>

      {result && (
        <div className="submitted-preview" aria-live="polite">
          <TestDesignResult result={result} />
        </div>
      )}
    </section>
  );
}

export default TestDesignForm;