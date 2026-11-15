# Task API

A small, production-ready Python REST API (Flask + Gunicorn + SQLite) packaged for Docker.

## Project layout

```
taskapi/
├── app/
│   ├── __init__.py      # application factory
│   ├── db.py            # SQLite connection + schema
│   └── routes.py        # HTTP endpoints
├── tests/test_api.py    # pytest suite
├── wsgi.py              # WSGI entrypoint
├── gunicorn.conf.py     # Gunicorn config (env-driven)
├── Dockerfile           # multi-stage, non-root, healthcheck
├── docker-compose.yml   # one-command deploy with a persistent volume
├── requirements.txt / requirements-dev.txt
└── Makefile
```

## Deploy with Docker

```bash
# Option A: docker compose (recommended)
docker compose up -d --build
curl http://localhost:8000/health

# Option B: plain docker
docker build -t task-api .
docker run -d -p 8000:8000 -v task-data:/data --name task-api task-api
```

Data is stored in SQLite at `/data/tasks.db`, kept in the `task-data` volume so it survives restarts.

## Endpoints

| Method | Path            | Description               |
|--------|-----------------|---------------------------|
| GET    | `/`             | Service name and version  |
| GET    | `/health`       | Health check (used by Docker) |
| GET    | `/tasks`        | List tasks                |
| POST   | `/tasks`        | Create `{"title": "..."}` |
| GET    | `/tasks/<id>`   | Get one task              |
| PATCH  | `/tasks/<id>`   | Update `title` and/or `done` |
| DELETE | `/tasks/<id>`   | Delete a task             |

Example:

```bash
curl -X POST localhost:8000/tasks -H 'Content-Type: application/json' -d '{"title":"Ship it"}'
curl -X PATCH localhost:8000/tasks/1 -H 'Content-Type: application/json' -d '{"done":true}'
curl localhost:8000/tasks
```

## Configuration (environment variables)

| Variable           | Default          | Purpose                     |
|--------------------|------------------|-----------------------------|
| `PORT`             | `8000`           | Port Gunicorn binds to      |
| `DATABASE_PATH`    | `/data/tasks.db` | SQLite file location        |
| `WEB_CONCURRENCY`  | `2*CPU+1` (max 4)| Gunicorn worker processes   |
| `GUNICORN_THREADS` | `2`              | Threads per worker          |
| `LOG_LEVEL`        | `INFO`           | Logging level               |

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q                               # run tests
DATABASE_PATH=./tasks.db python wsgi.py # dev server on :8000
```
