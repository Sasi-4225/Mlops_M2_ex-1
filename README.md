# Student Result Prediction — MLOps Practicals 5–10

This repository extends a student-result model training pipeline into a tested API, release package, Docker image, GHCR publication workflow, and cloud deployment instructions.

## Architecture

1. **Practical 5 — Continuous Delivery:** train/evaluate the model, enforce an accuracy quality gate, run tests, and upload a release candidate.
2. **Practical 7 — Docker CI:** build a container and test API endpoints in GitHub Actions.
3. **Practical 8 — GHCR:** publish a tested image to GitHub Container Registry.
4. **Practical 9 — Automated GHCR publishing:** publish `latest` and commit-specific `sha-...` tags only when tests pass.
5. **Practical 10 — Render:** deploy the published container image as a Render Web Service.

The API follows the Flask/port-5000 contract used in Practicals 5 and 7. Some later handouts show FastAPI/port-8000 examples; do not mix those commands with this Flask implementation.

## Local setup

Requires Python 3.11+ and Docker for container steps.

```bash
python -m pip install -r requirements.txt
python train_model.py
python quality_gate.py
python -m unittest discover -v
python app.py
```

Test endpoints:
- Root: `GET http://localhost:5000/`
- Health: `GET http://localhost:5000/health`
- Prediction: `POST http://localhost:5000/predict`

Example request:

```json
{
  "attendance": 90,
  "internal_marks": 85,
  "assignment_marks": 88,
  "previous_score": 80
}
```

## Docker

```bash
docker build -t student-result-prediction:local .
docker run --rm -p 5000:5000 student-result-prediction:local
```

The Docker image trains and validates its bundled model during build, making the image self-contained.

## GHCR

The workflow at `.github/workflows/docker-publish.yml` uses GitHub Actions' built-in `GITHUB_TOKEN`. Ensure repository Actions are enabled. For an existing GHCR package, grant this repository write access in the package's **Manage Actions access** settings. The package must be public for a credential-free Render pull; otherwise configure a registry credential in Render with package read permission.

Published references:
- `ghcr.io/sasi-4225/student-result-prediction:latest`
- `ghcr.io/sasi-4225/student-result-prediction:sha-<commit-sha>`

## Render deployment (Practical 10)

Create a Render **Web Service → Existing Image** and use:
- Image: `ghcr.io/sasi-4225/student-result-prediction:latest`
- `PORT=5000`
- Health-check path: `/health`

If the image is private, configure a registry credential with read-only package access. After a new image is pushed, manually deploy the updated image if Render does not automatically refresh the image-backed service. Record the actual Render URL only after deployment and verify `/`, `/health`, and `/predict`.

## Notes

- The dataset is generated synthetically by `train_model.py`; this is an educational pipeline, not a validated real-world student assessment system.
- The API expects four numeric inputs in the range 0–100.
- Never commit access tokens or other secrets to this repository.
