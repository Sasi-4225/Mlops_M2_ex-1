import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import app


class TestPredictionApplication(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertIn("X-Request-ID", response.headers)

    def test_health_endpoint(self):
        # The CI workflow trains the model before running this test.
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    @patch("app.load_model")
    def test_high_performance_prediction(self, load_model):
        class DummyModel:
            def predict(self, sample):
                return [1]
        load_model.return_value = DummyModel()
        response = self.client.post(
            "/predict",
            json={"attendance": 90, "internal_marks": 85, "assignment_marks": 88, "previous_score": 80},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["prediction"], "PASS")

    @patch("app.load_model")
    def test_low_performance_prediction(self, load_model):
        class DummyModel:
            def predict(self, sample):
                return [0]
        load_model.return_value = DummyModel()
        response = self.client.post(
            "/predict",
            json={"attendance": 55, "internal_marks": 30, "assignment_marks": 40, "previous_score": 35},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["prediction"], "FAIL")

    def test_missing_fields(self):
        response = self.client.post("/predict", json={"attendance": 90, "internal_marks": 85})
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())

    def test_non_numeric_input(self):
        response = self.client.post(
            "/predict",
            json={"attendance": "high", "internal_marks": 85, "assignment_marks": 88, "previous_score": 80},
        )
        self.assertEqual(response.status_code, 422)

    def test_out_of_range_input(self):
        response = self.client.post(
            "/predict",
            json={"attendance": 150, "internal_marks": 85, "assignment_marks": 88, "previous_score": 80},
        )
        self.assertEqual(response.status_code, 422)

    def test_metrics_endpoint(self):
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertIn("student_result_http_requests_total", response.text)


if __name__ == "__main__":
    unittest.main()
