from pydantic import BaseModel


class Column(BaseModel):
    name: str
    type: str


class DriftEvent(BaseModel):
    kind: str
    detail: str


class DriftRequest(BaseModel):
    previous_schema: list[Column]
    current_schema: list[Column]


class DriftResponse(BaseModel):
    events: list[DriftEvent]
    patch_sql: str
