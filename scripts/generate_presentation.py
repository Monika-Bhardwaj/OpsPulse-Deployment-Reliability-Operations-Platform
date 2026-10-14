"""Regenerate demo/presentation.pptx and demo/slides.pdf from one source.

Uses only standard PowerPoint layouts (Title Slide / Title and Content)
with real placeholders so the deck renders in every viewer
(PowerPoint, Google Slides, LibreOffice, Keynote, mobile apps).

Usage:  python3 scripts/generate_presentation.py   (run from repo root)
"""

import os

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

REPO_URL = "https://github.com/Monika-Bhardwaj/OpsPulse-Deployment-Reliability-Operations-Platform"

TITLE_BG = RGBColor(0x0F, 0x2A, 0x44)      # deep navy title band
TITLE_FG = RGBColor(0xFF, 0xFF, 0xFF)
ACCENT = RGBColor(0x1B, 0x6E, 0xC3)        # heading blue
BODY_FG = RGBColor(0x22, 0x22, 0x22)

SLIDES = [
    {
        "layout": "title",
        "title": "OPSPULSE",
        "subtitle": "Production-Grade DevSecOps Platform & Reliability Capstone",
        "body": [
            "Presenter: Monika Bhardwaj  |  Session 21 DevOps Final Capstone",
            "Deployment & Reliability Operations Platform",
            "Automated CI/CD - Trivy Gates - Terraform AWS EKS - Helm & GitOps - Observability",
            REPO_URL,
        ],
    },
    {
        "title": "Project Overview & Purpose",
        "body": [
            "Centralized tracking of cloud deployments, incidents, and service health in real time.",
            "Solves visibility silos across microservices and multi-environment infrastructure.",
            "Full delivery lifecycle: code to cloud through an automated, secure pipeline.",
            "Deployment ledger with status transitions (PENDING > RUNNING > SUCCESS / FAILED).",
            "Severity-ranked incident management with MTTR tracking.",
        ],
    },
    {
        "title": "Technology Stack",
        "body": [
            "Frontend: React 18 + Vite, Nginx runtime, responsive CSS dashboard.",
            "Backend: Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic V2.",
            "Database: PostgreSQL 16 (psycopg3 pooling); SQLite for isolated tests.",
            "Containers: multi-stage Dockerfiles, non-root UID 10001, GHCR registry.",
            "IaC: Terraform (VPC + EKS 1.31, ap-south-1) - K8s: Helm, Ingress, HPA, ArgoCD.",
            "Observability: Prometheus /metrics + Grafana dashboard - CI: GitHub Actions + Trivy.",
        ],
    },
    {
        "title": "System Architecture",
        "body": [
            "Browsers > AWS Load Balancer > Nginx Ingress Controller.",
            "Path / serves the React frontend (2 replicas, port 8080).",
            "Paths /api, /health, /metrics route to the FastAPI backend (2 replicas, port 8000).",
            "Backend persists to PostgreSQL 16 (classroom: in-cluster PVC; prod: Amazon RDS).",
            "Prometheus scrapes /metrics; Grafana visualizes rate, latency, errors.",
            "HPA scales 2-6 replicas at 60% CPU; ArgoCD reconciles Git desired state.",
        ],
    },
    {
        "title": "Testing & CI/CD Pipeline",
        "body": [
            "29 backend pytest tests (health, CRUD incl. PUT/PATCH, validation, 404s, pagination, stats, metrics) - all passing.",
            "5 frontend smoke tests + production Vite build in the pipeline test job.",
            "Failed tests block image build, scan, and publish - quality gate enforced.",
            "Docker Buildx builds both images tagged with the Git commit SHA (traceable).",
            "Deploy job verifies the release on an ephemeral Kubernetes cluster.",
        ],
    },
    {
        "title": "DevSecOps: Trivy Security Gates",
        "body": [
            "Both images scanned with Trivy on every build: --severity HIGH,CRITICAL --exit-code 1.",
            "Verified clean scan: 0 HIGH/CRITICAL findings (evidence in demo/evidence/).",
            "Hardening: multi-stage builds, pip/curl removed from backend runtime, apk/apt upgrades.",
            "Non-root UID 10001, K8s securityContext, resource limits, no committed secrets.",
            "Pinned action SHAs, least-privilege GITHUB_TOKEN, SHA tags (never mutable latest for deploys).",
        ],
    },
    {
        "title": "Terraform: AWS VPC + EKS",
        "body": [
            "Region ap-south-1; terraform fmt + validate pass; remote-state-safe layout.",
            "VPC 10.20.0.0/16: 2 public subnets (load balancers) + 2 private subnets (nodes).",
            "EKS 1.31 with managed node group (t3.medium, min 2 / max 4 / desired 2).",
            "terraform.tfvars.example ships with zero secrets; state files git-ignored.",
            "Cost estimate ~$70-120/mo for demo period; documented destroy checklist.",
            "BLOCKED without credentials: apply/destroy + console evidence need AWS keys.",
        ],
    },
    {
        "title": "Kubernetes, Helm & GitOps",
        "body": [
            "Helm chart helm/opspulse: lint-clean, renders 11 resources (deployments, services, ingress, HPA, postgres, secret, PVC).",
            "2 replicas each; ClusterIP services; ingress routes / to frontend and /api to backend.",
            "HPA proven live on kind: 2 > 6 replicas under load, scaled back to 2 after.",
            "ArgoCD Application proven Synced + Healthy; auto-detects Git commits.",
            "Real fixes from live runs: BACKEND_HOST env (nginx portability), wait-for-db initContainer, HPA ignoreDifferences.",
        ],
    },
    {
        "title": "Observability: Prometheus + Grafana",
        "body": [
            "Backend exposes Prometheus metrics at /metrics (requests, latency histogram, status codes).",
            "Prometheus target verified UP, scraping the backend service every 10s.",
            "Grafana provisioned with Prometheus datasource + 8-panel reliability dashboard.",
            "Panel query sum(rate(http_requests_total[5m])) verified returning live req/s data.",
            "Dashboard JSON committed at monitoring/grafana-dashboard.json (reproducible import).",
        ],
    },
    {
        "title": "Troubleshooting Exercises",
        "body": [
            "Scenario A (ImagePullBackOff): invalid image reference, diagnosed via pod events.",
            "Scenario B (selector mismatch): service with zero endpoints, fixed via label alignment.",
            "Both executed live in an isolated namespace with captured evidence.",
            "Bonus real incidents debugged: nginx upstream DNS crash, helm/ArgoCD ingress conflict.",
            "Runbooks in troubleshooting/ + docs for each symptom, cause, fix, verify cycle.",
        ],
    },
    {
        "title": "Verification, Limits & Learnings",
        "body": [
            "Locally verified: app, 34 tests, hardened images, compose stack, Helm, K8s, HPA, metrics, GitOps, CI green, GHCR push.",
            "Blocked (no AWS keys for this assignment): EKS provisioning + console evidence.",
            "Key learning: manifests are claims - only live cluster runs prove routing, scaling, and sync.",
            "Security is a gate, not a badge: Trivy fails the build on HIGH/CRITICAL.",
            "Submit: repo URL + this deck + demo video recorded per WALKTHROUGH_SCRIPT.md.",
        ],
    },
]


def build_pptx(path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    for idx, slide in enumerate(SLIDES):
        if idx == 0:
            s = prs.slides.add_slide(prs.slide_layouts[6])  # blank canvas
            bg = s.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(2.6))
            bg.fill.solid()
            bg.fill.fore_color.rgb = TITLE_BG
            bg.line.fill.background()
            title_box = s.shapes.add_textbox(Inches(0.7), Inches(0.35), Inches(11.9), Inches(1.1))
            tf = title_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = slide["title"]
            p.font.size = Pt(54)
            p.font.bold = True
            p.font.color.rgb = TITLE_FG
            p.alignment = PP_ALIGN.LEFT
            sub_box = s.shapes.add_textbox(Inches(0.7), Inches(1.45), Inches(11.9), Inches(0.8))
            tf = sub_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = slide["subtitle"]
            p.font.size = Pt(24)
            p.font.color.rgb = TITLE_FG
            top = Inches(3.1)
            for line in slide["body"]:
                box = s.shapes.add_textbox(Inches(0.7), top, Inches(11.9), Inches(0.75))
                tf = box.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.text = line
                p.font.size = Pt(17)
                p.font.color.rgb = BODY_FG
                top += Inches(0.78)
            continue

        s = prs.slides.add_slide(prs.slide_layouts[1])  # Title and Content
        s.shapes.title.text = f"{idx + 1}. {slide['title']}"
        for paragraph in s.shapes.title.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.color.rgb = ACCENT
        body = s.placeholders[1]
        tf = body.text_frame
        tf.word_wrap = True
        for i, line in enumerate(slide["body"]):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = line
            p.level = 0
            p.font.size = Pt(20)
            p.font.color.rgb = BODY_FG
            p.space_after = Pt(8)

    prs.save(path)
    print(f"Saved {path} ({len(prs.slides)} slides)")


def build_pdf(path):
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import ParagraphStyle

    navy = HexColor("#0F2A44")
    blue = HexColor("#1B6EC3")
    dark = HexColor("#222222")

    title_style = ParagraphStyle("Title2", fontSize=26, leading=30, textColor=blue, spaceAfter=12)
    cover_style = ParagraphStyle("Cover", fontSize=40, leading=44, textColor=navy, spaceAfter=8)
    body_style = ParagraphStyle("Body2", fontSize=13, leading=17, textColor=dark, spaceAfter=6, leftIndent=12)

    doc = SimpleDocTemplate(path, pagesize=landscape(A4),
                            leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    story = []
    for idx, slide in enumerate(SLIDES):
        if idx == 0:
            story.append(Paragraph(slide["title"], cover_style))
            story.append(Paragraph(slide["subtitle"], title_style))
        else:
            story.append(Paragraph(f"{idx + 1}. {slide['title']}", title_style))
        for line in slide["body"]:
            safe = line.replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;")
            story.append(Paragraph("&#8226;  " + safe, body_style))
        story.append(PageBreak())
    doc.build(story)
    print(f"Saved {path} ({len(SLIDES)} pages)")


if __name__ == "__main__":
    os.makedirs("demo", exist_ok=True)
    build_pptx("demo/presentation.pptx")
    build_pdf("demo/slides.pdf")
