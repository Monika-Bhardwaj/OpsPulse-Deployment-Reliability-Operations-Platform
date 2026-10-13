"""
OpsPulse API — Pytest test suite
Covers: health, deployments (CRUD), incidents (CRUD), stats, validation, 404s.
Uses an in-memory SQLite database isolated per session.
"""
import os

# Must be set before any app import so that config picks up the test DB.
os.environ["DATABASE_URL"] = "sqlite:///./test_opspulse.db"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


# ── Fixtures ───────────────────────────────────────────────────────────────


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """Create all tables once for the session, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_opspulse.db"):
        os.remove("test_opspulse.db")


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


# ── Health / Root ──────────────────────────────────────────────────────────


def test_health_returns_up(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "UP"


def test_root_returns_service_name(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "OpsPulse API"
    assert "docs" in data


def test_ready_returns_ready(client):
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "READY"


# ── Deployments ────────────────────────────────────────────────────────────


def test_create_deployment_success(client):
    payload = {
        "service_name": "payment-service",
        "version": "v1.2.3",
        "status": "PENDING",
        "deployed_by": "ci-pipeline",
        "notes": "Automated deploy",
    }
    resp = client.post("/api/deployments", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["service_name"] == "payment-service"
    assert data["version"] == "v1.2.3"
    assert data["status"] == "PENDING"
    assert "id" in data
    assert "created_at" in data


def test_get_deployment_by_id(client):
    # Create one first
    resp = client.post(
        "/api/deployments",
        json={"service_name": "auth-service", "version": "v2.0.0"},
    )
    dep_id = resp.json()["id"]

    resp = client.get(f"/api/deployments/{dep_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == dep_id
    assert resp.json()["service_name"] == "auth-service"


def test_list_deployments_returns_paginated(client):
    resp = client.get("/api/deployments?page=1&page_size=5")
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)
    assert data["page"] == 1


def test_update_deployment_status(client):
    resp = client.post(
        "/api/deployments",
        json={"service_name": "gateway", "version": "v0.9.0"},
    )
    dep_id = resp.json()["id"]

    resp = client.patch(f"/api/deployments/{dep_id}", json={"status": "SUCCESS"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "SUCCESS"


def test_delete_deployment(client):
    resp = client.post(
        "/api/deployments",
        json={"service_name": "temp-service", "version": "v0.0.1"},
    )
    dep_id = resp.json()["id"]

    resp = client.delete(f"/api/deployments/{dep_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/deployments/{dep_id}")
    assert resp.status_code == 404


def test_get_deployment_not_found(client):
    resp = client.get("/api/deployments/99999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_create_deployment_validation_empty_service_name(client):
    resp = client.post("/api/deployments", json={"service_name": "", "version": "v1"})
    assert resp.status_code == 422


def test_create_deployment_validation_invalid_status(client):
    resp = client.post(
        "/api/deployments",
        json={"service_name": "svc", "version": "v1", "status": "INVALID_STATUS"},
    )
    assert resp.status_code == 422


def test_filter_deployments_by_status(client):
    client.post(
        "/api/deployments",
        json={"service_name": "filter-test", "version": "v1", "status": "FAILED"},
    )
    resp = client.get("/api/deployments?status=FAILED")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert all(d["status"] == "FAILED" for d in items)


# ── Incidents ──────────────────────────────────────────────────────────────


def test_create_incident_success(client):
    payload = {
        "title": "Database connection timeout",
        "description": "PostgreSQL connections timing out in prod",
        "severity": "HIGH",
        "status": "OPEN",
        "affected_service": "orders-service",
        "owner": "ops-team",
    }
    resp = client.post("/api/incidents", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Database connection timeout"
    assert data["severity"] == "HIGH"
    assert data["status"] == "OPEN"
    assert data["resolved_at"] is None


def test_get_incident_by_id(client):
    resp = client.post(
        "/api/incidents",
        json={"title": "Memory leak in cache layer", "severity": "MEDIUM"},
    )
    inc_id = resp.json()["id"]
    resp = client.get(f"/api/incidents/{inc_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == inc_id


def test_list_incidents_returns_paginated(client):
    resp = client.get("/api/incidents")
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "items" in data


def test_update_incident_status_to_resolved(client):
    resp = client.post(
        "/api/incidents",
        json={"title": "Disk usage critical", "severity": "CRITICAL"},
    )
    inc_id = resp.json()["id"]

    resp = client.patch(f"/api/incidents/{inc_id}", json={"status": "RESOLVED"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "RESOLVED"
    assert data["resolved_at"] is not None


def test_delete_incident(client):
    resp = client.post(
        "/api/incidents", json={"title": "Temp incident", "severity": "LOW"}
    )
    inc_id = resp.json()["id"]
    resp = client.delete(f"/api/incidents/{inc_id}")
    assert resp.status_code == 204
    resp = client.get(f"/api/incidents/{inc_id}")
    assert resp.status_code == 404


def test_get_incident_not_found(client):
    resp = client.get("/api/incidents/99999")
    assert resp.status_code == 404


def test_create_incident_invalid_severity(client):
    resp = client.post(
        "/api/incidents",
        json={"title": "Test", "severity": "VERY_HIGH"},
    )
    assert resp.status_code == 422


def test_filter_incidents_by_severity(client):
    client.post(
        "/api/incidents",
        json={"title": "Critical incident", "severity": "CRITICAL"},
    )
    resp = client.get("/api/incidents?severity=CRITICAL")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert all(i["severity"] == "CRITICAL" for i in items)


# ── Stats ──────────────────────────────────────────────────────────────────


def test_stats_returns_correct_structure(client):
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "deployments" in data
    assert "incidents" in data
    assert "total" in data["deployments"]
    assert "total" in data["incidents"]
    assert data["deployments"]["total"] >= 0
    assert data["incidents"]["total"] >= 0


def test_stats_reflect_created_records(client):
    before = client.get("/api/stats").json()
    client.post(
        "/api/deployments",
        json={"service_name": "stats-test-svc", "version": "v1", "status": "SUCCESS"},
    )
    after = client.get("/api/stats").json()
    assert after["deployments"]["total"] == before["deployments"]["total"] + 1
    assert after["deployments"]["success"] == before["deployments"].get("success", 0) + 1


# ── Environments ───────────────────────────────────────────────────────────


def test_create_and_list_environments(client):
    resp = client.post(
        "/api/environments",
        json={"name": "production", "description": "Live production environment"},
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "production"

    resp = client.get("/api/environments")
    assert resp.status_code == 200
    names = [e["name"] for e in resp.json()]
    assert "production" in names


def test_metrics_endpoint_returns_prometheus_format(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "http_requests_total" in resp.text or "http_request" in resp.text
