# OpsPulse — Enterprise DevSecOps & Reliability Platform

> **Author: Monika Bhardwaj** — Session 21 DevSecOps Final Capstone submission.
> OpsPulse is my own original application domain (deployment & reliability operations),
> built on the standard DevOps toolchain. It is not a copy of any reference project.

[![CI/CD Pipeline](https://github.com/Monika-Bhardwaj/OpsPulse-Deployment-Reliability-Operations-Platform/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Monika-Bhardwaj/OpsPulse-Deployment-Reliability-Operations-Platform/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.143-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Docker Non-Root](https://img.shields.io/badge/Docker-Non--Root%20(UID%2010001)-blue.svg)](https://www.docker.com/)
[![Trivy Scanned](https://img.shields.io/badge/Security-Trivy%20Gate%20Passing-brightgreen.svg)](https://aquasecurity.github.io/trivy/)
[![Kubernetes 1.31](https://img.shields.io/badge/Kubernetes-1.31-326CE5.svg)](https://kubernetes.io/)

**OpsPulse** is a production-grade, full-stack DevSecOps and site reliability engineering platform. It provides centralized tracking of multi-environment deployments, service health indicators, incident remediation workflows (MTTR tracking), and automated quality/security gates across the entire software delivery lifecycle.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Technology Stack](#2-technology-stack)
3. [Repository Structure](#3-repository-structure)
4. [Local Development (Docker Compose)](#4-local-development-docker-compose)
5. [Automated Testing & Quality Gates](#5-automated-testing--quality-gates)
6. [Container Security & DevSecOps (Trivy)](#6-container-security--devsecops-trivy)
7. [CI/CD Pipeline (GitHub Actions & GHCR)](#7-cicd-pipeline-github-actions--ghcr)
8. [Infrastructure as Code (Terraform AWS VPC + EKS)](#8-infrastructure-as-code-terraform-aws-vpc--eks)
9. [Kubernetes Orchestration & Helm Packaging](#9-kubernetes-orchestration--helm-packaging)
10. [GitOps Continuous Delivery (ArgoCD)](#10-gitops-continuous-delivery-argocd)
11. [Observability & Monitoring (Prometheus + Grafana)](#11-observability--monitoring-prometheus--grafana)
12. [Presentation & Demo Artifacts](#12-presentation--demo-artifacts)
13. [Known Limitations & Future Roadmap](#13-known-limitations--future-roadmap)

---

## 1. Architecture Overview

OpsPulse is built as a classroom production-style system with sane defaults:

```
                           [ Internet Users / Browsers ]
                                         │
                                         ▼
                           [ AWS Application Load Balancer ]
                                         │
                                         ▼
                           [ Nginx Ingress Controller ]
                                         │
               ┌─────────────────────────┴─────────────────────────┐
               │                                                   │
        Path: / │                                   Path: /api, /health, /metrics
               ▼                                                   ▼
     [ opspulse-frontend ]                               [ opspulse-backend ]
     Nginx Alpine (UID 10001)                            FastAPI (UID 10001)
     2 Replicas, Port 8080                               2 Replicas, Port 8000
                                                                   │
                                                                   ▼
                                                         [ PostgreSQL 16 DB ]
                                                         Stateful PVC 5Gi
                                                                   ▲
                                                                   │ Scrapes /metrics
                                                         [ Prometheus Operator ]
                                                                   │
                                                                   ▼
                                                          [ Grafana Dashboard ]
```

### Key Architectural Tenets
- **Least Privilege Execution**: Both backend and frontend containers run as unprivileged user `UID 10001` (`appuser`).
- **Network Isolation**: All compute pods run in private AWS subnets behind NAT gateways, with external traffic entering strictly via ingress load balancers.
- **Stateless Tier Scalability**: Backend and frontend deployments utilize Horizontal Pod Autoscalers (HPA) targeting 60% CPU utilization.
- **Fail-Safe Self-Healing**: Kubernetes liveness and readiness probes verify process health and database connectivity before admitting traffic.

---

## 2. Technology Stack

| Layer | Component | Description |
|---|---|---|
| **Frontend** | React 18 & Vite | Single Page Application with OpsPulse design system, dark mode, and KPI counters |
| **Frontend Server** | Nginx stable-alpine | Multi-stage production container, unprivileged non-root on port 8080 |
| **Backend API** | FastAPI & Python 3.12 | Async REST API with OpenAPI documentation, Pydantic V2 validation, and CORS |
| **Database** | PostgreSQL 16 & SQLite | Relational persistence with psycopg3 connection pooling; in-memory SQLite for testing |
| **Migrations** | Alembic 1.14 | Schema version control managing tables, foreign keys, and indexes |
| **Testing** | Pytest 9.0 & Pytest-Cov | 29 test cases covering health, CRUD incl. PUT/PATCH, filtering, pagination, and metrics |
| **Security Scanning** | Aquasecurity Trivy | Automated vulnerability scanner gate with `--exit-code 1` on HIGH/CRITICAL CVEs |
| **Registry** | GitHub Container Registry | Immutable image publishing using Git commit SHA tags |
| **IaC** | HashiCorp Terraform 1.16+ | Modularized provisioning of AWS VPC (Multi-AZ) and Amazon EKS 1.31 cluster |
| **Orchestration** | Kubernetes 1.31 & Helm v3 | Declarative workload definitions, services, ingress, and auto-scaling |
| **GitOps** | ArgoCD | Declarative GitOps synchronization with automatic drift detection and self-healing |
| **Observability** | Prometheus & Grafana | OpenMetrics scraping via ServiceMonitor and real-time SRE dashboards |

---

## 3. Repository Structure

```text
OpsPulse-Deployment-Reliability-Operations-Platform/
├── backend/                  # FastAPI Application
│   ├── alembic/              # Database schema migrations
│   │   └── versions/         # Migration versions (0001_create_opspulse.py)
│   ├── app/                  # Application core
│   │   ├── config.py         # Pydantic BaseSettings environment config
│   │   ├── db.py             # SQLAlchemy session & connection pooling
│   │   ├── main.py           # FastAPI entry point, routes, /metrics instrumentation
│   │   ├── models.py         # SQLAlchemy ORM models (Deployment, Incident, Environment)
│   │   └── schemas.py        # Pydantic models for request validation & responses
│   ├── tests/                # Test suite
│   │   └── test_api.py       # 29 Pytest unit/integration tests
│   ├── Dockerfile            # Python 3.12-Alpine zero-CVE container (UID 10001)
│   ├── requirements.txt      # Pinned dependencies (incl. test deps)
│   ├── requirements-prod.txt# Runtime-only dependencies for the image build
│   ├── seed.py               # Explicit dev-data seeder (never auto-runs)
│   └── pytest.ini            # Pytest execution configuration
├── frontend/                 # React Single Page Application
│   ├── src/
│   │   ├── main.jsx          # React components: Dashboard, Deployments, Incidents, Modals
│   │   └── styles.css        # OpsPulse design system styling
│   ├── tests/                # 5 Node smoke tests (npm test)
│   ├── index.html            # HTML5 entry point with SEO metadata
│   ├── nginx.conf            # Unprivileged Nginx config (BACKEND_HOST injected at start)
│   ├── package.json          # React 18, Vite 5 pinned dependencies
│   ├── vite.config.js        # Vite build tool configuration
│   └── Dockerfile            # Multi-stage Node 22 build + Nginx stable-alpine (UID 10001)
├── docker-compose.yml        # Multi-container local stack with health checks
├── terraform/                # AWS Infrastructure as Code (VPC + EKS, ap-south-1)
├── helm/opspulse/            # Kubernetes Helm chart (deployments, services, ingress, HPA, postgres)
├── k8s/                      # Plain manifests used by the CI deploy job
├── argocd/                   # GitOps Applications (prod + kind-demo with local overrides)
├── monitoring/               # Prometheus values + 8-panel Grafana dashboard JSON
├── troubleshooting/          # Isolated broken manifests (ImagePullBackOff, selector mismatch)
├── scripts/                  # load-test.sh, generate_presentation.py
├── demo/
│   ├── presentation.pptx     # 11-slide deck (standard layouts, every viewer)
│   ├── slides.pdf            # Same deck as PDF (previews inline on GitHub)
│   ├── slides/               # One PNG per slide (always viewable)
│   ├── WALKTHROUGH_SCRIPT.md # Recording script for the demo video
│   └── evidence/             # Genuine captured outputs + checklist (README.md)
├── .github/workflows/
│   └── ci-cd.yml             # Test → build/scan/push → deploy pipeline
└── README.md                 # This file (full technical documentation)
```

---

## 4. Local Development (Docker Compose)

Spin up the full local stack with a single command:

```bash
docker compose up --build
```

### Services Started:
- **Frontend**: Available at `http://localhost:3000` (Nginx unprivileged on port 8080 mapped to 3000)
- **Backend API**: Available at `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/docs`
- **Prometheus Metrics**: `http://localhost:8000/metrics`
- **Health Check**: `http://localhost:8000/health`
- **PostgreSQL Database**: Port 5432 with health check validation (`pg_isready`)

To stop the stack and remove volumes:
```bash
docker compose down -v
```

---

## 5. Automated Testing & Quality Gates

The test suite validates application logic, schema integrity, and boundary conditions using `pytest`:

```bash
cd backend
python3 -m pytest tests/test_api.py -v
```

### Test Coverage Summary (29/29 Passed)
- **Health & Readiness**: `/health` returns `{status: "UP"}` and `/ready` verifies database query execution.
- **Deployment Lifecycle**: Create (`POST`), List (`GET`), Retrieve (`GET /{id}`), Update (`PUT /{id}`), and Delete (`DELETE /{id}`).
- **Status Constraints**: Enforces valid status transitions (`PENDING`, `RUNNING`, `SUCCESS`, `FAILED`, `CANCELLED`).
- **Incident Management**: Severity tracking (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), resolution timestamping, and MTTR calculation.
- **Pagination & Query Filtering**: Offset/limit boundaries and status query parameter filters.
- **Prometheus Exposition**: Conformance of `/metrics` output with standard OpenMetrics formats.

---

## 6. Container Security & DevSecOps (Trivy)

Security is shifted left into the build phase:

1. **Non-Root User Enforcement**:
   - Backend runs as `UID 10001` (`appuser`).
   - Frontend runs as `UID 10001` (`appuser`) with `/tmp/nginx.pid` and unprivileged port 8080 binding.
2. **Automated Vulnerability Scanning**:
   - The CI pipeline scans both container images using **Aquasecurity Trivy**.
   - Built with `--severity HIGH,CRITICAL --ignore-unfixed --exit-code 1`.
   - Any unmitigated HIGH or CRITICAL vulnerability halts the build before pushing to the registry.
   - Verified 2026-10-14: backend image (`python:3.12-alpine`, prod-only deps, pip removed)
     reports **0 vulnerabilities across ALL severities** (UNKNOWN/LOW/MEDIUM/HIGH/CRITICAL);
     frontend (`nginx:stable-alpine`) likewise **0 across all severities**.
   - Remediation history: Debian-slim base carried 44 HIGH CVEs with no upstream fix
     (util-linux/login/perl-base); eliminated by moving to Alpine + dropping test deps from the image.

```bash
# Manual scan verification
trivy image --severity HIGH,CRITICAL --ignore-unfixed opspulse-backend:test
trivy image --severity HIGH,CRITICAL --ignore-unfixed opspulse-frontend:test
```

---

## 7. CI/CD Pipeline (GitHub Actions & GHCR)

The automated pipeline (`.github/workflows/ci-cd.yml`) triggers on every push and pull request to `main`:

```text
[ Git Push to main ]
        │
        ├──> Stage 1: Test & Quality Gate
        │       ├── Setup Python 3.12 & Node.js 22
        │       ├── Run Pytest test suite (29 tests)
        │       └── Compile React production bundle (npm run build)
        │
        ├──> Stage 2: Container Build & Security Scan
        │       ├── Build Backend & Frontend Docker images
        │       ├── Scan Backend with Trivy (exit-code 1 on HIGH/CRITICAL)
        │       ├── Scan Frontend with Trivy (exit-code 1 on HIGH/CRITICAL)
        │       └── Push to GitHub Container Registry (ghcr.io) with Git SHA tag
        │
        └──> Stage 3: End-to-End Cluster Deploy (KinD in CI)
                ├── Provision ephemeral KinD Kubernetes cluster
                ├── Deploy namespace, deployments, services, ingress
                ├── Wait for readiness probes (kubectl wait)
                └── Verify live endpoints via port-forward (/health & /metrics)
```

---

## 8. Infrastructure as Code (Terraform AWS VPC + EKS)

The `terraform/` directory provisions production AWS infrastructure in `ap-south-1`:

### Provisioned Resources
- **VPC (`10.20.0.0/16`)**:
  - 2 Public Subnets (`10.20.101.0/24`, `10.20.102.0/24`) with Internet Gateway.
  - 2 Private Subnets (`10.20.1.0/24`, `10.20.2.0/24`) with single NAT Gateway for cost-effective egress.
- **Amazon EKS Cluster (v1.31)**:
  - Managed Node Group with `t3.medium` instances (min 2, max 4, desired 2).
  - OIDC identity provider integration for IAM service accounts.

### Usage:
```bash
cd terraform
terraform init
terraform fmt
terraform validate
cp terraform.tfvars.example terraform.tfvars
terraform plan
# To provision: terraform apply -auto-approve
# To tear down: terraform destroy -auto-approve
```

---

## 9. Kubernetes Orchestration & Helm Packaging

Deploy the complete application to any Kubernetes cluster using the OpsPulse Helm chart:

```bash
# Deploy to local cluster or EKS
helm upgrade --install opspulse ./helm/opspulse \
  --namespace opspulse \
  --create-namespace \
  --values ./helm/opspulse/values-prod.yaml
```

### Workload Characteristics:
- **Deployments**: 2 replicas each for frontend and backend ensuring continuous availability.
- **Horizontal Pod Autoscaling**: Automatically scales up to 6 pods when average CPU exceeds 60%.
- **Ingress Routing**: Exposes `/api` and `/health` to backend service (port 80) and `/` to frontend service (port 80).
- **Resource Management**: Explicit CPU and Memory requests and limits preventing noisy neighbor issues.

---

## 10. GitOps Continuous Delivery (ArgoCD)

OpsPulse utilizes ArgoCD to enforce declarative GitOps delivery:

- The manifest in `argocd/application.yaml` points directly to this repository's `helm/opspulse` directory.
- ArgoCD continuously monitors `main` branch changes and synchronizes cluster state automatically.
- Automatic self-healing reconciles manual out-of-band drifts back to the committed Git configuration.

```bash
kubectl apply -f argocd/application.yaml
```

---

## 11. Observability & Monitoring (Prometheus + Grafana)

The backend natively exports telemetry via the `/metrics` endpoint:

### Key Metrics Tracked:
- `http_requests_total`: Request volume partitioned by HTTP method, handler, and status code.
- `http_request_duration_seconds`: Request latency histogram buckets for p50, p95, and p99 calculation.
- `http_requests_in_progress`: Real-time concurrent in-flight request gauge.

### Monitoring Setup:
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f monitoring/prometheus-values.yaml
```

Import the custom Grafana dashboard from `monitoring/grafana-dashboard.json` to monitor real-time throughput, latency percentiles, and error spikes.

---

## 12. Presentation & Demo Artifacts

All presentation materials live in the `demo/` folder:
- 📊 **Slide Deck**: [`demo/presentation.pptx`](./demo/presentation.pptx) (11 slides, standard layouts)
- 📄 **Slides as PDF**: [`demo/slides.pdf`](./demo/slides.pdf) (previews inline on GitHub)
- 🖼️ **Slides as PNGs**: [`demo/slides/`](./demo/slides/) (one image per slide, always viewable)
- 🎙️ **Recording Script**: [`demo/WALKTHROUGH_SCRIPT.md`](./demo/WALKTHROUGH_SCRIPT.md) (step-by-step narration)
- 🎥 **Presentation Video**: record your screen while following
  [`demo/WALKTHROUGH_SCRIPT.md`](./demo/WALKTHROUGH_SCRIPT.md), then save the file as
  `demo/presentation.mp4` and commit it. The video is mandatory — do not submit without it.
- 🧾 **Evidence**: [`demo/evidence/`](./demo/evidence/) (genuine outputs + checklist)

---

## 13. Known Limitations & Future Roadmap

- **No authentication yet**: the API and UI are open by design for this classroom demo.
  Do not expose them publicly as-is; Keycloak/OAuth2 integration is the planned next step.
- **Distributed Tracing**: Metrics are fully implemented; adding OpenTelemetry Jaeger traces for database spans is on the roadmap.
- **Canary Deployments**: Argo Rollouts integration for progressive traffic shifting during releases.

---

## Verification & Rubric Coverage Matrix

Honest status per module — **IMPLEMENTED** means the code/config exists and is validated
where the environment permits; **BLOCKED** needs AWS credentials or a recorded video.

| Module | Criteria | Status |
|---|---|---|
| **M1 Application** | FastAPI `/health`, GET/POST/PUT/PATCH/DELETE endpoints, PostgreSQL + Alembic, React UI | ✅ Verified locally |
| **M2 Testing** | 29 Pytest tests + 5 frontend tests passing, isolated test DB, pytest.ini | ✅ Verified locally |
| **M3 Git/GitHub** | Public repo, descriptive commits, clean .gitignore (no secrets) | ✅ Verified |
| **M4 Docker** | Multi-stage Dockerfiles, non-root UID 10001, compose health checks | ✅ Verified locally |
| **M5 CI/CD** | GitHub Actions green, pytest gate, GHCR push with Git SHA tags | ✅ Verified (green runs) |
| **M6 DevSecOps** | Trivy gate on both images, 0 vulns at all severities | ✅ Verified |
| **M7 Terraform** | Valid HCL, VPC + EKS, `fmt`/`validate` pass, tfvars.example | ⚠️ Config verified; `apply` BLOCKED (no AWS credentials) |
| **M8 Kubernetes** | Namespace, 2 replicas, Ingress routing, Helm chart, HPA, ArgoCD | ✅ Verified on local kind cluster |
| **M9 Observability** | `/metrics`, Prometheus UP, Grafana dashboard with live data | ✅ Verified on local kind cluster |
| **M10 Documentation** | Full README, 11-slide deck (pptx/pdf/png), walkthrough script | ⚠️ Video not yet recorded — record and commit `demo/presentation.mp4` |
