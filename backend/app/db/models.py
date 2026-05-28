from datetime import datetime, timezone
import uuid

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class TestDesignHistory(Base):
    __tablename__ = "test_design_histories"

    history_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    target_type: Mapped[str] = mapped_column(String(100), nullable=False)
    test_level: Mapped[str] = mapped_column(String(100), nullable=False)
    spec_text: Mapped[str] = mapped_column(Text, nullable=False)
    supplement: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 初期MVPではJSON文字列として保存する
    viewpoints: Mapped[str] = mapped_column(Text, nullable=False)
    test_cases: Mapped[str] = mapped_column(Text, nullable=False)

    markdown: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )