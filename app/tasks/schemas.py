from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: Optional[str] = None
    done: bool = False


class ConsultingResponse(BaseModel):
    task_id: int
    title: str
    action_plan: str


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    done: bool
