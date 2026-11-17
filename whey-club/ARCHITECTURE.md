# Frontend/backend separation

- `frontend/`: React + Vite. Existing storefront layouts, styles, imagery, video, cart behavior, and URL structure are retained. Shop layouts are currently imported HTML templates rendered by React, with the original interaction script; these can be converted into smaller React components incrementally. Journal pages use React components and Django API data.
- `backend/`: Django API. Products and article content come from the existing content JSON files. Only articles in the persistent publication history are exposed. Existing article IDs and publication dates remain unchanged.
- Existing `dist/`, deployment files, and publishing service remain intact for rollback. The develop deployment runs Django on loopback port 8089 behind the existing isolated storefront on 8088.

## Development

Backend (Python 3.10+):

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
