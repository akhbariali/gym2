# WHEY CLUB

A responsive Persian / RTL whey protein storefront built with plain HTML, CSS, and JavaScript.

Open `dist/index.html` in a browser, or run `python3 -m http.server 5173 --directory dist` and visit http://localhost:5173.

Features: product search, protein/flavor/price filters, sorting, sale and popular collections, product dialogs, persistent local cart, and an educational protein guide.

The brand, six products, packaging, nutrition values, and prices are illustrative. Payment and real order submission are not connected. Replace sample catalog data in `dist/app.js` before launch. Fonts use Google Fonts with system fallbacks.

Checks completed: JavaScript syntax, catalog rendering, search, empty state, price filtering, cart quantities/totals, and product dialog logic. HTTP preview returned 200. Visual browser checks were unavailable in this session.

A private Sites project is registered in `.openai/hosting.json`, but publication did not complete: both initial and refreshed source credentials were already expired relative to the local clock. No live deployment has been verified.

## Independent server deployment

A Dockerfile serves only the static storefront using unprivileged Nginx on container port 8080. Build from this directory with `docker build -t whey-club:local .`.

Before deployment, inspect listening ports, running containers, available resources, and firewall rules. Choose an unused host port and a unique container name. Do not modify existing reverse proxy configuration or restart existing services. The server deployment uses a separate Nginx process instead of Docker to minimize memory use; see below.

## Server service

Deployment target: `http://94.184.25.127:8088`. Static files live in `/opt/whey-club/site`; configuration is `/opt/whey-club/nginx.conf`. `deploy/` contains the standalone configuration and systemd unit. The existing Nginx service, proxy configurations, applications, and firewall rules are not modified.

The separate `whey-club.service` uses a dynamic unprivileged user, a read-only filesystem except its runtime directory, a 64 MB memory cap, and 20% CPU quota. It starts automatically after reboot. Inspect with `systemctl status whey-club` and `journalctl -u whey-club`. Stop only this storefront with `systemctl disable --now whey-club`.

For updates, upload the contents of `dist/` into `/opt/whey-club/site/`; static content updates do not require restarting Nginx.
