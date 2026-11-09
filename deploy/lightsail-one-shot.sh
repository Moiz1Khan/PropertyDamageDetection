#!/usr/bin/env bash
# Run once in Lightsail browser SSH (ubuntu). Public repo — no git auth needed.
set -euo pipefail

GITHUB_ACTIONS_PUB='ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINyqp3QrXQBNbrHC5i56tLAiUMyoF4ccoMu7z37uVegH github-actions-lightsail'

mkdir -p ~/.ssh
chmod 700 ~/.ssh
grep -qF "$GITHUB_ACTIONS_PUB" ~/.ssh/authorized_keys 2>/dev/null || echo "$GITHUB_ACTIONS_PUB" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

TMP=/tmp/offmarketstream-bootstrap.sh
curl -fsSL "https://raw.githubusercontent.com/Moiz1Khan/PropertyDamageDetection/main/deploy/bootstrap-server.sh" -o "$TMP"
chmod +x "$TMP"
bash "$TMP"
