
from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    done: bool = False


class ConsultingResponse(BaseModel):
    task_id: int
    title: str
    action_plan: str


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    done: bool
