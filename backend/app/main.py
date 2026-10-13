import logging
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator

from .config import settings
from .db import Base, engine, get_db
from .models import Deployment, Environment, Incident
from .schemas import (
    DeploymentCreate,
    DeploymentOut,
    DeploymentStats,
    DeploymentUpdate,
    EnvironmentCreate,
    EnvironmentOut,
    IncidentCreate,
    IncidentOut,
    IncidentStats,
    IncidentUpdate,
    PaginatedDeployments,
    PaginatedIncidents,
    StatsOut,
)

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)

# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="OpsPulse — Deployment & Reliability Operations Platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.on_event("startup")
def startup():
    # In production containers Alembic runs before Uvicorn.
    # create_all is kept here so that test-mode SQLite works without migrations.
    Base.metadata.create_all(bind=engine)
    logger.info("OpsPulse API started")


# ── Utility ────────────────────────────────────────────────────────────────

def _get_or_404(db: Session, model, obj_id: int):
    obj = db.get(model, obj_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} {obj_id} not found",
        )
    return obj


# ── Root / Health / Ready ──────────────────────────────────────────────────

@app.get("/")
def root():
    return {"service": settings.app_name, "version": settings.app_version, "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "UP", "service": settings.app_name}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(select(func.count(Deployment.id)))
        return {"status": "READY"}
    except Exception as exc:  # pragma: no cover
        logger.error("Readiness check failed: %s", exc)
        raise HTTPException(status_code=503, detail="Database not ready")


# ── Stats ──────────────────────────────────────────────────────────────────

@app.get("/api/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    d_rows = db.execute(
        select(Deployment.status, func.count(Deployment.id)).group_by(Deployment.status)
    ).all()
    dc = {r[0]: r[1] for r in d_rows}

    i_rows = db.execute(
        select(Incident.status, func.count(Incident.id)).group_by(Incident.status)
    ).all()
    ic = {r[0]: r[1] for r in i_rows}

    return StatsOut(
        deployments=DeploymentStats(
            total=sum(dc.values()),
            pending=dc.get("PENDING", 0),
            running=dc.get("RUNNING", 0),
            success=dc.get("SUCCESS", 0),
            failed=dc.get("FAILED", 0),
            rolled_back=dc.get("ROLLED_BACK", 0),
        ),
        incidents=IncidentStats(
            total=sum(ic.values()),
            open=ic.get("OPEN", 0),
            investigating=ic.get("INVESTIGATING", 0),
            resolved=ic.get("RESOLVED", 0),
            closed=ic.get("CLOSED", 0),
        ),
    )


# ── Deployments ────────────────────────────────────────────────────────────

@app.get("/api/deployments", response_model=PaginatedDeployments)
def list_deployments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    service: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = select(Deployment).order_by(Deployment.created_at.desc())
    if status:
        q = q.where(Deployment.status == status.upper())
    if service:
        q = q.where(Deployment.service_name.ilike(f"%{service}%"))
    total = db.scalar(select(func.count()).select_from(q.subquery()))
    items = list(db.scalars(q.offset((page - 1) * page_size).limit(page_size)))
    return PaginatedDeployments(total=total, page=page, page_size=page_size, items=items)


@app.get("/api/deployments/{deployment_id}", response_model=DeploymentOut)
def get_deployment(deployment_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, Deployment, deployment_id)


@app.post("/api/deployments", response_model=DeploymentOut, status_code=status.HTTP_201_CREATED)
def create_deployment(payload: DeploymentCreate, db: Session = Depends(get_db)):
    dep = Deployment(**payload.model_dump())
    db.add(dep)
    db.commit()
    db.refresh(dep)
    logger.info("Deployment created: %s v%s", dep.service_name, dep.version)
    return dep


@app.patch("/api/deployments/{deployment_id}", response_model=DeploymentOut)
def update_deployment(deployment_id: int, payload: DeploymentUpdate, db: Session = Depends(get_db)):
    dep = _get_or_404(db, Deployment, deployment_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(dep, key, value)
    db.commit()
    db.refresh(dep)
    logger.info("Deployment %d updated to status %s", dep.id, dep.status)
    return dep


@app.delete("/api/deployments/{deployment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deployment(deployment_id: int, db: Session = Depends(get_db)):
    dep = _get_or_404(db, Deployment, deployment_id)
    db.delete(dep)
    db.commit()


# ── Incidents ──────────────────────────────────────────────────────────────

@app.get("/api/incidents", response_model=PaginatedIncidents)
def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = select(Incident).order_by(Incident.created_at.desc())
    if status:
        q = q.where(Incident.status == status.upper())
    if severity:
        q = q.where(Incident.severity == severity.upper())
    total = db.scalar(select(func.count()).select_from(q.subquery()))
    items = list(db.scalars(q.offset((page - 1) * page_size).limit(page_size)))
    return PaginatedIncidents(total=total, page=page, page_size=page_size, items=items)


@app.get("/api/incidents/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, Incident, incident_id)


@app.post("/api/incidents", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    inc = Incident(**payload.model_dump())
    db.add(inc)
    db.commit()
    db.refresh(inc)
    logger.info("Incident created: %s [%s]", inc.title, inc.severity)
    return inc


@app.patch("/api/incidents/{incident_id}", response_model=IncidentOut)
def update_incident(incident_id: int, payload: IncidentUpdate, db: Session = Depends(get_db)):
    from datetime import datetime, timezone
    inc = _get_or_404(db, Incident, incident_id)
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(inc, key, value)
    if updates.get("status") == "RESOLVED" and not inc.resolved_at:
        inc.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(inc)
    return inc


@app.delete("/api/incidents/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    inc = _get_or_404(db, Incident, incident_id)
    db.delete(inc)
    db.commit()


# ── Environments ───────────────────────────────────────────────────────────

@app.get("/api/environments", response_model=list[EnvironmentOut])
def list_environments(db: Session = Depends(get_db)):
    return list(db.scalars(select(Environment).order_by(Environment.name)))


@app.post("/api/environments", response_model=EnvironmentOut, status_code=status.HTTP_201_CREATED)
def create_environment(payload: EnvironmentCreate, db: Session = Depends(get_db)):
    env = Environment(**payload.model_dump())
    db.add(env)
    db.commit()
    db.refresh(env)
    return env
