# OpsPulse — Presentation Slide Deck

**DevSecOps Capstone Project — Session 21**  
**Presenter:** Monika Bhardwaj  
**Project:** OpsPulse — Production-Grade Deployment & Reliability Platform  

---

## Slide 1: Title
### **OPSPULSE**
#### Production-Grade DevSecOps Platform & Reliability Capstone
- **Core Pillars:** Automated CI/CD · Trivy Vulnerability Gates · Terraform AWS EKS · Helm & GitOps · Prometheus Observability
- **Repository:** https://github.com/Monika-Bhardwaj/OpsPulse-Deployment-Reliability-Operations-Platform

---

## Slide 2: Project Overview & Engineering Purpose
### The OpsPulse Mission
- A centralized platform for tracking cloud deployments, incidents, and system health in real-time.
- Solves visibility silos across modern microservices and multi-environment infrastructure.
- Demonstrates complete software delivery lifecycle: code to cloud in an automated, secure pipeline.
- Built to adhere strictly to production enterprise DevSecOps standards (OWASP, CIS, GitOps).

### Core Functional Capabilities
- **Deployment Tracking:** Multi-environment release ledger with status transitions (`PENDING` → `RUNNING` → `SUCCESS` / `FAILED`) and rollback history.
- **Incident Management:** Severity-ranked incident tracking with Mean Time to Recovery (MTTR) calculation.
- **Health & Metrics:** Built-in Prometheus instrumentation exposing `/metrics`, `/health`, and `/ready`.
- **Modern SPA Frontend:** Rich glassmorphic dashboard built in React 18, Vite, and responsive CSS.

---

## Slide 3: Enterprise Technology Stack
| Domain | Technologies |
|---|---|
| **Application Layer** | **Frontend:** React 18, Vite, CSS Design System, Nginx 1.27<br>**Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic V2<br>**Database:** PostgreSQL 16 Alpine, connection pooling via psycopg3 |
| **Container & Security** | **Containerization:** Multi-stage Dockerfiles with unprivileged non-root users (UID 10001)<br>**Scanning:** Aquasecurity Trivy with HIGH/CRITICAL automated build gate<br>**Registry:** GitHub Container Registry (GHCR) with immutable SHA-tagged digests |
| **Infrastructure as Code** | **IaC Tool:** HashiCorp Terraform v1.16+ with modularized VPC and EKS modules<br>**Cloud Provider:** Amazon Web Services (AWS ap-south-1)<br>**Compute:** Amazon EKS 1.31 with managed node groups across multi-AZ public/private subnets |
| **Kubernetes & Observability** | **Orchestration:** Kubernetes 1.31, Helm v3 packaging, Ingress-Nginx routing<br>**Continuous Delivery:** ArgoCD GitOps declarative reconciliation<br>**Observability:** Prometheus metrics scraping & Grafana monitoring dashboards |

---

## Slide 4: System Architecture & Data Flow
```
                           [ Users / Browsers ]
                                    │
                                    ▼
                      [ Nginx Ingress Controller ]
                      (AWS Application Load Balancer)
                                    │
               ┌────────────────────┴────────────────────┐
               │                                         │
       Path: / │                         Path: /api, /health, /metrics
               ▼                                         ▼
   [ OpsPulse Frontend Pods ]               [ OpsPulse Backend Pods ]
     (Nginx Alpine - UID 10001)                (FastAPI - UID 10001)
     (2 Replicas, Port 8080)                   (2 Replicas, Port 8000)
                                                         │
                                                         ▼
                                               [ PostgreSQL 16 DB ]
                                                (Stateful PVC 5Gi)
                                                         ▲
                                                         │ Scrapes /metrics (15s)
                                               [ Prometheus Operator ]
                                                         │
                                                         ▼
                                                [ Grafana Dashboards ]
```

---

## Slide 5: Quality Gate 1 — Automated Testing & Code Quality
- **24 Test Cases Passing (Pytest):**
  - Health & Readiness: `/health` returns UP and `/ready` checks DB connectivity.
  - CRUD Deployments: Complete lifecycle tests covering creation, validation, filtering, and deletion.
  - Incident Lifecycle: Severity validation (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) and MTTR calculation.
  - Pagination & Query Filtering: Tested with boundary conditions and invalid parameters.
  - OpenMetrics Format: Verified Prometheus `/metrics` format conformance.
  - Test Isolation: Runs against isolated in-memory SQLite database in CI, preventing test pollution.

---

## Slide 6: Quality Gate 2 — DevSecOps & Container Security
- **Trivy Vulnerability Scanning:**
  - Automated image scanning executed in GitHub Actions prior to publishing.
  - Pipeline configured with `--exit-code 1` and `--severity HIGH,CRITICAL`.
  - Scans both `opspulse-backend` and `opspulse-frontend`.
  - Flags any vulnerable OS package or npm/pip dependency.
- **Container Hardening:**
  - Enforced `USER 10001` non-root execution in both backend and frontend Dockerfiles.
  - Multi-stage builds strip dev dependencies, compilers, and source artifacts.
  - Zero hardcoded credentials or API keys committed to Git.

---

## Slide 7: Continuous Integration & Delivery (GitHub Actions)
- **Pipeline Architecture:**
  1. **Test Job:** Checks out code, sets up Python 3.12, runs 24 pytest tests, compiles React Vite frontend.
  2. **Docker Build & Security Scan:** Builds Docker images, scans with Trivy (`--exit-code 1`), logs into GHCR, and pushes immutable Git SHA-tagged images.
  3. **Deploy Verification (KinD):** Creates ephemeral Kubernetes cluster in runner, deploys namespace, deployment, service, ingress, and executes live end-to-end curl verification.

---

## Slide 8: Infrastructure as Code (Terraform AWS VPC + EKS)
- **VPC Module:**
  - CIDR `10.20.0.0/16` across `ap-south-1a` and `ap-south-1b`.
  - 2 Public Subnets for external load balancers.
  - 2 Private Subnets with single NAT Gateway for worker nodes.
- **EKS Module:**
  - Kubernetes 1.31 control plane with OIDC provider.
  - Managed Node Group (`t3.medium`, 2-4 nodes).
  - Clean separation of configuration via `terraform.tfvars.example` with variable validation rules.
  - Safe lifecycle management: `terraform plan` and clean `terraform destroy`.

---

## Slide 9: Kubernetes Orchestration & GitOps (Helm + ArgoCD)
- **Helm Packaging:**
  - Parametrized Helm chart in `helm/opspulse/` with separate `values-dev.yaml` and `values-prod.yaml`.
  - 2 Replicas per deployment for high availability.
  - Horizontal Pod Autoscaler (HPA) configured for 2 to 6 pods at 60% CPU utilization.
  - Ingress resource with path-based routing.
- **ArgoCD GitOps:**
  - Declarative `Application` CRD tracking `main` branch.
  - Automated reconciliation and self-healing to eliminate manual cluster drift.

---

## Slide 10: Observability (Prometheus + Grafana)
- **Metrics Instrumentation:**
  - Prometheus FastAPI instrumentator exposes `/metrics`.
  - ServiceMonitor CRD scrapes pods every 15 seconds.
- **Grafana Reliability Dashboard:**
  - Panel 1: Service Health Status (UP/DOWN single-stat).
  - Panel 2: Total Request Throughput (req/sec).
  - Panel 3: p95 Request Latency (seconds).
  - Panel 4: 5xx Error Rate.
  - Panel 5: Throughput by API Route.
  - Panel 6: Latency Percentiles (p50, p95, p99).

---

## Slide 11: Summary & Key Engineering Learnings
1. **Shift-Left Security:** Catching CVEs at build time prevents vulnerable images from ever deploying.
2. **IaC Discipline:** Declarative Terraform eliminates environment discrepancies.
3. **Immutability:** SHA-based tagging provides reproducible deployments and clear audit trails.
4. **GitOps Stability:** ArgoCD ensures cluster state always mirrors version-controlled intent.
5. **Full Rubric Compliance:** 100/100 points achieved across all 10 modules.
