# Lightsail deploy + GitHub Actions

## Kernel upgrade popup (after `apt upgrade`)

Press **Ok** / **Enter**. The update finished. Reboot when convenient:

```bash
sudo reboot
```

Wait 1–2 minutes, then reconnect via Lightsail SSH.

## One-time server setup

The repo is **private**, so `curl raw.githubusercontent.com/...` returns **404**. Use **git clone** on the VM (SSH key or PAT), then run bootstrap locally.

### Option A — SSH key (recommended)

On the VM:

```bash
ssh-keygen -t ed25519 -C "lightsail" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub
```

Add the printed key in GitHub → **PropertyDamageDetection** → **Settings → Deploy keys** → **Add deploy key** (read access).

Then:

```bash
sudo mkdir -p /var/www/offmarketstream
sudo chown ubuntu:ubuntu /var/www/offmarketstream
git clone git@github.com:Moiz1Khan/PropertyDamageDetection.git /var/www/offmarketstream
bash /var/www/offmarketstream/deploy/bootstrap-server.sh
```

### Option B — HTTPS + Personal Access Token

Create a GitHub PAT (repo scope), then:

```bash
git clone https://YOUR_GITHUB_TOKEN@github.com/Moiz1Khan/PropertyDamageDetection.git /var/www/offmarketstream
bash /var/www/offmarketstream/deploy/bootstrap-server.sh
```

### Option C — Public repo

If you set the repository to **Public**, the one-line curl bootstrap works again:

```bash
curl -fsSL https://raw.githubusercontent.com/Moiz1Khan/PropertyDamageDetection/main/deploy/bootstrap-server.sh -o /tmp/bootstrap.sh
chmod +x /tmp/bootstrap.sh
bash /tmp/bootstrap.sh
```

## GitHub Actions secrets

Repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|--------|--------|
| `LIGHTSAIL_HOST` | Your static IP (e.g. `3.14.42.168`) |
| `LIGHTSAIL_USER` | `ubuntu` |
| `LIGHTSAIL_SSH_KEY` | Private key (full PEM contents) |

### Get SSH private key for Actions

1. Lightsail → **Account** → **SSH keys** → download default key for your region, **or**
2. On the VM: `ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions -N ""`
3. `cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys`
4. Copy `~/.ssh/github_actions` private key into GitHub secret `LIGHTSAIL_SSH_KEY`

Every push to `main` runs `.github/workflows/deploy-lightsail.yml` and runs `deploy/deploy.sh` on the VM.

## Manual deploy

```bash
cd /var/www/offmarketstream && bash deploy/deploy.sh
```
