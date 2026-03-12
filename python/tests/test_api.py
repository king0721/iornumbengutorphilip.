import unittest


class TestAPI(unittest.TestCase):
    def setUp(self) -> None:
        try:
            from fastapi.testclient import TestClient
            from bsf_air.api import app
        except Exception as exc:  # optional dependency
            self.skipTest(f"FastAPI test dependencies unavailable: {exc}")

        self.client = TestClient(app)

    def test_health(self) -> None:
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 'ok')

    def test_decision_endpoint(self) -> None:
        response = self.client.get('/api/decision?temperature=36&humidity=70&methane=350')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['decision']['fan_on'])
        self.assertTrue(payload['decision']['methane_alert'])


if __name__ == '__main__':
    unittest.main()
