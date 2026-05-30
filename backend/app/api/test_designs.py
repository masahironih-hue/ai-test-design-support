from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.test_design import (
    TestDesignGenerateRequest,
    TestDesignGenerateResponse,
    TestDesignHistoryDetail,
    TestDesignHistorySummary,
)
from app.services.history_service import (
    get_test_design_history,
    list_test_design_histories,
    save_test_design_history,
)
from app.services.llm_errors import LLMProviderError
from app.services.llm_provider import generate_test_design as generate_test_design_by_provider

router = APIRouter(prefix="/test-designs", tags=["test-designs"])


@router.post("/generate", response_model=TestDesignGenerateResponse)
def generate_test_design(
    request: TestDesignGenerateRequest,
    db: Session = Depends(get_db),
) -> TestDesignGenerateResponse:
    try:
        response = generate_test_design_by_provider(request)
    except LLMProviderError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.public_message) from exc

    save_test_design_history(
        db=db,
        request=request,
        response=response,
    )

    return response


@router.get("/histories", response_model=list[TestDesignHistorySummary])
def get_histories(
    db: Session = Depends(get_db),
) -> list[TestDesignHistorySummary]:
    return list_test_design_histories(db)


@router.get("/histories/{history_id}", response_model=TestDesignHistoryDetail)
def get_history(
    history_id: str,
    db: Session = Depends(get_db),
) -> TestDesignHistoryDetail:
    history = get_test_design_history(db=db, history_id=history_id)

    if history is None:
        raise HTTPException(status_code=404, detail="History not found")

    return history
