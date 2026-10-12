# Flask CRUD API (SQLite + SQLAlchemy)

A small, production-style REST API for a single `items` table, built with **Flask**, **SQLAlchemy ORM** and **SQLite**.

## Features
- Full CRUD on `items` (`id`, `name`, `description`, `created_at`, `updated_at`)
- JSON input validation with clear error messages
- Correct HTTP status codes: `201`, `200`, `204`, `400`, `404`
- Partial updates with `PUT` (only the fields you send are changed)
- App factory pattern, configurable database via `DATABASE_URL`
- Automated tests for every endpoint (pytest, in-memory DB)

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                    # http://127.0.0.1:5000
```

## Endpoints
| Method | Path | Description | Success |
|---|---|---|---|
| POST | `/items` | Create an item (`name` required, `description` optional) | 201 |
| GET | `/items` | List all items | 200 |
| GET | `/items/<id>` | Get one item | 200 |
| PUT | `/items/<id>` | Update `name` and/or `description` | 200 |
| DELETE | `/items/<id>` | Delete an item | 204 |

## Examples
```bash
curl -X POST localhost:5000/items -H "Content-Type: application/json" \
     -d '{"name": "Widget", "description": "A useful thing"}'
curl localhost:5000/items
curl localhost:5000/items/1
curl -X PUT localhost:5000/items/1 -H "Content-Type: application/json" -d '{"description": "Updated"}'
curl -X DELETE localhost:5000/items/1
```

Error format: `{"error": "Item 99 not found."}`

## Tests
```bash
pytest -q
```
