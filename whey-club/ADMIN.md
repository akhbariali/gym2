# Store administration

Open **https://wheyclub.ir/admin/** (`/admin` redirects to `/admin/`). The Persian Django admin is staff-only, uses HTTPS/session/CSRF protection, and limits login attempts. A dedicated randomly named owner account is created by `bootstrap_store_admin`; its generated credentials are written only to a private file, never to Git or application logs. Existing customer accounts are not promoted. Password changes are available from the admin header.

## Products

Use **افزودن محصول**. Enter the name, brand, type, flavor, package size, price in toman, protein/serving data, image URL or built-in placeholder, and stock. Extra nutrition, ingredients, allergens, usage and package information are optional and grouped separately. The public URL can be left blank to generate a unique slug; it is read-only after creation so saved links remain stable. Enable **نمایش در فروشگاه** to publish. Uncheck it to archive; hard deletion is disabled to preserve historical references.

Products are stored in PostgreSQL and immediately feed `/api/products/`, public product pages, the catalog, checkout validation and the dynamic sitemap. Product pages return real 404s for missing/unpublished products. Checkout calculates current prices on the server and rejects unpublished/out-of-stock items. Zero stock means unavailable; blank stock means stock enforcement is disabled. The original eight whey/creatine/shaker records are imported with their IDs, slugs, nutrition and recommendation metadata preserved.

## Orders and reports

The dashboard shows sales value, paid-order count, units sold, active paid orders, unpaid checkout drafts, per-product units/value, and recent orders. Date filters cover all time, seven days and thirty days. Per-product revenue uses the unit price saved on each order line, so editing today's product price does not rewrite historical sales.

Verified sales require `payment_status=paid`, a payment reference, a paid timestamp, and a non-cancelled order. Refunded, unpaid, cancelled or unverified records are excluded. Active orders are verified paid orders in pending, processing or shipped state. Unpaid checkout drafts remain separate and read-only. Product-only staff cannot see financial reports without order-view permission.

Order details include the customer, shipping address, line items, payment reference, total and status. Fulfillment status, tracking and internal notes are editable. Financial fields and line items are read-only; admin cannot mark a payment successful or create a paid order manually. Unpaid orders cannot be prepared/shipped. Cancellation is not a bank refund; actual refund handling belongs to the future gateway integration.

**The payment gateway is still unavailable.** There is no adapter creating verified paid orders from checkout yet, so the initial real-sales figures are zero. Do not treat drafts or fabricated test payments as revenue. Payment integration must verify the provider callback before creating the Order/OrderItem snapshots and updating inventory.

## Deployment

Run `python manage.py migrate`, collect Django static files into `/opt/whey-club/django-static`, build/prerender React, and preserve production secrets/hosts/TLS settings. Nginx proxies `/admin/`, `/api/`, `/products/`, and `/sitemap.xml` to Django; `/django-static/` serves admin assets. Django reads the current frontend entry manifest using `WHEY_FRONTEND_ROOT=/opt/whey-club/site`. Keep its TCP port on loopback and let only the controlled Nginx proxy set the trusted HTTPS header.

Before changes, keep a PostgreSQL dump plus the backend/settings/Nginx backup. No admin credentials belong in source. The management command `bootstrap_store_admin --output /root/wheyclub-admin-login.txt` refuses to overwrite an existing credential file or reset an existing account.

Validation: `python manage.py test store` on PostgreSQL covers permissions, live product publication and archiving, stock/price validation, sales calculations, payment-field protection, fulfillment checks and private owner-account creation. Browser verification covers owner login, the dashboard and product form. Test orders/products are confined to the isolated test database; production sales are not fabricated for the preview.
