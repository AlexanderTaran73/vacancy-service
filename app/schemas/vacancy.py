from pydantic import BaseModel, Field

from app.models.vacancy import VacancyStatus


class VacancyCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    position_id: int = Field(gt=0)
    category_id: int = Field(gt=0)
    status: VacancyStatus = VacancyStatus.open


class VacancyUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1)
    position_id: int | None = Field(None, gt=0)
    category_id: int | None = Field(None, gt=0)
    status: VacancyStatus | None = None


class VacancyResponse(BaseModel):
    id: int
    title: str
    description: str
    position_id: int
    category_id: int
    status: VacancyStatus

    model_config = {"from_attributes": True}
