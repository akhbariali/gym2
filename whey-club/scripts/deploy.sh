#!/usr/bin/env bash
# Deploy the current checkout's frontend to the existing WheyClub server.
set -euo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
DEPLOY_HOST=${DEPLOY_HOST:-root@45.149.78.179}
DEPLOY_PORT=${DEPLOY_PORT:-22}

if [[ ! $DEPLOY_PORT =~ ^[0-9]+$ ]] || (( 10#$DEPLOY_PORT < 1 || 10#$DEPLOY_PORT > 65535 )); then
    echo 'DEPLOY_PORT must be between 1 and 65535.' >&2
    exit 1
fi
if [[ $DEPLOY_HOST == -* || ! $DEPLOY_HOST =~ ^[a-zA-Z0-9_.@-]+$ ]]; then
    echo 'DEPLOY_HOST must be a hostname or user@hostname.' >&2
    exit 1
fi
for command in python3 node npm ssh rsync; do
    command -v "$command" >/dev/null || { echo "Missing command: $command" >&2; exit 1; }
done

cd "$ROOT"
python3 -m unittest discover -s tests -v
node tests/test_health_calculator.cjs
node tests/test_storefront.cjs
(
    cd frontend
    npm ci
    npm run build
)
python3 scripts/prerender_frontend.py
test -s frontend/build/index.html
test -s frontend/build/react-entry.json

ssh_options=(-p "$DEPLOY_PORT" -o BatchMode=yes -o ConnectTimeout=15)
ssh "${ssh_options[@]}" "$DEPLOY_HOST" 'bash -se' <<'REMOTE'
set -euo pipefail
command -v rsync >/dev/null
test -d /opt/whey-club/site
test -w /opt/whey-club/site
mkdir -p /opt/whey-club/backups
backup=$(mktemp /opt/whey-club/backups/site-XXXXXXXX.tar.gz)
tar -czf "$backup" -C /opt/whey-club site
echo "Site backup: $backup"
REMOTE

# Keep published articles, publisher metadata, and old bundles used by open tabs.
rsync -rlptz --delay-updates \
    --exclude='/blog/' --exclude='/sitemap.xml' --exclude='/robots.txt' \
    -e "ssh -p $DEPLOY_PORT -o BatchMode=yes -o ConnectTimeout=15" \
    frontend/build/ "$DEPLOY_HOST:/opt/whey-club/site/"

ssh "${ssh_options[@]}" "$DEPLOY_HOST" 'bash -se' <<'REMOTE'
set -euo pipefail
test -s /opt/whey-club/site/index.html
test -s /opt/whey-club/site/react-entry.json
nginx -t -p /opt/whey-club/ -c /opt/whey-club/nginx.conf
systemctl restart whey-club.service
systemctl is-active --quiet whey-club.service
REMOTE
echo "Frontend uploaded to $DEPLOY_HOST:/opt/whey-club/site/; site Nginx restarted."
echo 'Check https://wheyclub.ir/ and /health-calculator/ in your browser.'
