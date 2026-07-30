from pydantic import BaseModel, Field


class ContributorInput(BaseModel):
    name: str = Field(min_length=1)
    hours: float = Field(gt=0)
    accuracy: float = Field(gt=0, le=1)
    complexity: int = Field(ge=1, le=5)
    pool_size: int = Field(ge=0)


class CalculateRequest(BaseModel):
    contributors: list[ContributorInput] = Field(min_length=1)
    profit: float = 20000.0
    k: float = 0.01
    platform_share: float = Field(default=0.30, ge=0, le=1)
    cap_multiplier: float = 300.0
    traditional_rate: float = 5.0


class ContributorCalcItem(BaseModel):
    name: str
    hours: float
    accuracy: float
    complexity: int
    pool_size: int
    scarcity: float
    contribution: float
    share_pct: float
    profit: float
    cap: float
    traditional_income: float


class CalculateResponse(BaseModel):
    results: list[ContributorCalcItem]
    total_contribution: float
    distributable: float
    platform_profit: float
    total_traditional: float


class SimulateRequest(BaseModel):
    contributors: list[ContributorInput] = Field(min_length=1)
    profit_per_call: float = 20000.0
    timeline_calls: int = Field(default=5, ge=1, le=200)
    projection_calls: int = Field(default=50, ge=1, le=500)
    k: float = 0.01
    platform_share: float = Field(default=0.30, ge=0, le=1)
    cap_multiplier: float = 300.0
    traditional_rate: float = 5.0


class CallItem(BaseModel):
    name: str
    raw_profit: float
    credited: float
    to_pool: float


class PerCallResult(BaseModel):
    call_index: int
    platform_profit: float
    items: list[CallItem]


class ContributorMeta(BaseModel):
    name: str
    hours: float
    accuracy: float
    complexity: int
    pool_size: int
    scarcity: float
    contribution: float
    share_pct: float
    cap: float
    traditional_income: float


class ContributorSimSummary(BaseModel):
    name: str
    contribution: float
    share_pct: float
    cap: float
    traditional_income: float
    cumulative_income: float
    excess_to_pool: float
    projection_income: float
    projection_excess: float


class SimulateResponse(BaseModel):
    calls: list[PerCallResult]
    summaries: list[ContributorSimSummary]
    total_platform_timeline: float
    total_pool_timeline: float
    total_worker_income_timeline: float
    total_traditional: float
    total_worker_income_projection: float
    total_pool_projection: float
    total_platform_projection: float
    projection_calls: int
    timeline_calls: int
