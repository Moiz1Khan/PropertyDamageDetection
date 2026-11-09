#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="/var/www/offmarketstream"
cd "$APP_ROOT"

echo "==> Pull latest (if not already updated by CI)"
git fetch origin main
git reset --hard origin/main

echo "==> Backend"
cd "$APP_ROOT/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "==> Frontend"
cd "$APP_ROOT/frontend"
export VITE_API_URL="/api"
if command -v npm >/dev/null 2>&1; then
  npm ci
  npm run build
else
  echo "npm not found; install Node.js on the server (see deploy/README.md)"
  exit 1
fi

echo "==> Restart API"
sudo systemctl restart offmarketstream-api
sudo systemctl reload nginx || sudo systemctl restart nginx

echo "==> Health check"
curl -fsS http://127.0.0.1/api/health
echo ""
echo "Deploy complete."
