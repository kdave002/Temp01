from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class Column(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*$",
        description="SQL-safe column identifier (snake_case recommended).",
    )
    type: str = Field(
        min_length=1,
        max_length=32,
        pattern=r"^[A-Za-z][A-Za-z0-9_() ,.-]*$",
        description="Column type descriptor (e.g., int, varchar(255), decimal(10,2)).",
    )

    @field_validator("name", "type")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("value cannot be blank")
        return cleaned


class DriftEvent(BaseModel):
    kind: str = Field(min_length=1, max_length=64, pattern=r"^[a-z_]+$")
    detail: str = Field(min_length=1, max_length=512)
    severity: Literal["low", "medium", "high"] = Field(default="low", description="low|medium|high")
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class DriftRequest(BaseModel):
    previous_schema: list[Column] = Field(default_factory=list, max_length=500)
    current_schema: list[Column] = Field(default_factory=list, max_length=500)
    downstream_model_count: int = Field(default=0, ge=0, le=10_000)

    @model_validator(mode="after")
    def validate_unique_column_names(self) -> "DriftRequest":
        prev_names = [c.name for c in self.previous_schema]
        curr_names = [c.name for c in self.current_schema]

        if len(prev_names) != len(set(prev_names)):
            raise ValueError("previous_schema contains duplicate column names")
        if len(curr_names) != len(set(curr_names)):
            raise ValueError("current_schema contains duplicate column names")

        return self


class DriftResponse(BaseModel):
    events: list[DriftEvent]
    impact_score: int = Field(ge=0, le=100)
    risk: Literal["low", "medium", "high"]
    patch_sql: str
    validation: dict
    pr_body: str
    action_recommendation: str
    recommendation_reasons: list[str]


class SimulationMetricBaselines(BaseModel):
    incidents_per_month: int | None = Field(default=None, ge=0, le=100_000)
    mean_time_to_detect_hours: float | None = Field(default=None, ge=0.0, le=24 * 31)
    mean_time_to_resolve_hours: float | None = Field(default=None, ge=0.0, le=24 * 31)


class SimulationRequest(BaseModel):
    previous_schema: list[Column] = Field(default_factory=list, max_length=500)
    current_schema: list[Column] = Field(default_factory=list, max_length=500)
    downstream_model_count: int = Field(default=0, ge=0, le=10_000)
    metric_baselines: SimulationMetricBaselines | None = None

    @model_validator(mode="after")
    def validate_unique_column_names(self) -> "SimulationRequest":
        prev_names = [c.name for c in self.previous_schema]
        curr_names = [c.name for c in self.current_schema]

        if len(prev_names) != len(set(prev_names)):
            raise ValueError("previous_schema contains duplicate column names")
        if len(curr_names) != len(set(curr_names)):
            raise ValueError("current_schema contains duplicate column names")

        return self


class SimulationResponse(BaseModel):
    predicted_breakage_class: Literal["non_breaking", "potentially_breaking", "likely_breaking"]
    expected_repair_path: str
    confidence_band: Literal["low", "medium", "high"]
    confidence_range: dict[str, float]
    summary: str


class RoiEstimateRequest(BaseModel):
    incidents_per_month: int = Field(ge=0, le=100_000)
    mean_time_to_detect_hours: float = Field(ge=0.0, le=24 * 31)
    mean_time_to_resolve_hours: float = Field(ge=0.0, le=24 * 31)
    engineers_involved_per_incident: float = Field(gt=0.0, le=500.0)
    hourly_engineering_cost_usd: float = Field(gt=0.0, le=10_000.0)
    driftshield_adoption_rate: float = Field(default=1.0, ge=0.0, le=1.0)


class RoiEstimateResponse(BaseModel):
    baseline_monthly_engineering_hours: float = Field(ge=0.0)
    baseline_monthly_cost_usd: float = Field(ge=0.0)
    projected_monthly_engineering_hours: float = Field(ge=0.0)
    projected_monthly_cost_usd: float = Field(ge=0.0)
    monthly_engineering_hours_saved: float = Field(ge=0.0)
    monthly_cost_saved_usd: float = Field(ge=0.0)
    annual_cost_saved_usd: float = Field(ge=0.0)
    monthly_cost_savings_percent: float = Field(ge=0.0, le=100.0)
    assumptions: dict


class PilotReadinessRequest(BaseModel):
    data_owner_identified: bool
    repo_access_configured: bool
    ci_green: bool
    rollback_plan_defined: bool
    oncall_contact_set: bool


class PilotReadinessResponse(BaseModel):
    readiness_score: int = Field(ge=0, le=100)
    status: Literal["not_ready", "ready_with_risks", "ready"]
    missing_items: list[str]
    recommendation: str
