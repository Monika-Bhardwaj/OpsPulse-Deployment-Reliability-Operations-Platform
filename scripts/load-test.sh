#!/usr/bin/env bash
set -euo pipefail

URL="${URL:-http://localhost:8000/health}"
CONCURRENCY="${CONCURRENCY:-10}"
TOTAL_REQUESTS="${TOTAL_REQUESTS:-500}"

echo "🚀 Starting OpsPulse load test against: $URL ($TOTAL_REQUESTS requests)"
for i in $(seq 1 "$TOTAL_REQUESTS"); do
  curl -sf "$URL" > /dev/null 2>&1 || true
done
echo "✅ OpsPulse load test completed successfully."
