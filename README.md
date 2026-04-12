<h1 align="center">Astral Kerykeion</h1>
<p align="center">Generate astrology charts via a simple FastAPI service. Returns structured JSON or a ready-to-use SVG chart powered by the kerykeion library.</p>

---

## What is this?

Astral Kerykeion is a lightweight HTTP API that:

- Computes astrological data for a person given birth details
- Generates beautiful SVG natal, synastry, and transit charts (with theming support)
- Caches responses in-memory with LRU-style eviction
- Ships with Docker and Kubernetes manifests for easy deployment

Technology: FastAPI, Uvicorn, and [kerykeion](https://pypi.org/project/kerykeion/).

OpenAPI docs are available at /docs when the server is running.

## Features

- JSON and SVG outputs from a single endpoint
- Built-in CORS enabled for all origins
- In-memory cache with configurable max items and max size (MB)
- Simple CSS theming for charts (see app/themes/astral.css)
- Dockerized runtime (port 80 inside the container)
- Kubernetes deployment and service manifests included

## Quickstart

### Option A — Local (Windows)

Prereqs: [uv](https://docs.astral.sh/uv/) installed.

```bat
cd app
uv venv
# On Windows:
.venv\Scripts\activate
uv pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

Now open http://localhost:8002/docs

To run the testing suite:

```bat
uv run python -m pytest tests -v
```

### Option B — Docker

Build and run the container (the app listens on port 80 inside the container):

```bat
docker build -t astral-kerykeion .
docker run --rm -p 8000:80 astral-kerykeion
```

Open http://localhost:8000/docs

## API

### Natal Chart
- **Path**: `/gen` (alias: `/gen/birth`)
- **Method**: GET
- **Returns**: `application/json` or `image/svg+xml` depending on the `svg` flag.

Query parameters:
- `name` (string) — subject name
- `year` (int) — year of birth
- `month` (int) — month of birth (1-12)
- `day` (int) — day of birth (1-31)
- `hour` (int) — hour (0-23)
- `minute` (int) — minute (0-59)
- `city` (string) — city name
- `lng` (float) — longitude
- `lat` (float) — latitude
- `tz_str` (string) — timezone, e.g. `Europe/London`
- `svg` (bool, default false) — when true returns SVG; otherwise JSON

### Synastry Chart
- **Path**: `/charts/synastry`
- **Method**: GET
- **Description**: Compares two charts.
- **Parameters**: `name1`, `year1`, `month1`, `day1`, `hour1`, `minute1`, `city1`, `lng1`, `lat1`, `tz_str1` AND same for person 2 (e.g. `name2`, `year2`, ...).

### Transit Chart
- **Path**: `/charts/transit`
- **Method**: GET
- **Description**: Composes a transit chart over a natal chart.
- **Parameters**: 
  - Natal: `name`, `year`, `month`, `day`, `hour`, `minute`, `city`, `lng`, `lat`, `tz_str`
  - Transit reference: `t_year`, `t_month`, `t_day`, `t_hour`, `t_minute`, `t_city`, `t_lng`, `t_lat`, `t_tz_str`

### Examples

**Birth Chart (JSON):**
```
GET /charts/birth?name=Ada%20Lovelace&year=1815&month=12&day=10&hour=6&minute=0&city=London&lng=-0.1278&lat=51.5074&tz_str=Europe%2FLondon
```

**Transit Chart (SVG):**
```
GET /charts/transit?name=Ada&year=1815&month=12&day=10&hour=6&minute=0&city=London&lng=-0.1278&lat=51.5074&tz_str=Europe/London&t_year=2024&t_month=1&t_day=1&t_hour=12&t_minute=0&t_city=London&t_lng=-0.1278&t_lat=51.5074&t_tz_str=Europe/London&svg=true
```

Response:
- 200 OK — `application/json` or `image/svg+xml`
- 400/422 — validation error for bad or missing parameters
- 500 — chart generation failure (rare)

### Cache endpoints

The service maintains an in-memory cache with LRU-style eviction. Defaults:

- Max items: 700
- Max size: 100 MB

Endpoints:

- GET /cache/info — returns cache stats (count, size MB, keys)
- DELETE /cache/clear — clears all cached items
- PUT /cache/config — update limits via query params max_items and/or max_size_mb

Examples:

```
PUT /cache/config?max_items=500&max_size_mb=50
GET /cache/info
DELETE /cache/clear
```

## Theming (SVG)

Generated SVG charts can be styled via CSS embedded into the SVG. By default, the server tries to inline the CSS from app/themes/astral.css whenever an SVG is produced.

Notes:

- The server reads from ./themes/astral.css relative to the working directory
- In Docker (WORKDIR=/app), that resolves to /app/themes/astral.css (already present)

To customize:

1) Edit app/themes/astral.css
2) Request an SVG (svg=true) and the styles will be injected into the SVG markup

If the CSS file is missing, SVGs will still be returned without extra styling.

## Kubernetes

Manifests are provided under kubernetes/:

- kubernetes/deployment.yaml — app Deployment (container listens on 80)
- kubernetes/service.yaml — ClusterIP Service on port 80

Notes:

- Update the image in the Deployment to your registry (or publish to GHCR as shown)
- The Service is ClusterIP; expose via Ingress or change to LoadBalancer for direct access
- An imagePullSecret for GitHub Container Registry (GHCR) is referenced; configure or remove accordingly

Apply manifests:

```bat
kubectl apply -f kubernetes\deployment.yaml
kubectl apply -f kubernetes\service.yaml
```

## Development

- Source entry: app/main.py
- Requirements: app/requirements.txt
- Local testing suite: `python -m pytest tests` (expects server on http://localhost:8002)
- Swagger UI: /docs | ReDoc: /redoc

## Acknowledgements

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Astrology computations and SVG charts by [kerykeion](https://pypi.org/project/kerykeion/)
