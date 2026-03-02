from pydantic import BaseModel, Field


class Column(BaseModel):
    name: str
    type: str


class DriftEvent(BaseModel):
    kind: str
    detail: str
    severity: str = Field(default="low", description="low|medium|high")
    confidence: float | None = None


class DriftRequest(BaseModel):
    previous_schema: list[Column]
    current_schema: list[Column]
    downstream_model_count: int = 0


class DriftResponse(BaseModel):
    events: list[DriftEvent]
    impact_score: int
    risk: str
    patch_sql: str
    validation: dict
    pr_body: str
