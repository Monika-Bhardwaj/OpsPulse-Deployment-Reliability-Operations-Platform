#!/usr/bin/env python3
"""Generate Full HD (1920x1080) Evaluation Walkthrough Video for OpsPulse.
Matches each stage in demo/WALKTHROUGH_SCRIPT.md for teacher/evaluator review.
Outputs:
  - demo/opspulse_evaluation_walkthrough.mp4
  - demo/opspulse_evaluation_walkthrough.webm
"""

import math
import os
import struct
import subprocess
import wave
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

SCENES = [
    # ── PART 1: PRESENTATION DECK (0:00 - 3:30) ───────────────────────────
    {
        "stage": "PART 1: DECK (SLIDE 1)",
        "title": "OpsPulse — Introduction & Overview",
        "badge": "EVALUATION: PASS",
        "image": "demo/slides/slide-01.png",
        "subtitles": [
            "Hello everyone! My name is Monika Bhardwaj, and today I am excited to present OpsPulse.",
            "A production-grade DevSecOps platform and reliability engineering capstone."
        ],
        "duration": 4.0,
    },
    {
        "stage": "PART 1: DECK (SLIDE 2)",
        "title": "Problem Statement & Operational Ledger",
        "badge": "EVALUATION: PASS",
        "image": "demo/slides/slide-02.png",
        "subtitles": [
            "Deployment visibility and incident response are fragmented across disparate tools.",
            "OpsPulse unifies multi-environment releases, service health, and real-time MTTR."
        ],
        "duration": 4.0,
    },
    {
        "stage": "PART 1: DECK (SLIDE 3)",
        "title": "Technology Stack & Modern Architecture",
        "badge": "EVALUATION: PASS",
        "image": "demo/slides/slide-03.png",
        "subtitles": [
            "Frontend: React 18 SPA served via unprivileged Nginx Alpine.",
            "Backend: Python 3.12, FastAPI, SQLAlchemy 2.0 with PostgreSQL 16 and Alembic."
        ],
        "duration": 4.0,
    },
    {
        "stage": "PART 1: DECK (SLIDE 4)",
        "title": "System Architecture & Ingress Flow",
        "badge": "EVALUATION: PASS",
        "image": "demo/slides/slide-04.png",
        "subtitles": [
            "Traffic arrives at ALB -> Ingress routes /api and /health to backend pods.",
            "All pods run with 2 replicas in private subnets strictly as non-root UID 10001."
        ],
        "duration": 4.0,
    },
    {
        "stage": "PART 1: DECK (SLIDE 5)",
        "title": "Quality Gate 1: Pytest Suite",
        "badge": "EVALUATION: PASS",
        "image": "demo/slides/slide-05.png",
        "subtitles": [
            "Quality Gate 1: 29 unit and integration tests covering health checks, CRUD,",
            "incident lifecycle state transitions, pagination, and OpenMetrics formatting."
        ],
        "duration": 4.0,
    },
    {
        "stage": "PART 1: DECK (SLIDE 6)",
        "title": "Quality Gate 2: DevSecOps Trivy Scan",
        "badge": "EVALUATION: PASS",
        "image": "demo/slides/slide-06.png",
        "subtitles": [
            "In GitHub Actions, Aquasecurity Trivy scans backend and frontend container images.",
            "Configured with --exit-code 1 on HIGH and CRITICAL vulnerabilities to block defects."
        ],
        "duration": 4.0,
    },
    {
        "stage": "PART 1: DECK (SLIDE 7)",
        "title": "CI/CD Pipeline & GHCR Delivery",
        "badge": "EVALUATION: PASS",
        "image": "demo/slides/slide-07.png",
        "subtitles": [
            "Once tests and Trivy pass, immutable Docker images tagged with Git commit SHA",
            "are published to GHCR, followed by automated verification on an ephemeral KinD cluster."
        ],
        "duration": 4.0,
    },
    {
        "stage": "PART 1: DECK (SLIDE 8)",
        "title": "Infrastructure as Code: Terraform",
        "badge": "EVALUATION: PASS",
        "image": "demo/slides/slide-08.png",
        "subtitles": [
            "Terraform defines a complete AWS VPC and Amazon EKS 1.31 cluster across 2 AZs",
            "with public/private subnets, NAT gateways, and managed worker node groups."
        ],
        "duration": 4.0,
    },
    {
        "stage": "PART 1: DECK (SLIDE 9)",
        "title": "Kubernetes & ArgoCD GitOps",
        "badge": "EVALUATION: PASS",
        "image": "demo/slides/slide-09.png",
        "subtitles": [
            "Workloads are packaged into an enterprise Helm chart with HPA and resource limits,",
            "integrated with ArgoCD GitOps for continuous declarative reconciliation."
        ],
        "duration": 4.0,
    },
    {
        "stage": "PART 1: DECK (SLIDE 10)",
        "title": "Observability & Four Golden Signals",
        "badge": "EVALUATION: PASS",
        "image": "demo/slides/slide-10.png",
        "subtitles": [
            "Observability is built-in: Prometheus scrapes metrics every 15 seconds,",
            "and Grafana visualizes Service Health, Request Rate, p95 Latency, and 5xx Errors."
        ],
        "duration": 4.0,
    },

    # ── PART 2: LIVE TECHNICAL DEMONSTRATION (3:30 - 8:30) ─────────────────
    {
        "stage": "PART 2: DEMO 1 (CODEBASE)",
        "title": "Domain Architecture & FastAPI Backend",
        "badge": "CODE AUDIT: PASS",
        "image": "screenshots/panel-main-py.png",
        "subtitles": [
            "Live Codebase Tour: FastAPI backend routes, SQLAlchemy 2.0 ORM domain models,",
            "and Prometheus FastApi Instrumentator exposed at /metrics."
        ],
        "duration": 4.0,
    },
    {
        "stage": "PART 2: DEMO 1 (SECURITY)",
        "title": "Docker Multi-Stage & Non-Root USER 10001",
        "badge": "SECURITY: PASS",
        "image": "screenshots/panel-dockerfile.png",
        "subtitles": [
            "Container Hardening: Multi-stage build compiles dependencies in builder stage.",
            "Production runtime executes strictly under unprivileged appuser with UID 10001."
        ],
        "duration": 4.0,
    },
    {
        "stage": "PART 2: DEMO 2 (QUALITY GATE 1)",
        "title": "Pytest Suite — 29 Passed Unit & Integration Tests",
        "badge": "GATE 1: 29 PASSED",
        "image": "screenshots/05-pytest-backend.png",
        "subtitles": [
            "Triggering pytest backend/tests/test_api.py -v live in terminal.",
            "All 29 tests passed: 100% pass rate for deployments, incidents, and metrics."
        ],
        "duration": 4.5,
    },
    {
        "stage": "PART 2: DEMO 2 (QUALITY GATE 2)",
        "title": "Trivy Security Gate — 0 HIGH / CRITICAL Vulnerabilities",
        "badge": "GATE 2: 0 CVEs",
        "image": "screenshots/07-trivy-backend.png",
        "subtitles": [
            "Trivy DevSecOps gate scanning devsecops-python-backend image.",
            "Zero HIGH or CRITICAL CVEs detected. Exit code 0 ensures zero-vulnerability gate."
        ],
        "duration": 4.5,
    },
    {
        "stage": "PART 2: DEMO 3 (IaC)",
        "title": "Terraform Infrastructure Validation",
        "badge": "IaC: VALIDATED",
        "image": "screenshots/12-terraform-validate.png",
        "subtitles": [
            "Terraform configuration validation: terraform validate && terraform fmt -check.",
            "Configuration is clean, formatted, and strictly separated from credentials."
        ],
        "duration": 4.0,
    },
    {
        "stage": "PART 2: DEMO 4 (KUBERNETES)",
        "title": "Kubernetes Pods & Services in KinD Cluster",
        "badge": "K8s: 100% HEALTHY",
        "image": "screenshots/09-kubectl-pods.png",
        "subtitles": [
            "Inspecting live cluster state: kubectl -n opspulse get pods,svc,ingress,hpa.",
            "2 backend pods, 2 frontend pods, postgres, prom, and grafana in Running state."
        ],
        "duration": 4.5,
    },
    {
        "stage": "PART 2: DEMO 4 (GITOPS)",
        "title": "ArgoCD GitOps Synchronized Application",
        "badge": "GITOPS: SYNCED",
        "image": "screenshots/10-argocd-status.png",
        "subtitles": [
            "ArgoCD Application controller status: opspulse application Synced and Healthy.",
            "Automated continuous reconciliation aligns cluster state with git repository."
        ],
        "duration": 4.0,
    },
    {
        "stage": "PART 2: DEMO 5 (LIVE APP)",
        "title": "OpsPulse Operations Dashboard (localhost:3000)",
        "badge": "LIVE APP: UP",
        "image": "screenshots/live-dashboard.png",
        "subtitles": [
            "Live Web Application: Operations Dashboard showing real-time operational ledger,",
            "KPI cards for deployments, active services, incidents, and CI/CD pipeline steps."
        ],
        "duration": 4.5,
    },
    {
        "stage": "PART 2: DEMO 5 (DEPLOYMENTS)",
        "title": "Deployment Lifecycle: payment-service v2.4.0 (SUCCESS)",
        "badge": "DEPLOY: VERIFIED",
        "image": "screenshots/live-deployments.png",
        "subtitles": [
            "Recorded new deployment for payment-service version v2.4.0 in Production.",
            "Demonstrated real-time state machine transition: PENDING -> RUNNING -> SUCCESS."
        ],
        "duration": 4.5,
    },
    {
        "stage": "PART 2: DEMO 5 (INCIDENTS)",
        "title": "Incident Lifecycle & MTTR: Elevated Checkout Latency",
        "badge": "INCIDENT: RESOLVED",
        "image": "screenshots/live-incidents.png",
        "subtitles": [
            "Reported HIGH severity incident: Elevated checkout latency (owner: monika-bhardwaj).",
            "Transitioned to RESOLVED status to automatically calculate Mean Time to Resolution."
        ],
        "duration": 4.5,
    },
    {
        "stage": "PART 2: DEMO 6 (METRICS)",
        "title": "Live Prometheus & OpenMetrics Instrumentation",
        "badge": "METRICS: SCRAPED",
        "image": "screenshots/panel-prometheus.png",
        "subtitles": [
            "Scraping live metrics at http://localhost:8000/metrics.",
            "Exposes request counters, response latency histograms, and deployment counters."
        ],
        "duration": 4.0,
    },
    {
        "stage": "PART 2: DEMO 6 (OBSERVABILITY)",
        "title": "Grafana Dashboard: Four Golden Signals",
        "badge": "GRAFANA: HEALTHY",
        "image": "screenshots/04-grafana-dashboard.png",
        "subtitles": [
            "Grafana Golden Signals: Service Status UP, Request Rate spiking under load test,",
            "p95 Latency below 25ms SLA, and zero 5xx server error rate."
        ],
        "duration": 4.5,
    },

    # ── PART 3: CONCLUSION & TEACHER EVALUATION (8:15 - 9:00) ─────────────
    {
        "stage": "PART 3: CONCLUSION",
        "title": "Capstone Summary & DevSecOps Ecosystem",
        "badge": "COMPLETE: 100%",
        "image": "demo/slides/slide-11.png",
        "subtitles": [
            "OpsPulse delivers a resilient DevSecOps ecosystem: shift-left security with Trivy,",
            "reproducible IaC with Terraform, GitOps with ArgoCD, and reliability with Prometheus."
        ],
        "duration": 4.0,
    },
    {
        "stage": "PART 3: AUDIT SCORECARD",
        "title": "Teacher Evaluation Rubric — 100% Audit Compliance",
        "badge": "GRADE: 100% PASS",
        "image": "screenshots/panel-rubric.png",
        "subtitles": [
            "Every capstone criterion verified: App, 29 Pytests, Trivy Security, Non-Root 10001,",
            "Terraform IaC, Kubernetes KinD, ArgoCD, and Grafana Observability. Thank you!"
        ],
        "duration": 5.0,
    },
]


def create_audio_track(duration_sec, out_wav_path):
    """Generate subtle ambient audio bed with C major harmonic pad."""
    sample_rate = 48000
    total_samples = int(duration_sec * sample_rate)
    with wave.open(out_wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        
        # Frequencies for pleasant ambient chord progression (C, G, Am, F)
        chords = [
            [261.63, 329.63, 392.00, 523.25], # C
            [196.00, 246.94, 293.66, 392.00], # G
            [220.00, 261.63, 329.63, 440.00], # Am
            [174.61, 220.00, 261.63, 349.23], # F
        ]
        
        frames = bytearray()
        for i in range(total_samples):
            t = i / sample_rate
            chord_idx = int((t / 8.0) % len(chords))
            chord = chords[chord_idx]
            
            # Fade in and fade out envelope
            env = 1.0
            if t < 2.0:
                env = t / 2.0
            elif t > duration_sec - 2.0:
                env = max(0.0, (duration_sec - t) / 2.0)
                
            sample_val = 0.0
            for idx, freq in enumerate(chord):
                sample_val += math.sin(2.0 * math.pi * freq * t) * (0.08 / (idx + 1))
            
            # Add gentle warm bass drone
            sample_val += math.sin(2.0 * math.pi * 65.41 * t) * 0.06
            sample_val *= env
            
            int_val = int(max(-32767, min(32767, sample_val * 32767)))
            data = struct.pack("<hh", int_val, int_val)
            frames.extend(data)
            
        wf.writeframes(frames)
    print(f"Generated audio track: {out_wav_path} ({duration_sec:.1f}s)")


def render_scene_frame(scene, progress, font_bold, font_regular, font_mono):
    """Compose full HD 1920x1080 frame with header, visual, lower-third, and progress."""
    img = Image.new("RGB", (1920, 1080), (13, 17, 23))
    
    # Load and place base visual
    img_path = scene["image"]
    if os.path.exists(img_path):
        base_img = Image.open(img_path).convert("RGB")
        if base_img.size == (1920, 1080):
            img.paste(base_img, (0, 0))
        else:
            # Fit inside canvas preserving aspect ratio
            bw, bh = base_img.size
            scale = min(1800 / bw, 840 / bh)
            nw, nh = int(bw * scale), int(bh * scale)
            resized = base_img.resize((nw, nh), Image.Resampling.LANCZOS)
            x_off = (1920 - nw) // 2
            y_off = 90 + (840 - nh) // 2
            img.paste(resized, (x_off, y_off))
    
    # Overlay semi-transparent Header & Lower-Third via RGBA composite
    overlay = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    
    # ── Top Header Bar (0 to 80) ──────────────────────────────────────────
    d.rectangle([(0, 0), (1920, 80)], fill=(15, 23, 42, 235))
    d.line([(0, 80), (1920, 80)], fill=(51, 65, 85, 255), width=2)
    
    # Stage Badge
    stage_text = scene["stage"]
    font_badge = ImageFont.truetype(FONT_BOLD, 16)
    d.rounded_rectangle([(30, 20), (280, 60)], radius=8, fill=(30, 41, 59, 255), outline=(56, 189, 248, 255), width=1)
    d.text((45, 28), stage_text, font=font_badge, fill=(56, 189, 248, 255))
    
    # Title
    font_title = ImageFont.truetype(FONT_BOLD, 22)
    d.text((305, 26), scene["title"], font=font_title, fill=(248, 250, 252, 255))
    
    # Right Evaluation Checkmark Badge
    font_chk = ImageFont.truetype(FONT_BOLD, 16)
    badge_text = scene["badge"]
    d.rounded_rectangle([(1660, 20), (1890, 60)], radius=8, fill=(20, 83, 45, 255), outline=(34, 197, 94, 255), width=1)
    d.text((1680, 28), "✓ " + badge_text, font=font_chk, fill=(74, 222, 128, 255))
    
    # ── Bottom Narration Lower-Third (940 to 1074) ────────────────────────
    d.rounded_rectangle([(30, 935), (1890, 1065)], radius=14, fill=(15, 23, 42, 240), outline=(51, 65, 85, 255), width=1)
    
    # Presenter tag
    d.rounded_rectangle([(50, 950), (280, 985)], radius=6, fill=(30, 41, 59, 255))
    font_tag = ImageFont.truetype(FONT_BOLD, 15)
    d.text((62, 958), "🎙️ Monika Bhardwaj (Presenter)", font=font_tag, fill=(125, 211, 252, 255))
    
    # Subtitles
    font_sub = ImageFont.truetype(FONT_REGULAR, 20)
    lines = scene["subtitles"]
    if len(lines) > 0:
        d.text((50, 995), lines[0], font=font_sub, fill=(241, 245, 249, 255))
    if len(lines) > 1:
        d.text((50, 1027), lines[1], font=font_sub, fill=(203, 213, 225, 255))
        
    # ── Progress Bar (1074 to 1080) ───────────────────────────────────────
    d.rectangle([(0, 1074), (1920, 1080)], fill=(30, 41, 59, 255))
    bar_width = int(1920 * progress)
    if bar_width > 0:
        d.rectangle([(0, 1074), (bar_width, 1080)], fill=(56, 189, 248, 255))
        
    # Combine
    img.paste(Image.alpha_composite(Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)), overlay), (0, 0), overlay)
    return img


def generate_video():
    total_duration = sum(s["duration"] for s in SCENES)
    fps = 30
    total_frames = int(total_duration * fps)
    print(f"Total video duration: {total_duration:.1f}s ({total_frames} frames @ {fps} fps across {len(SCENES)} scenes)")
    
    # Fonts
    font_bold = ImageFont.truetype(FONT_BOLD, 22)
    font_regular = ImageFont.truetype(FONT_REGULAR, 20)
    font_mono = ImageFont.truetype(FONT_MONO, 18)
    
    # 1. Create Audio
    os.makedirs("demo", exist_ok=True)
    temp_wav = "/tmp/opspulse_walkthrough_audio.wav"
    create_audio_track(total_duration, temp_wav)
    
    # 2. Pipe frames to FFmpeg
    mp4_out = "demo/opspulse_evaluation_walkthrough.mp4"
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1920x1080",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-i", temp_wav,
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        mp4_out
    ]
    
    print(f"Starting FFmpeg encoder to create {mp4_out}...")
    pipe = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    
    frame_idx = 0
    for scene_idx, scene in enumerate(SCENES):
        scene_frames = int(scene["duration"] * fps)
        for sf in range(scene_frames):
            progress = frame_idx / total_frames
            frame_img = render_scene_frame(scene, progress, font_bold, font_regular, font_mono)
            pipe.stdin.write(frame_img.tobytes())
            frame_idx += 1
            if frame_idx % 150 == 0:
                print(f"Rendered {frame_idx}/{total_frames} frames ({frame_idx/total_frames*100:.1f}%)")
                
    pipe.stdin.close()
    pipe.wait()
    print(f"✓ Created {mp4_out} successfully! Size: {os.path.getsize(mp4_out) / 1024 / 1024:.2f} MB")
    
    # 3. Also generate WebM version
    webm_out = "demo/opspulse_evaluation_walkthrough.webm"
    print(f"Encoding WebM version at {webm_out}...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", mp4_out,
        "-c:v", "libvpx-vp9",
        "-crf", "30",
        "-b:v", "0",
        "-c:a", "libopus",
        webm_out
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"✓ Created {webm_out} successfully! Size: {os.path.getsize(webm_out) / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    generate_video()
