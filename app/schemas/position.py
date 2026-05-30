from pydantic import BaseModel, Field


class PositionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class PositionUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class PositionResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
