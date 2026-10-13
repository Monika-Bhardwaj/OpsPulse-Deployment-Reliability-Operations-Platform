# OpsPulse — Final Capstone Presentation & Demo Walkthrough Script

**Presenter:** Monika Bhardwaj  
**Duration:** 8–10 Minutes  
**Target Audience:** DevOps Evaluators, Engineering Leadership, SRE Leads  

---

## Part 1: Presentation Deck Walkthrough (0:00 – 3:30)

### [0:00 - 0:45] Slide 1 & 2: Introduction & Project Overview
> *"Hello everyone! My name is Monika Bhardwaj, and today I am excited to present **OpsPulse** — a production-grade DevSecOps platform and reliability engineering capstone.*
>
> *In modern engineering environments, deployment visibility and incident response are often fragmented across multiple disparate tools. OpsPulse solves this by providing a unified operational ledger: tracking multi-environment releases, service health indicators, and incident remediation metrics like MTTR in real-time.*
>
> *More than just an application, OpsPulse demonstrates a complete, battle-tested DevSecOps lifecycle: moving from clean code to containerization, passing automated security gates, provisioning cloud infrastructure with Terraform, and deploying onto a monitored Kubernetes cluster via GitOps."*

### [0:45 - 1:30] Slide 3 & 4: Tech Stack & System Architecture
> *"Let's examine our technology stack and architecture.*
>
> *On the frontend, we built a modern React 18 single-page application served via an unprivileged Nginx Alpine container.*
> *The backend is powered by Python 3.12 and FastAPI, using SQLAlchemy 2.0 with PostgreSQL 16, versioned with Alembic migrations.*
>
> *Looking at our system architecture diagram on Slide 4:*
> *External user traffic arrives at the AWS Application Load Balancer and is routed via the Nginx Ingress Controller. Ingress routes requests with the `/api` or `/health` prefix to our backend pods, and all other traffic to our frontend pods.*
> *Both backend and frontend run with 2 replicas in private subnets, running strictly as non-root users with UID 10001 for least-privilege security.*
> *Prometheus scrapes `/metrics` from our backend pods every 15 seconds, and Grafana visualizes the four Golden Signals in real time."*

### [1:30 - 2:30] Slide 5, 6 & 7: Quality Gates, DevSecOps & CI/CD
> *"Quality and security are shifted left from the very first commit.*
>
> *Quality Gate 1 is our Pytest suite: 24 comprehensive unit and integration tests covering health checks, deployment CRUD, incident lifecycle transitions, query pagination, and OpenMetrics formatting. Tests execute against an isolated in-memory test database.*
>
> *Quality Gate 2 is our DevSecOps security scan: In GitHub Actions, before any Docker image is published, Aquasecurity Trivy scans both backend and frontend images. The pipeline is configured with `--exit-code 1` on HIGH and CRITICAL vulnerabilities, immediately stopping any build with unfixed security defects.*
>
> *Once tests and Trivy pass, our pipeline publishes immutable Docker images tagged with the Git commit SHA to GitHub Container Registry (GHCR), followed by automated deployment verification on an ephemeral Kubernetes KinD cluster."*

### [2:30 - 3:30] Slide 8, 9 & 10: Infrastructure as Code, Kubernetes & Observability
> *"On the infrastructure side, our `terraform/` directory defines a complete AWS VPC and Amazon EKS 1.31 cluster across two availability zones with public and private subnets, NAT gateways, and managed worker node groups. Configuration is validated, formatted, and strictly separated with `terraform.tfvars.example` to ensure no credentials ever touch version control.*
>
> *Our workloads are packaged into an enterprise Helm chart in `helm/opspulse/`, featuring Horizontal Pod Autoscaling, resource requests and limits, and ArgoCD GitOps integration for continuous reconciliation.*
>
> *Finally, observability is built-in: our custom Grafana dashboard visualizes Service Health, Total Request Rate, p95 Latency, and 5xx Error Rates."*

---

## Part 2: Live Technical Demonstration (3:30 – 8:30)

### [3:30 - 4:15] Demo 1: Codebase Tour & Domain Architecture
- **Terminal/IDE View:** Show the repository root structure.
- **Key Files Highlighted:**
  - `backend/app/main.py`: FastAPI routes, Prometheus instrumentation.
  - `backend/app/models.py`: SQLAlchemy ORM models (`Deployment`, `Incident`, `Environment`).
  - `backend/alembic/versions/`: Database migration versioning.
  - `frontend/src/main.jsx`: React components and state management.
  - `backend/Dockerfile` & `frontend/Dockerfile`: Non-root `USER 10001` and multi-stage builds.

### [4:15 - 5:15] Demo 2: CI/CD Pipeline & Trivy DevSecOps Gate
- **Action:** Show `.github/workflows/ci-cd.yml` in action.
- **Walkthrough:**
  1. Trigger test run (`pytest tests/test_api.py -v`). Show 24 passed tests.
  2. Show Trivy scanning step blocking HIGH/CRITICAL CVEs.
  3. Show successful GHCR publication with commit SHA tag.
  4. Show automated KinD cluster testing in CI.

### [5:15 - 6:00] Demo 3: Terraform Infrastructure as Code
- **Terminal Commands:**
  ```bash
  cd terraform
  terraform init
  terraform validate
  terraform plan
  ```
- **Explanation:**
  - Walk through the planned resources: VPC, 2 public subnets, 2 private subnets, NAT gateway, EKS cluster, managed worker node group.
  - Highlight the clean variable validation and absence of hardcoded secrets.

### [6:00 - 6:45] Demo 4: ArgoCD GitOps & Kubernetes Deployment
- **Commands:**
  ```bash
  kubectl get pods -n opspulse
  kubectl get svc -n opspulse
  kubectl get ingress -n opspulse
  ```
- **Observations:**
  - Show 2 backend pods and 2 frontend pods in `Running` state.
  - Show ClusterIP services correctly routing ports.
  - Show ArgoCD application synced and healthy.

### [6:45 - 7:30] Demo 5: Live Application Walkthrough
- **Browser View (`http://localhost:3000`):**
  - **KPI Header:** Total Deployments, Active Deployments, Open Incidents, Average MTTR.
  - **Create Deployment:** Create `payment-service` version `v2.4.0` in `Production`. Transition status from `PENDING` to `SUCCESS`.
  - **Create Incident:** Log a `HIGH` severity incident: `Elevated checkout latency`. Update owner and resolve to calculate MTTR.
  - Show responsive UI, status badges, and smooth state updates.

### [7:30 - 8:15] Demo 6: Observability (Prometheus & Grafana)
- **Browser/Terminal View:**
  - Execute `curl http://localhost:8000/metrics` to show live Prometheus metrics.
  - Run `scripts/load-test.sh` to generate 500 synthetic requests.
  - Switch to Grafana dashboard (`http://localhost:3000` / Prometheus port):
    - Show Service Status: `UP`.
    - Show Request Rate spiking with synthetic traffic.
    - Show p95 Latency under 25ms.
    - Show 0% 5xx error rate.

---

## Part 3: Conclusion & Key Learnings (8:15 – 9:00)

> *"In summary, OpsPulse delivers a complete, resilient DevSecOps ecosystem. By shifting security left with Trivy, defining reproducible cloud infrastructure with Terraform, automating delivery via GitHub Actions and ArgoCD, and tracking reliability through Prometheus and Grafana, we have built a platform that adheres to the highest standards of modern software engineering.*
>
> *Thank you very much for your time and attention! All artifacts, documentation, and source code are available in the repository."*
