from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

# ── Status / Severity enums ────────────────────────────────────────────────

DeploymentStatusLiteral = Literal[
    "PENDING", "RUNNING", "SUCCESS", "FAILED", "ROLLED_BACK"
]
IncidentSeverityLiteral = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
IncidentStatusLiteral = Literal["OPEN", "INVESTIGATING", "RESOLVED", "CLOSED"]

# ── Environment ────────────────────────────────────────────────────────────


class EnvironmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = ""


class EnvironmentOut(EnvironmentCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ── Deployment ─────────────────────────────────────────────────────────────


class DeploymentCreate(BaseModel):
    service_name: str = Field(min_length=1, max_length=200)
    version: str = Field(min_length=1, max_length=100)
    environment_id: Optional[int] = None
    status: DeploymentStatusLiteral = "PENDING"
    deployed_by: str = "system"
    notes: str = ""


class DeploymentUpdate(BaseModel):
    service_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    version: Optional[str] = Field(default=None, min_length=1, max_length=100)
    environment_id: Optional[int] = None
    status: Optional[DeploymentStatusLiteral] = None
    deployed_by: Optional[str] = None
    notes: Optional[str] = None


class DeploymentOut(BaseModel):
    id: int
    service_name: str
    version: str
    environment_id: Optional[int]
    status: str
    deployed_by: str
    notes: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ── Incident ───────────────────────────────────────────────────────────────


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    severity: IncidentSeverityLiteral = "MEDIUM"
    status: IncidentStatusLiteral = "OPEN"
    affected_service: str = ""
    owner: str = "Unassigned"


class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    severity: Optional[IncidentSeverityLiteral] = None
    status: Optional[IncidentStatusLiteral] = None
    affected_service: Optional[str] = None
    owner: Optional[str] = None


class IncidentOut(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    status: str
    affected_service: str
    owner: str
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


# ── Stats ──────────────────────────────────────────────────────────────────


class DeploymentStats(BaseModel):
    total: int
    pending: int
    running: int
    success: int
    failed: int
    rolled_back: int


class IncidentStats(BaseModel):
    total: int
    open: int
    investigating: int
    resolved: int
    closed: int


class StatsOut(BaseModel):
    deployments: DeploymentStats
    incidents: IncidentStats


# ── Pagination ─────────────────────────────────────────────────────────────


class PaginatedDeployments(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[DeploymentOut]


class PaginatedIncidents(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[IncidentOut]
