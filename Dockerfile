FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py train_model.py quality_gate.py result_logic.py ./
COPY test_app.py test_ml_pipeline.py test_result_logic.py ./

# Build a self-contained image with a trained and quality-checked model.
RUN python train_model.py && python quality_gate.py

EXPOSE 8000
ENV PORT=8000
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
