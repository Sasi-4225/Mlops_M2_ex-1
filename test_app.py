import unittest
from unittest.mock import patch

from app import app

class TestPredictionApplication(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_root_endpoint(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'ok')

    @patch('app.MODEL_PATH.exists', return_value=True)
    def test_health_endpoint(self, _exists):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'ok')

    @patch('app.load_model')
    def test_high_performance_prediction(self, load_model):
        class DummyModel:
            def predict(self, sample):
                return [1]
        load_model.return_value = DummyModel()
        response = self.client.post('/predict', json={'attendance': 90, 'internal_marks': 85, 'assignment_marks': 88, 'previous_score': 80})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['prediction'], 'PASS')

    @patch('app.load_model')
    def test_low_performance_prediction(self, load_model):
        class DummyModel:
            def predict(self, sample):
                return [0]
        load_model.return_value = DummyModel()
        response = self.client.post('/predict', json={'attendance': 55, 'internal_marks': 30, 'assignment_marks': 40, 'previous_score': 35})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['prediction'], 'FAIL')

    def test_missing_fields(self):
        response = self.client.post('/predict', json={'attendance': 90, 'internal_marks': 85})
        self.assertEqual(response.status_code, 400)
        self.assertIn('missing_fields', response.get_json())

    def test_non_numeric_input(self):
        response = self.client.post('/predict', json={'attendance': 'high', 'internal_marks': 85, 'assignment_marks': 88, 'previous_score': 80})
        self.assertEqual(response.status_code, 400)

    def test_out_of_range_input(self):
        response = self.client.post('/predict', json={'attendance': 150, 'internal_marks': 85, 'assignment_marks': 88, 'previous_score': 80})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
