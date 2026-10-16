# Screenshots — captured live on 2026-10-16

Browser shots were taken with headless Chrome against the running local stack
and kind cluster. Terminal shots were rendered from live command output by
`scripts/capture_terminal_shots.py` (re-run it any time to refresh them).

| File | What it proves |
|---|---|
| `01-frontend-dashboard.png` | OpsPulse dashboard at `localhost:3000` with live deployment/incident data |
| `02-swagger-docs.png` | FastAPI OpenAPI docs at `localhost:8000/docs` — all 20 endpoints incl. PUT |
| `03-prometheus-targets.png` | Prometheus Targets page: `opspulse-backend` **UP**, 1/1 |
| `04-grafana-dashboard.png` | Grafana dashboard with live panels (7.68 req/s, p95 95ms, 0 errors, throughput + latency graphs) |
| `05-pytest-backend.png` | `pytest`: 29 passed |
| `06-frontend-tests.png` | `npm test`: 5 passed, 0 failed |
| `07-trivy-backend.png` | Trivy backend gate: 0 HIGH/CRITICAL, exit 0 |
| `08-trivy-frontend.png` | Trivy frontend gate: 0 HIGH/CRITICAL, exit 0 |
| `09-kubectl-pods.png` | kind cluster: pods, services, ingress, HPA state |
| `10-argocd-status.png` | ArgoCD application: Synced + Healthy |
| `11-compose-status.png` | `docker compose ps`: 3/3 services healthy |
| `12-terraform-validate.png` | `terraform validate` success + `fmt` clean |

One real issue found while capturing: the Prometheus scrape target still pointed at
the pre-ArgoCD service DNS name (`opspulse-opspulse-backend…`, state DOWN after the
ArgoCD rename). Fixed by patching the `prom-config` ConfigMap to
`opspulse-kind-opspulse-backend.opspulse.svc.cluster.local:80` and restarting
Prometheus — screenshot 03 was taken after the fix shows UP.
