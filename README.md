# Student Result Prediction — MLOps Practicals 1–12

This repository demonstrates an educational end-to-end MLOps workflow for a Student Result Prediction model. The API uses **FastAPI** on port **8000**.

## Practical roadmap

| Practical | Implementation |
|---|---|
| 1–5 | Python CI, model training, quality gate, artifacts, release candidate |
| 6 | Dockerize the FastAPI application |
| 7 | GitHub Actions builds and tests the Docker container |
| 8 | Publish and pull the image through GitHub Container Registry (GHCR) |
| 9 | Automate Docker build, test, tagging, and GHCR publishing |
| 10 | Deploy the GHCR image to Render |
| 11 | Structured application logs, request IDs, and request-duration logs |
| 12 | Prometheus metrics, Grafana dashboard, and alert rules |

## Architecture

GitHub Actions trains and validates the model, runs tests, builds the Docker image, starts it, and verifies health, prediction, and metrics endpoints. On a successful push, the workflow publishes the tested image to GHCR. Render can run that image. The local Docker Compose monitoring stack runs the API, Prometheus, and Grafana together.

## Run locally

Requires Python 3.11+.

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python train_model.py
python quality_gate.py
python -m unittest discover -v
uvicorn app:app --host 0.0.0.0 --port 8000
```

API endpoints:
- Root: `http://localhost:8000/`
- Health: `http://localhost:8000/health`
- Swagger: `http://localhost:8000/docs`
- Metrics: `http://localhost:8000/metrics`
- Prediction: `POST http://localhost:8000/predict`

Example prediction JSON:

```json
{
  "attendance": 90,
  "internal_marks": 85,
  "assignment_marks": 88,
  "previous_score": 80
}
```

All four values must be between 0 and 100. Invalid input returns HTTP 422.

## Practicals 6–9: Docker and GHCR

```bash
docker build -t student-result-prediction:local .
docker run --rm -p 8000:8000 student-result-prediction:local
```

The Docker build trains and quality-checks the model artifact. The GitHub Actions workflow builds the image, starts a container, and tests health, prediction, and Prometheus metrics before publishing `latest` and commit-specific tags to GHCR.

Image:
`ghcr.io/sasi-4225/student-result-prediction:latest`

## Practical 10: Render deployment

The `render.yaml` blueprint references the GHCR image and configures port 8000 with `/health` as the health-check path. Create/deploy the service in your Render account. If the GHCR package is private, configure a registry credential with read-only package access.

After deployment, verify the actual service URL:
- `/`
- `/health`
- `/docs`
- `/predict`

Do not report a public deployment as complete until these endpoints work on the actual Render URL.

## Practical 11: Application logging

The API logs request ID, HTTP method, path, status code, and duration. Prediction/model-loading events and exceptions are logged without writing student input values. Inspect logs with:

```bash
docker logs student-result-api
```

## Practical 12: Prometheus and Grafana

Start the complete local stack:

```bash
docker compose -f docker-compose.monitoring.yml up --build -d
docker compose -f docker-compose.monitoring.yml ps
```

Open:
- FastAPI + Swagger: `http://localhost:8000/docs`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (local demo login: admin / admin)

Grafana provisions the Prometheus data source and the Student Result API dashboard automatically. Prometheus scrapes `api:8000/metrics` every five seconds and loads alert rules from `monitoring/prometheus/alerts.yml`.

Generate traffic by calling `/health` and `/predict`, then view request rate, p95 latency, and status-code panels in Grafana. The alert rules cover API scrape failure and repeated client errors.

Stop the stack:

```bash
docker compose -f docker-compose.monitoring.yml down
```

## Important limitation

The model training data is generated synthetically by `train_model.py`. This is an academic MLOps demonstration, not a validated real-world student assessment system. Do not use its predictions for consequential academic decisions.
