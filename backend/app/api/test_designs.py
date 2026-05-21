from fastapi import APIRouter

from app.models.test_design import (
    GenerateTestDesignRequest,
    GenerateTestDesignResponse,
)
from app.services.llm_mock import generate_test_design_mock


router = APIRouter(prefix="/test-designs", tags=["test-designs"])


@router.post("/generate", response_model=GenerateTestDesignResponse)
def generate_test_design(
    request: GenerateTestDesignRequest,
) -> GenerateTestDesignResponse:
    """仕様入力からテスト設計結果を生成する。"""

    return generate_test_design_mock(request)
