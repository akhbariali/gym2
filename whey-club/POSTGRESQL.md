# PostgreSQL

PostgreSQL is Django's default database. Set `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGHOST` (default 127.0.0.1), `PGPORT` (5432), and optionally `PGSSLMODE`. Credentials belong in the server's root-readable `/opt/whey-club/django.env`, not Git. The production role should own only the application database and must not be a superuser or have CREATEDB.

## Local development

Install Python 3.10+ and Docker (or a local PostgreSQL installation). From `whey-club/`:

```sh
export PGPASSWORD='choose-a-local-development-password'
docker compose -f compose.postgres.yml up -d --wait
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 127.0.0.1:8001
```

The development Compose service exposes PostgreSQL only on loopback and stores data in a named volume. Its database owner can create test databases. Production credentials should not have this permission; run tests with a separate test role/instance.

SQLite remains available only when explicitly selected with `WHEY_DB_ENGINE=sqlite` and `WHEY_DATABASE=/path/to/db.sqlite3`. This is for isolated development and rollback, not the production default.

## One-time production migration

1. Inspect the current service, database location, credentials configuration, available resources and listening ports. Preserve all current domain/TLS settings. Install PostgreSQL and the psycopg driver. Keep port 5432 bound only to loopback; do not publish it through Nginx or a firewall.
2. Create an application database and an unprivileged dedicated login role. Pass randomly generated credentials through stdin and the private environment file; never put passwords in shell arguments or output.
3. Stage the new backend, apply migrations to the empty PostgreSQL database, and run the Django suite against a separate test database with test-only credentials.
4. During a short API maintenance window, stop only `whey-club-django`. Back up its service, environment file, settings and SQLite database in a root-only directory. Use SQLite's backup API for a consistent copy, including any WAL data.
5. Export all application records from the stopped SQLite source with `dumpdata --natural-foreign --exclude contenttypes --exclude auth.permission`. Keep the fixture mode 0600. Do not use `--natural-primary`: preserving user IDs also preserves signed-in session user references. Generated content types and permissions are recreated by `migrate`; natural foreign keys preserve permission relationships.
6. Save a logical manifest with `database_snapshot`. Load the fixture into PostgreSQL with `loaddata`. Run `database_snapshot --compare /secure/path/source-manifest.json` against PostgreSQL. It checks model row counts and a SHA-256 digest of the canonical serialized data, including password hashes, user/session IDs, saved addresses and checkout drafts. Do not switch if they differ. Django fixture loading resets sequences; verify a new record can be inserted without an ID collision in tests.
7. Back up PostgreSQL with `pg_dump -Fc`, append the private PostgreSQL connection settings, remove the service's old SQLite override, and restart only Django. Check the database-backed health endpoint, APIs, permissions, service logs and article timer. Existing article files and their publication state are independent and should not be changed.
8. Retain the SQLite backup and the before/after manifests. Rolling back requires `WHEY_DB_ENGINE=sqlite` and the original `WHEY_DATABASE` path, plus the previous settings/service/environment. Once PostgreSQL accepts new writes, reconcile them before rollback; do not silently discard new customer data.

## Backups

Use `pg_dump -Fc` for PostgreSQL backups, with restrictive file permissions and credentials supplied through a private environment or peer-authenticated database administrator. Test restoration into an isolated database. The old SQLite file is a migration rollback copy, not an ongoing backup. Source deployments must not overwrite the database data directory or private credential file.

## Validation

`python3 -m unittest discover -s tests -v` tests database configuration and existing static tooling. `python manage.py test store` must also run against PostgreSQL; SQLite-only tests do not establish PostgreSQL compatibility. The `database_snapshot` management command exposes only aggregate counts and a digest, not record contents.
