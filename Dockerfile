FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py train_model.py quality_gate.py result_logic.py ./
COPY test_app.py test_ml_pipeline.py test_result_logic.py ./

# Generate the model inside the image so the container is self-contained.
RUN python train_model.py && python quality_gate.py

EXPOSE 5000
ENV PORT=5000
CMD ["python", "app.py"]
