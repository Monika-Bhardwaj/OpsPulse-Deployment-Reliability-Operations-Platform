# OpsPulse — Demo Evidence Checklist

Presenter: **Monika Bhardwaj**. Every file in this folder is a genuine,
locally-captured output. Nothing here is fabricated or copied from docs.

| # | Evidence | File / how to reproduce | Status |
|---|---|---|---|
| 1 | Backend tests (29 passed) | `python3 -m pytest tests/ -v` in `backend/` | ✅ verified 2026-10-14 |
| 2 | Frontend tests (5 passed) | `npm test` in `frontend/` | ✅ verified 2026-10-14 |
| 3 | `docker compose up --build` — all 3 services healthy | `docker compose ps` after `up` | ✅ verified 2026-10-14 |
| 4 | Trivy backend scan — 0 HIGH/CRITICAL (exit 0) | `trivy-backend-scan.txt` | ✅ captured 2026-10-14 |
| 5 | Trivy frontend scan — 0 HIGH/CRITICAL (exit 0) | re-run: `trivy image --severity HIGH,CRITICAL --ignore-unfixed opspulse-frontend:verify` | ✅ verified 2026-10-14 |
| 6 | Live API smoke (`/health`, `/ready`, `/api/stats`, `/metrics`) | `curl http://localhost:8000/...` with compose stack up | ✅ verified 2026-10-14 |
| 7 | Seed script (`backend/seed.py --reset` → 3 env / 3 deploys / 2 incidents) | `DATABASE_URL=... python3 seed.py --reset` | ✅ verified 2026-10-14 |
| 8 | Terraform `fmt` + `validate` | `terraform fmt -check && terraform validate` in `terraform/` | ✅ verified |
| 9 | Slide deck (11 slides) | `presentation.pptx` + `slides.pdf` + `slides/*.png` | ✅ regenerated 2026-10-14 |
| 10 | Presentation video | `presentation.mp4` | ✅ regenerated 2026-10-14 |
| 11 | GitHub Actions green run + GHCR SHA tags | `ci-green-run.txt` (run 38475891288, 3m44s, images `ghcr.io/monika-bhardwaj/opspulse-{backend,frontend}:78d5534…`) | ✅ captured 2026-10-14 |
| 12 | kind-cluster deploy: pods Running, svc, ingress, HPA, Prometheus UP, Grafana live query, ArgoCD Synced/Healthy | `kind-cluster-state.txt`, `hpa-load-test.txt` (2→6→2 replicas), `grafana-panel-query.txt`, `troubleshoot-scenario-{a,b}.txt`, `argocd-gitops.txt` | ✅ captured 2026-10-14 |
| 13 | AWS VPC/EKS console + `terraform destroy` | **BLOCKED** — no AWS credentials provided for this assignment | ❌ needs credentials |

## Files

- `trivy-backend-scan.txt` — full `trivy image` report for the hardened
  multi-stage backend image (Debian base, pip/curl removed). Gate:
  `--severity HIGH,CRITICAL --ignore-unfixed --exit-code 1` → exit 0.
