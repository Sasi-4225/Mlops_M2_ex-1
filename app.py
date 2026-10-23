from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request

app = Flask(__name__)
MODEL_PATH = Path('student_result_model.pkl')
FEATURES = ['attendance', 'internal_marks', 'assignment_marks', 'previous_score']

def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError('student_result_model.pkl is missing. Run train_model.py first.')
    return joblib.load(MODEL_PATH)

@app.get('/')
def root():
    return jsonify({'status': 'ok', 'service': 'student-result-prediction', 'health': '/health', 'prediction': '/predict'})

@app.get('/health')
def health():
    if not MODEL_PATH.exists():
        return jsonify({'status': 'error', 'message': 'model artifact missing'}), 503
    return jsonify({'status': 'ok', 'service': 'student-result-prediction'})

@app.post('/predict')
def predict():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'JSON request body is required'}), 400
    missing = [feature for feature in FEATURES if feature not in data]
    if missing:
        return jsonify({'error': 'Missing required fields', 'missing_fields': missing}), 400
    try:
        sample = pd.DataFrame([{feature: float(data[feature]) for feature in FEATURES}])
    except (TypeError, ValueError):
        return jsonify({'error': 'All feature values must be numeric'}), 400
    for feature in FEATURES:
        if not 0 <= sample.iloc[0][feature] <= 100:
            return jsonify({'error': feature + ' must be between 0 and 100'}), 400
    model = load_model()
    prediction_code = int(model.predict(sample)[0])
    return jsonify({'prediction': 'PASS' if prediction_code == 1 else 'FAIL', 'prediction_code': prediction_code})

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')))
