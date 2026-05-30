from pydantic import BaseModel, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    login: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.employee


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    login: str
    role: UserRole

    model_config = {"from_attributes": True}


class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=128)
