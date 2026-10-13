"""Seed the OpsPulse development database with reproducible sample data.

Explicit dev-only helper — never runs automatically. Production data is
managed exclusively through Alembic migrations.

Usage (from the backend/ directory, with the dev stack running):
    DATABASE_URL='postgresql+psycopg://opspulse:opspulse@localhost:5432/opspulse' \\
        python3 seed.py [--reset]

--reset truncates OpsPulse tables before inserting sample rows.
"""

import argparse
import sys

sys.path.insert(0, ".")

from sqlalchemy import delete

from app.db import Base, SessionLocal, engine
from app.models import Deployment, Environment, Incident

SAMPLE_ENVIRONMENTS = [
    {"name": "development", "description": "Local developer sandbox"},
    {"name": "staging", "description": "Pre-production verification"},
    {"name": "production", "description": "Customer-facing workloads"},
]

SAMPLE_DEPLOYMENTS = [
    {
        "service_name": "auth-service",
        "version": "v1.4.0",
        "status": "SUCCESS",
        "deployed_by": "release-bot",
        "notes": "Sample operational data for local demo only",
    },
    {
        "service_name": "payments-api",
        "version": "v2.1.0",
        "status": "RUNNING",
        "deployed_by": "release-bot",
        "notes": "Sample operational data for local demo only",
    },
    {
        "service_name": "search-indexer",
        "version": "v0.9.3",
        "status": "FAILED",
        "deployed_by": "release-bot",
        "notes": "Sample operational data for local demo only",
    },
]

SAMPLE_INCIDENTS = [
    {
        "title": "Elevated p99 latency on search-indexer",
        "description": "Sample incident for local demo only",
        "severity": "HIGH",
        "status": "INVESTIGATING",
        "affected_service": "search-indexer",
        "owner": "on-call",
    },
    {
        "title": "Stale feature flag in staging",
        "description": "Sample incident for local demo only",
        "severity": "LOW",
        "status": "OPEN",
        "affected_service": "frontend",
        "owner": "Unassigned",
    },
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed OpsPulse dev database")
    parser.add_argument("--reset", action="store_true", help="Truncate tables first")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        # Dev-only convenience: ensure tables exist so the script works
        # against a fresh database without running Alembic first.
        # Production schema changes still go through migrations.
        Base.metadata.create_all(bind=engine)
        if args.reset:
            db.execute(delete(Incident))
            db.execute(delete(Deployment))
            db.execute(delete(Environment))
            db.commit()

        for row in SAMPLE_ENVIRONMENTS:
            if not db.query(Environment).filter_by(name=row["name"]).first():
                db.add(Environment(**row))
        db.commit()

        for row in SAMPLE_DEPLOYMENTS:
            exists = (
                db.query(Deployment)
                .filter_by(service_name=row["service_name"], version=row["version"])
                .first()
            )
            if not exists:
                db.add(Deployment(**row))

        for row in SAMPLE_INCIDENTS:
            if not db.query(Incident).filter_by(title=row["title"]).first():
                db.add(Incident(**row))
        db.commit()
        print(
            f"Seeded {len(SAMPLE_ENVIRONMENTS)} environments, "
            f"{len(SAMPLE_DEPLOYMENTS)} deployments, "
            f"{len(SAMPLE_INCIDENTS)} incidents."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
