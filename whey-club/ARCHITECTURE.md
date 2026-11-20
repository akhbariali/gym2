# Frontend/backend separation

- `frontend/`: React + Vite. Existing storefront layouts, styles, imagery, video, cart behavior, and URL structure are retained. Shop layouts are currently imported HTML templates rendered by React, with the original interaction script; these can be converted into smaller React components incrementally. Journal pages use React components and Django API data.
- `backend/`: Django API. Products are managed in PostgreSQL through `/admin/`; article content remains in the existing private JSON publishing queue. Only articles in the persistent publication history are exposed. Existing article IDs and publication dates remain unchanged.
- Existing `dist/`, deployment files, and publishing service remain intact for rollback. The develop deployment runs Django on loopback port 8089 behind the existing isolated storefront on 80.

## Development

Backend (Python 3.10+; configure PostgreSQL first as described in [POSTGRESQL.md](POSTGRESQL.md)):

```sh
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 127.0.0.1:8001
```

Frontend (Node 20+):

```sh
cd frontend
npm install
npm run dev
```

Visit http://localhost:5174. Vite proxies `/api/` to Django on port 8001. API endpoints: `/api/products/`, `/api/articles/`, `/api/articles/<descriptive-slug>/`, `/api/health/`.

Production must configure `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`, and `WHEY_PUBLICATION_STATE=/var/lib/whey-club-publisher/publication.json`. Configure `/api/` to Django and other routes to the React build's index.html. Existing assets are served from the React build. Keep the existing publication timer and state file; it remains the authority for the two-day release schedule.

Do not put the private article queue in frontend assets. The API reads it from `content/` on the backend. Preserve existing Nginx legacy article redirects when switching deployments. After the React build, run `python3 scripts/prerender_frontend.py`. The publisher also adds the React entry point to newly generated journal pages, preserving searchable HTML.

## Dedicated server

Deploy the current checkout's frontend from `whey-club/`:

```sh
bash scripts/deploy.sh
# Override the connection when needed:
DEPLOY_HOST=root@45.149.78.179 DEPLOY_PORT=22 bash scripts/deploy.sh
```

Requires local Python 3, Node/npm, rsync, and working SSH key authentication; the server also needs Bash, rsync, tar, and write access to `/opt/whey-club`. The script runs tests, installs locked frontend dependencies, builds and prerenders the pages, backs up the existing site under `/opt/whey-club/backups/`, and uploads to `/opt/whey-club/site/`. It preserves published articles, sitemap, robots.txt, and older bundles. After upload it validates `/opt/whey-club/nginx.conf`, restarts the site’s `whey-club.service`, and checks that the service is active. It does not pull Git changes, deploy backend code, migrate the database, or alter Nginx configuration. Verify the public site after upload; backups and older bundles require occasional manual cleanup.

Production host: `root@45.149.78.179`; website: `http://45.149.78.179` on port 80. Django stays private on loopback port 8089. The former shared host is retired for this project; its project services are disabled after migration verification. The article queue and publication history are transferred unchanged. Domain/TLS configuration will be added once a domain is supplied.

## Accounts, delivery addresses and checkout

React routes: `/account/`, `/account/register/`, `/account/login/`, `/account/addresses/`, `/checkout/`. Django session authentication uses CSRF protection, password hashing/validation and an authentication attempt limit. Addresses are scoped to the signed-in user; the optional Leaflet/OpenStreetMap picker loads tiles only when explicitly opened and never requests device geolocation.

`Address` and `CheckoutDraft` use PostgreSQL by default, configured through private `PG*` environment variables. The old SQLite database is retained only for verified migration/rollback. See [POSTGRESQL.md](POSTGRESQL.md) for setup, data transfer, verification and backups. Source deployments must never replace database storage or credentials. `python manage.py migrate` is required on schema updates.

Checkout validates ownership, product IDs and quantities, computes prices on the backend, and uses an idempotency key to avoid duplicate drafts. The cart is retained. Drafts are not paid/final orders. Payment availability and URL remain false/null until a real, server-verified payment provider integration is implemented. No mock successful payment or fake gateway redirect is provided. Catalog prices are still illustrative and delivery costs are not finalized.

Production account and checkout APIs require HTTPS (`ACCOUNT_REQUIRE_HTTPS`); the public HTTP account screens display an HTTPS-required message. Do not disable this guard for real users. Domain DNS currently is not ready. Once TLS is configured, set the domain in allowed hosts, configure trusted reverse-proxy HTTPS detection, and keep secure cookies enabled. Local development over localhost works without this production guard. There is no email verification/password-reset email service yet; registration states this explicitly.

Run account/ownership/CSRF/checkout/throttle tests using `python manage.py test store`. Rate limiting uses Django's process-shared local-memory cache for the single-worker deployment; adopt a shared cache before increasing Gunicorn workers. Nginx overwrites X-Forwarded-For to prevent spoofing; configure trusted CDN real-IP handling before routing account traffic through a CDN.

Store operations and deployment details: [ADMIN.md](ADMIN.md). Only the admin-panel checklist item is completed in this change; storefront redesign, eNAMAD, selected text removal and account-management work remain pending.
