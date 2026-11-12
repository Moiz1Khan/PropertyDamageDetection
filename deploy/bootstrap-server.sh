#!/usr/bin/env bash
# One-time setup on Lightsail Ubuntu. Run as ubuntu with sudo.
set -euo pipefail

APP_ROOT="/var/www/offmarketstream"
REPO_URL="${REPO_URL:-https://github.com/Moiz1Khan/PropertyDamageDetection.git}"

export DEBIAN_FRONTEND=noninteractive

echo "==> Packages"
sudo apt-get update -qq
sudo apt-get install -y -qq git nginx python3-venv python3-pip curl libgl1 libglib2.0-0

if ! command -v npm >/dev/null 2>&1; then
  echo "==> Node.js 20"
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y -qq nodejs
fi

echo "==> App directory"
sudo mkdir -p "$APP_ROOT"
sudo chown ubuntu:ubuntu "$APP_ROOT"
if [ ! -d "$APP_ROOT/.git" ]; then
  git clone "$REPO_URL" "$APP_ROOT"
else
  cd "$APP_ROOT"
  git pull origin main || true
fi

echo "==> Env file (create if missing)"
ENV_FILE="$APP_ROOT/deploy/.env.production"
if [ ! -f "$ENV_FILE" ]; then
  SECRET="$(openssl rand -hex 24)"
  cat > "$ENV_FILE" <<EOF
# Production env for systemd (not committed)
DATABASE_URL=sqlite:////var/www/offmarketstream/backend/offmarketstream.db
SECRET_KEY=$SECRET
EOF
  chmod 600 "$ENV_FILE"
fi

echo "==> Nginx"
sudo cp "$APP_ROOT/deploy/nginx-offmarketstream.conf" /etc/nginx/sites-available/offmarketstream
sudo ln -sf /etc/nginx/sites-available/offmarketstream /etc/nginx/sites-enabled/offmarketstream
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx

echo "==> Systemd"
sudo cp "$APP_ROOT/deploy/offmarketstream-api.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable offmarketstream-api

echo "==> First deploy"
chmod +x "$APP_ROOT/deploy/deploy.sh"
bash "$APP_ROOT/deploy/deploy.sh"

echo "==> Done. Open http://<your-static-ip>/"
