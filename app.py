from functools import lru_cache
from pathlib import Path
import logging
import time
import uuid

import joblib
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("student_result_api")

MODEL_PATH = Path("student_result_model.pkl")
FEATURES = ["attendance", "internal_marks", "assignment_marks", "previous_score"]

REQUEST_COUNT = Counter(
    "student_result_http_requests_total",
    "Total HTTP requests handled by the Student Result API",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "student_result_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

app = FastAPI(
    title="Student Result Prediction API",
    description="Predicts PASS or FAIL from four student performance inputs.",
    version="1.0.0",
)


class PredictionInput(BaseModel):
    attendance: float = Field(ge=0, le=100, description="Attendance percentage")
    internal_marks: float = Field(ge=0, le=100, description="Internal marks")
    assignment_marks: float = Field(ge=0, le=100, description="Assignment marks")
    previous_score: float = Field(ge=0, le=100, description="Previous score")


@lru_cache(maxsize=1)
def load_model():
    if not MODEL_PATH.exists():
        logger.error("model_artifact_missing path=%s", MODEL_PATH)
        raise FileNotFoundError("student_result_model.pkl is missing. Run train_model.py first.")
    logger.info("model_loaded path=%s", MODEL_PATH)
    return joblib.load(MODEL_PATH)


@app.middleware("http")
async def request_observability(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    started = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception:
        logger.exception(
            "request_failed request_id=%s method=%s path=%s",
            request_id, request.method, request.url.path,
        )
        raise
    finally:
        elapsed = time.perf_counter() - started
        path = request.url.path
        REQUEST_COUNT.labels(request.method, path, str(status_code)).inc()
        REQUEST_LATENCY.labels(request.method, path).observe(elapsed)
        logger.info(
            "request_completed request_id=%s method=%s path=%s status_code=%s duration_ms=%.2f",
            request_id, request.method, path, status_code, elapsed * 1000,
        )


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "student-result-prediction",
        "health": "/health",
        "prediction": "/predict",
        "documentation": "/docs",
        "metrics": "/metrics",
    }


@app.get("/health")
def health():
    if not MODEL_PATH.exists():
        logger.warning("health_check_failed reason=model_artifact_missing")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "model artifact missing"},
        )
    return {"status": "ok", "service": "student-result-prediction"}


@app.post("/predict")
def predict(payload: PredictionInput):
    try:
        sample = pd.DataFrame([payload.model_dump()])
        prediction_code = int(load_model().predict(sample)[0])
        result = "PASS" if prediction_code == 1 else "FAIL"
        logger.info("prediction_completed prediction=%s", result)
        return {"prediction": result, "prediction_code": prediction_code}
    except FileNotFoundError as exc:
        logger.error("prediction_unavailable reason=model_artifact_missing")
        return JSONResponse(status_code=503, content={"error": str(exc)})
    except Exception:
        logger.exception("prediction_failed")
        return JSONResponse(
            status_code=500,
            content={"error": "Prediction could not be completed"},
        )


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
