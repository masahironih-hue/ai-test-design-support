from typing import Literal
from datetime import datetime

from pydantic import BaseModel, Field


TargetType = Literal["screen", "api", "batch", "db", "external"]
TestLevel = Literal["unit", "integration", "system"]


class GenerateTestDesignRequest(BaseModel):
    """テスト設計生成APIのリクエストモデル。"""

    title: str = Field(..., min_length=1, max_length=100)
    target_type: TargetType
    test_level: TestLevel
    spec_text: str = Field(..., min_length=1, max_length=5000)
    supplement: str | None = Field(default=None, max_length=2000)


class Viewpoint(BaseModel):
    """テスト観点。"""

    category: str = Field(..., min_length=1)
    items: list[str] = Field(default_factory=list)


class TestCase(BaseModel):
    """テストケース。"""

    case_no: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    condition: str = Field(..., min_length=1)
    expected_result: str = Field(..., min_length=1)


class GenerateTestDesignResponse(BaseModel):
    """テスト設計生成APIのレスポンスモデル。"""

    title: str
    target_type: TargetType
    test_level: TestLevel
    viewpoints: list[Viewpoint]
    test_cases: list[TestCase]
    markdown: str


class TestDesignGenerateRequest(BaseModel):
    title: str = Field(..., min_length=1)
    target_type: TargetType
    test_level: TestLevel
    spec_text: str = Field(..., min_length=1)
    supplement: str | None = None


class TestDesignGenerateResponse(BaseModel):
    title: str
    target_type: TargetType
    test_level: TestLevel
    viewpoints: list[Viewpoint]
    test_cases: list[TestCase]
    markdown: str


class TestDesignHistorySummary(BaseModel):
    history_id: str
    title: str
    target_type: str
    test_level: str
    created_at: datetime


class TestDesignHistoryDetail(BaseModel):
    history_id: str
    title: str
    target_type: str
    test_level: str
    spec_text: str
    supplement: str | None
    viewpoints: list[Viewpoint]
    test_cases: list[TestCase]
    markdown: str
    created_at: datetime
