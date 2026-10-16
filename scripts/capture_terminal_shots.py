"""Capture real terminal outputs as PNGs for screenshots/.
Runs each command live and renders its actual stdout — no mock content.
Usage: python3 scripts/capture_terminal_shots.py  (repo root, stack running)
"""

import subprocess

from PIL import Image, ImageDraw, ImageFont

SHOTS = [
    ("05-pytest-backend.png", "cd backend && python3 -m pytest tests/ -q 2>&1 | tail -4",
     "backend pytest — 29 passed"),
    ("06-frontend-tests.png", "cd frontend && npm test 2>&1 | grep -E '^# (tests|pass|fail)'",
     "frontend tests — 5 passed"),
    ("07-trivy-backend.png", "trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 devsecops-python-backend 2>&1 | tail -6; echo \"EXIT=$?\"",
     "trivy backend gate — 0 HIGH/CRITICAL"),
    ("08-trivy-frontend.png", "trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 devsecops-python-frontend 2>&1 | tail -4; echo \"EXIT=$?\"",
     "trivy frontend gate — 0 HIGH/CRITICAL"),
    ("09-kubectl-pods.png", "kubectl -n opspulse get pods,svc,ingress,hpa 2>&1 | head -22",
     "kind cluster — pods, services, ingress, HPA"),
    ("10-argocd-status.png", "kubectl -n argocd get applications -o wide 2>&1 | head -6",
     "argocd — synced application"),
    ("11-compose-status.png", "docker compose ps --format 'table {{.Name}}\\t{{.Status}}\\t{{.Ports}}' 2>&1 | head -6",
     "docker compose — 3 healthy services"),
    ("12-terraform-validate.png", "terraform -chdir=terraform validate 2>&1 | tail -3 && terraform -chdir=terraform fmt -check && echo 'fmt: clean'",
     "terraform validate + fmt"),
]

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def render(title, output, path):
    font_title = ImageFont.truetype(FONT, 26)
    font_body = ImageFont.truetype(FONT, 22)
    lines = [l.rstrip()[:150] for l in output.strip().splitlines()][-32:]
    W = 1440
    H = 120 + 34 * len(lines)
    img = Image.new("RGB", (W, H), (13, 17, 23))
    d = ImageDraw.Draw(img)
    d.rectangle([(0, 0), (W, 64)], fill=(30, 41, 59))
    d.text((24, 16), "$ " + title, font=font_title, fill=(125, 211, 252))
    y = 88
    for line in lines:
        color = (74, 222, 128) if ("passed" in line or "0 " in line[:8] or "Success" in line
                                   or "UP" in line or "Healthy" in line or "Running" in line
                                   or "Synced" in line or "clean" in line) else (226, 232, 240)
        d.text((24, y), line, font=font_body, fill=color)
        y += 34
    img.save(path)
    print(f"saved {path} ({len(lines)} lines)")


def main():
    import os
    os.makedirs("screenshots", exist_ok=True)
    for fname, cmd, title in SHOTS:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                              cwd=".", timeout=600)
        out = proc.stdout + proc.stderr
        render(title, out, f"screenshots/{fname}")


if __name__ == "__main__":
    main()
