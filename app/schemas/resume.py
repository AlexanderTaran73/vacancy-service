from typing import Any

from pydantic import BaseModel, Field

from app.models.resume import ResumeStatus


class ResumeCreate(BaseModel):
    candidate_data: dict[str, Any]
    category_id: int = Field(gt=0)
    status: ResumeStatus = ResumeStatus.active


class ResumeUpdate(BaseModel):
    candidate_data: dict[str, Any] | None = None
    category_id: int | None = Field(None, gt=0)
    status: ResumeStatus | None = None


class ResumeResponse(BaseModel):
    id: int
    candidate_data: dict[str, Any]
    category_id: int
    status: ResumeStatus

    model_config = {"from_attributes": True}
