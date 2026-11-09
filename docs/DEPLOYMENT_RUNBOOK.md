# OffmarketStream — Production deployment (saved reference)

Last verified: **2026-11-09**

## Live URLs

| What | URL |
|------|-----|
| **Site (IP)** | http://3.14.42.168/ |
| **API health** | http://3.14.42.168/api/health |
| **GitHub repo** | https://github.com/Moiz1Khan/PropertyDamageDetection |
| **Old Vercel UI** | https://prop-iq-eight.vercel.app (optional; not wired to Lightsail API unless env updated) |

## AWS Lightsail

| Item | Value |
|------|--------|
| Instance name | `offmarketstream` |
| Region | **us-east-2** (Ohio) |
| Plan | ~2 GB RAM / 2 vCPU |
| Static IP | **3.14.42.168** |
| OS | Ubuntu 22.04 |
| App path on VM | `/var/www/offmarketstream` |
| Nginx config | `/etc/nginx/sites-available/offmarketstream` |
| API systemd | `offmarketstream-api.service` |
| Production env | `/var/www/offmarketstream/deploy/.env.production` (not in git) |

## Demo logins

| Role | Email | Password |
|------|-------|----------|
| Investor | demo@offmarketstream.com | demo123 |
| Admin | admin@offmarketstream.com | admin123 |

## CI/CD (GitHub Actions)

- Workflow: `.github/workflows/deploy-lightsail.yml`
- Trigger: every **push to `main`** (+ manual `workflow_dispatch`)
- Secrets on repo (names only — values in GitHub):

  | Secret | Purpose |
  |--------|---------|
  | `LIGHTSAIL_HOST` | `3.14.42.168` |
  | `LIGHTSAIL_USER` | `ubuntu` |
  | `LIGHTSAIL_SSH_KEY` | ed25519 key for Actions → VM (`deploy/.ssh/github_actions` on dev machine, **gitignored**) |

- Deploy script on server: `bash /var/www/offmarketstream/deploy/deploy.sh`
- One-time bootstrap: `deploy/lightsail-one-shot.sh` or `deploy/bootstrap-server.sh`

## Attach a custom domain (Lightsail)

### Option A — Domain in Lightsail (easiest)

1. Lightsail → **Networking** → **Create DNS zone** → enter your domain (e.g. `offmarketstream.com`).
2. Lightsail shows **nameservers** — set these at your domain registrar (GoDaddy, Namecheap, etc.).
3. In the DNS zone, add **A record**:
   - **Subdomain:** `@` (root) and/or `www`
   - **Points to:** `3.14.42.168` (your static IP)
4. Wait for DNS propagation (minutes to 48h).

### Option B — Keep DNS at registrar

Add **A record** only:

| Type | Host | Value |
|------|------|--------|
| A | `@` | `3.14.42.168` |
| A | `www` | `3.14.42.168` |

### HTTPS (recommended after domain works)

1. Lightsail → **Networking** → **Certificates** → create cert for your domain (+ www).
2. Attach cert to a **Load balancer** (Lightsail LB) **or** use Certbot on the VM:

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

3. Update frontend build if you change public URL (same-origin `/api` on one domain usually needs no change).

### After domain is live

- Test: `https://yourdomain.com/api/health`
- Optional: add domain to `backend/app/config.py` `cors_origins` and redeploy (push to `main`).

## Quick checks

```bash
# From your PC
curl http://3.14.42.168/api/health

# On VM (SSH)
sudo systemctl status offmarketstream-api nginx
bash /var/www/offmarketstream/deploy/deploy.sh
```

## CI/CD test log

See `docs/CI_CD_TEST_LOG.md` (updated on test commits).
