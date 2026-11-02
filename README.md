# Student Result Prediction — MLOps Practicals 1–12

This repository demonstrates an end-to-end educational MLOps workflow for a Student Result Prediction model. The API framework is **FastAPI** throughout, using port **8000**.

## Practical roadmap

| Practical | Implementation |
|---|---|
| 1 | Basic Python CI and automated unit tests |
| 2 | Automated model training and ML pipeline tests |
| 3 | Model-quality gate using a minimum accuracy threshold |
| 4 | Save and upload the trained model, metrics, and dataset as workflow artifacts |
| 5 | Continuous Delivery of a validated release candidate |
| 6 | Dockerize the FastAPI application |
| 7 | GitHub Actions builds and tests the Docker container |
| 8 | Publish and pull the container image through GitHub Container Registry (GHCR) |
| 9 | Automate Docker build, test, tagging, and GHCR publishing |
| 10 | Deploy the GHCR image to Render |
| 11 | Add structured application logs, request IDs, and request-duration logs |
| 12 | Export Prometheus metrics and visualize them with Grafana |

## Architecture

`train_model.py` creates the educational dataset, trains the model, and writes `student_result_model.pkl` and `metrics.json`. `quality_gate.py` checks the configured minimum accuracy. GitHub Actions runs the tests and packages validated artifacts. Docker packages the FastAPI service and model. The publishing workflow pushes tested images to GHCR. Render can run the published image. Prometheus scrapes the API metrics and Grafana visualizes them.

## Local setup

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
- Root: `GET http://localhost:8000/`
- Health: `GET http://localhost:8000/health`
- Prediction: `POST http://localhost:8000/predict`
- Swagger documentation: `http://localhost:8000/docs`
- Prometheus metrics: `GET http://localhost:8000/metrics`

Example prediction request:

```json
{
  "attendance": 90,
  "internal_marks": 85,
  "assignment_marks": 88,
  "previous_score": 80
}
```

The four inputs must be numeric values between 0 and 100. FastAPI returns HTTP 422 for invalid or missing input fields.

## Docker — Practicals 6 and 7

```bash
docker build -t student-result-prediction:local .
docker run --rm -p 8000:8000 student-result-prediction:local
```

The image trains and validates its bundled model during the Docker build. Test `http://localhost:8000/health` and send the example JSON to `/predict`.

## GHCR — Practicals 8 and 9

The workflow `.github/workflows/docker-publish.yml` builds the image, runs health and prediction checks, checks the metrics endpoint, and publishes `latest` and commit-specific tags to GHCR after successful checks.

Image name:
`ghcr.io/sasi-4225/student-result-prediction:latest`

For manual GHCR publishing (Practical 8), authenticate with a GitHub token that has package write permission, then tag and push the locally tested image. Never commit tokens to the repository. For automated publishing (Practical 9), GitHub Actions uses the repository's `GITHUB_TOKEN`; the workflow grants `packages: write`.

## Render — Practical 10

Create a Render **Web Service** using the existing GHCR image:
`ghcr.io/sasi-4225/student-result-prediction:latest`

Set `PORT=8000` and health-check path `/health`. If the GHCR package is private, configure a registry credential with read-only package access. After a new image is published, redeploy the image-backed service as required by Render. Verify `/`, `/health`, `/docs`, and `/predict` using the actual deployed URL. Do not record a deployment URL until the service has been deployed and tested.

## Logging — Practical 11

The FastAPI middleware logs request ID, HTTP method, path, status code, and duration. Prediction and model-loading events are logged. Invalid request details and student inputs are not written to logs. View container logs with:

```bash
docker logs <container-name>
```

## Prometheus and Grafana — Practical 12

Start the local monitoring stack:

```bash
docker compose -f docker-compose.monitoring.yml up --build
```

- FastAPI: `http://localhost:8000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (default local admin credentials: admin / admin; change them for any shared environment)

Prometheus scrapes `api:8000/metrics`. A provisioned Grafana dashboard displays request volume and request latency. This local Compose monitoring stack is for demonstration; the Prometheus/Grafana containers are not deployed by the Render API service.

## Important limitation

The dataset is generated synthetically by `train_model.py`. This is an academic demonstration of an MLOps pipeline, not a validated real-world student assessment system. Do not use its predictions for consequential academic decisions.
