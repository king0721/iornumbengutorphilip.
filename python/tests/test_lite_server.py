import unittest

from bsf_air.lite_server import decision_payload, readings_payload, summary_payload


class TestLiteServer(unittest.TestCase):
    def test_summary_payload_has_count(self) -> None:
        payload = summary_payload(data_file="data/bsf_air_data.csv")
        self.assertIn("count", payload)
        self.assertGreaterEqual(payload["count"], 0)

    def test_readings_payload_limit(self) -> None:
        payload = readings_payload(limit=2, data_file="data/bsf_air_data.csv")
        self.assertLessEqual(payload["count"], 2)
        self.assertEqual(payload["count"], len(payload["readings"]))

    def test_decision_payload(self) -> None:
        payload = decision_payload(temperature=40, humidity=70, methane=350)
        self.assertTrue(payload["decision"]["fan_on"])
        self.assertTrue(payload["decision"]["methane_alert"])


if __name__ == "__main__":
    unittest.main()
