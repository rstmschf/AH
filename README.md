# Auction House

A REST + WebSocket backend for running timed online auctions. Users create auctions, invite bidders via a one-time code, and place bids in real time. When the end time hits, a scheduled task picks a winner per item.

## Stack

- **Django 6 + DRF:** REST API under `/api/v1/`
- **Channels + Daphne:** WebSockets for live bid broadcasts
- **PostgreSQL:** row level locking for bid serialization
- **Redis:** message brocker for both wS and Celery
- **Celery + Beat:** periodic task closes expired auctions and picks winners
- **JWT (simplejwt):** auth for both HTTP and WS (token via `?token=...`)
- **pytest + pytest-asyncio:** sync, async, and multithreaded concurrency tests

## Architecture notes

Some design decisions:

**Hybrid WSGI + ASGI:** I kept both for now, but plan to move everything to Dapnhe once I add nginx. Now Gunicorn serves REST on `:8000`, Daphne serves WS on `:8001`. REST endpoints are synchronous and benefit from Gunicorn's worker management while WS connections are long-lived and need Daphne's async model. Redis sits between them as the channel layer so a bid created in Gunicorn reaches WS clients connected to Daphne.

**Bid serialization:** `perform_create` wraps the write in `@transaction.atomic` with `SELECT ... FOR UPDATE` on the item row. Two users bidding the same amount simultaneously produces exactly one winner wbile the second gets a clean 400 with the updated minimum. Tested with with `threading.Barrier`.

**WS broadcasts happen on commit:** events are emitted via `transaction.on_commit` so the broadcast only fires if the bid actually persists which means rolledback bid will not send fake event to WS clients.

**Visibility vs. authorization are separate layers:** private auctions return 404 to non-participants (not 403) to not leak that auction exists to someone who can't see it. Done by the queryset, permissions only guard write actions on visible objects.

**Soft deletes:** auctions and items use `django-safedelete` with cascade-soft-delete, so bid history survives an accidental delete.

## Setup

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

Services:
- `web`  Gunicorn on `:8000`
- `ws`  Daphne on `:8001`
- `celery` + `celery-beat`
- `db` (Postgres) + `redis`

Migrations run automatically on `web` startup. To create an admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

OpenAPI schema + Swagger UI at `/api/schema/` and `/api/schema/swagger-ui/`.

## Tests

```bash
docker compose exec web pytest
```

66 tests across auctions, items, bids, users, and WebSockets (will add more for new functionality Im planning to add):

- Permission + visibility edge cases (private auctions return 404, not 403)
- Multi-threaded bid concurrency to see if equal bids resolve to one winner and higher bid always wins regardless of scheduling
- WebSocket auth, visibility enforcement, and end-to-end broadcast

## Work in progress

- Frontend soon to be added: for now this is backend-only.
- No nginx config yet. WS and HTTP are exposed on separate ports.
- Email/notifications not wired up yet, will likely add mail+socials notifs.