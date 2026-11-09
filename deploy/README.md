# Lightsail deploy + GitHub Actions

## Kernel upgrade popup (after `apt upgrade`)

Press **Ok** / **Enter**. The update finished. Reboot when convenient:

```bash
sudo reboot
```

Wait 1–2 minutes, then reconnect via Lightsail SSH.

## One-time server setup

In Lightsail SSH (as `ubuntu`), download your GitHub **deploy key** or use HTTPS clone (public repo).

For SSH deploy from GitHub Actions you need a key pair — see below.

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
