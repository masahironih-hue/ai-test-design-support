import json
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.models import TestDesignHistory
from app.models.test_design import (
    TestDesignGenerateRequest,
    TestDesignGenerateResponse,
    TestDesignHistoryDetail,
    TestDesignHistorySummary,
)


def _to_json_text(value: Any) -> str:
    """
    Convert Pydantic models / list / dict into JSON text for SQLite storage.
    """
    return json.dumps(jsonable_encoder(value), ensure_ascii=False)


def _from_json_text(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return []


def save_test_design_history(
    db: Session,
    request: TestDesignGenerateRequest,
    response: TestDesignGenerateResponse,
) -> TestDesignHistory:
    history = TestDesignHistory(
        title=request.title,
        target_type=request.target_type,
        test_level=request.test_level,
        spec_text=request.spec_text,
        supplement=request.supplement,
        viewpoints=_to_json_text(response.viewpoints),
        test_cases=_to_json_text(response.test_cases),
        markdown=response.markdown,
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return history


def list_test_design_histories(db: Session) -> list[TestDesignHistorySummary]:
    histories = (
        db.query(TestDesignHistory)
        .order_by(desc(TestDesignHistory.created_at), desc(TestDesignHistory.history_id))
        .all()
    )

    return [
        TestDesignHistorySummary(
            history_id=history.history_id,
            title=history.title,
            target_type=history.target_type,
            test_level=history.test_level,
            created_at=history.created_at,
        )
        for history in histories
    ]


def get_test_design_history(
    db: Session,
    history_id: str,
) -> TestDesignHistoryDetail | None:
    history = db.get(TestDesignHistory, history_id)

    if history is None:
        return None

    return TestDesignHistoryDetail(
        history_id=history.history_id,
        title=history.title,
        target_type=history.target_type,
        test_level=history.test_level,
        spec_text=history.spec_text,
        supplement=history.supplement,
        viewpoints=_from_json_text(history.viewpoints),
        test_cases=_from_json_text(history.test_cases),
        markdown=history.markdown,
        created_at=history.created_at,
    )