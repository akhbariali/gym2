# WHEY CLUB

A responsive Persian / RTL natural-bodybuilding site with training and nutrition content, a health calculator, and a supporting supplement storefront, built with plain HTML, CSS, and JavaScript.

Open `dist/index.html` in a browser, or run `python3 -m http.server 5173 --directory dist` and visit http://localhost:5173.

Features: a content-first homepage with an optimized, user-provided training video; an evidence-linked beginner path at `/start/`; published articles; a calorie/protein/BMI calculator; product search, protein/flavor/price filters, sorting, persistent local cart, and a protein guide.

The brand, six products, packaging, nutrition values, and prices are illustrative. Payment and real order submission are not connected. Replace sample catalog data in `dist/app.js` before launch. Fonts use Google Fonts with system fallbacks.

Checks include Python route/publishing tests, Node catalog/calculator checks, actual Chrome desktop/mobile layouts, product search/cart, and local HTTP previews.

A private Sites project is registered in `.openai/hosting.json`, but publication did not complete: both initial and refreshed source credentials were already expired relative to the local clock. No live deployment has been verified.

## Independent server deployment

A Dockerfile serves only the static storefront using unprivileged Nginx on container port 8080. Build from this directory with `docker build -t whey-club:local .`.

Before deployment, inspect listening ports, running containers, available resources, and firewall rules. Choose an unused host port and a unique container name. Do not modify existing reverse proxy configuration or restart existing services. The server deployment uses a separate Nginx process instead of Docker to minimize memory use; see below.

## Server service

Deployment target: `http://94.184.25.127:8088`. Static files live in `/opt/whey-club/site`; configuration is `/opt/whey-club/nginx.conf`. `deploy/` contains the standalone configuration and systemd unit. The existing Nginx service, proxy configurations, applications, and firewall rules are not modified.

Static files are owned by `root:root` with world-readable files/directories; this lets the capability-restricted publisher write them while the unprivileged web service can only read them.

The separate `whey-club.service` uses a dynamic unprivileged user, a read-only filesystem except its runtime directory, a 64 MB memory cap, and 20% CPU quota. It starts automatically after reboot. Inspect with `systemctl status whey-club` and `journalctl -u whey-club`. Stop only this storefront with `systemctl disable --now whey-club`.

For updates, upload the contents of `dist/` into `/opt/whey-club/site/`; static content updates do not require restarting Nginx.

## Persian journal and automatic publishing

The supplied 100-article package is imported into `content/articles.json`. Public journal: `http://94.184.25.127:8088/blog/`. Each article has a static HTML URL, unique title/meta description, canonical URL, Article structured data, sources, table of contents, publication date, related published articles, and a shop link. The journal supports Persian search/category filters; the homepage shows up to three published articles. No medical reviewer is invented; articles disclose that they were AI-assisted and not medically reviewed.

`publish_articles.py` uses only Python's standard library. The first run publishes article 1 immediately. Each subsequent article becomes eligible 48 hours after the preceding actual publication. A persistent systemd timer checks every five minutes, so publication can be up to five minutes after the interval. Missed intervals do not cause bulk publishing: after downtime it publishes at most one article, then waits another 48 hours. After article 100 it stops adding articles. A lock prevents concurrent publications, atomic file writes protect pages, and publication history persists across restarts and content deployments.

Server paths:

- Private queue and script: `/opt/whey-club/publisher/{content,scripts}` (outside Nginx's document root).
- Persistent dates/history: `/var/lib/whey-club-publisher/publication.json` (never overwrite during deployment).
- Generated public pages: `/opt/whey-club/site/blog/`, `sitemap.xml`, and `robots.txt`.
- Schedule: `whey-club-publisher.timer`; execution/logs: `whey-club-publisher.service`.

Inspect: `systemctl list-timers whey-club-publisher.timer` and `journalctl -u whey-club-publisher.service`.
Pause: `systemctl disable --now whey-club-publisher.timer`. Resume: `systemctl enable --now whey-club-publisher.timer`.
The timer's status shows the next **check**, not the next article. The next article is due 48 hours after the last `published_at` value in the state file.

To rebuild published pages after editing the private queue, run:

```sh
python3 /opt/whey-club/publisher/scripts/publish_articles.py \
  --source /opt/whey-club/publisher/content/articles.json \
  --output /opt/whey-club/site \
  --state-dir /var/lib/whey-club-publisher \
  --origin http://94.184.25.127:8088 --rebuild
```

The same origin is configured in the publisher service; update it when a real domain is attached, then rebuild. Never put the full queue/ZIP in `site/`, and do not synchronize the static files with a delete option that erases generated articles. Source `status: draft` is retained from the original package; the persistent publication history is authoritative for the authorized automatic release schedule.

Local journal preview: run `python3 scripts/publish_articles.py --source content/articles.json --output dist --state-dir .publication-state --origin http://localhost:5173`, then start the local HTTP server. Generated journal files and local state are ignored by Git.

Validation: `python3 -m unittest discover -s whey-club/tests -v` from the repository root. Tests cover all 100 rendered pages, the 48-hour boundary, idempotency, clock rollback, downtime, queue exhaustion, rebuilds, HTML escaping, and future article privacy. The storefront remains a demo catalog with checkout disabled.

## Color palette and page URLs

The storefront and journal use soothing lime `#DFF478`, silky white `#F7F3E6`, floral blue `#92BAD5`, kawaii blue `#788CE3`, and nautical navy `#17243F`. Navy text and buttons, lime hero sections, and floral/periwinkle panels carry the theme through product illustrations and article pages.

### Natural bodybuilding homepage

`dist/index.html` is the content-first homepage; `/start/` is generated from `content/start.html` and `/about/` from `content/about.html`. The shop catalog and whey guide are preserved in `content/storefront-catalog.html` and `content/whey-guide.html`, so shop generation no longer depends on a catalog being present on the homepage.

The homepage uses an eight-second, silent H.264 version of the user-provided training clip, with a poster and native playback controls. `dist/homepage.js` respects reduced-motion and data-saving preferences before autoplaying. The original 4K upload remains unchanged outside the public site; only the optimized derivative is served. Social links await actual account URLs. No checkout, daily Telegram/Instagram automation or live deployment was enabled. See `docs/iran-launch.md` for the launch experiment and its limits.

### ماشین حساب سلامت

`/health-calculator/` estimates resting energy, maintenance calories and a starting calorie target for losing, maintaining or gaining weight. It also shows resistance-training protein ranges, protein across four meals, and adult BMI. Persian and Arabic numerals are accepted. Calculations run entirely in the browser without storing or submitting personal inputs.

The tool supports ages 20–80, weights 35–250 kg and heights 130–220 cm. It uses Mifflin–St Jeor, approximate activity factors, a 15% deficit or 10% surplus, and 1.6–2.2 g/kg protein for healthy resistance-training adults. Sources and limitations are displayed on the page. It withholds weight-loss targets below BMI 18.5, unusually low calorie targets, and protein estimates at BMI 30 or above. These are product guardrails, not diagnoses or universal safety thresholds. It is unsuitable for pregnancy, breastfeeding and conditions requiring individualized nutrition care.

Page content: `content/health-calculator.html`; behavior and styles: `dist/health-calculator.{js,css}`. Run `python3 scripts/build_storefront.py` after changing the HTML, and rebuild already-published journal pages to update their navigation and sitemap. Run `node tests/test_health_calculator.cjs`, `node tests/test_storefront.cjs` and `python3 -m unittest discover -s tests -v` for regression checks.

Public pages:

- `/shop/`: store landing page with the available whey category.
- `/shop/whey-protein/`: full whey catalog.
- `/shop/whey-protein/{isolate,concentrate,blend}/`: specific whey types.
- `/products/whey-isolate-chocolate/` (and five other descriptive product pages).
- `/cart/`, `/guide/whey-protein/`, `/about/`.
- `/blog/what-is-whey-protein/`: descriptive article URLs.
- `/blog/category/whey-protein/`: published article category pages.

Original `fa-fitness-*` article IDs are retained in the private queue/state for scheduling. `url_slug` is used only for the public URL; the dedicated storefront Nginx configuration issues 301 redirects from the original article addresses. The publisher does not reset dates when URLs change. Sitemap entries include shop/product/guide/about routes and only published journal pages. Cart is marked noindex. Unknown URLs return 404.

Catalog source: `content/products.json`. Build store routes and browser catalog data with `python3 scripts/build_storefront.py --origin http://94.184.25.127:8088` from `whey-club/`, then run the article publisher with `--rebuild` to refresh the sitemap and already-published articles. Root-relative links/assets work on direct visits and reloads of nested URLs. Product pages include canonical tags, product metadata, breadcrumbs, and HTML product details; catalog category links are also present in static HTML. Existing local cart IDs are preserved.

Routing/cart regression tests: `node whey-club/tests/test_storefront.cjs` from the repository root.
