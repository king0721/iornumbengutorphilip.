import csv
import tempfile
import unittest
from pathlib import Path

from bsf_air.calculator import methane_reduction, waste_conversion
from bsf_air.config import EnvironmentConfig
from bsf_air.control_logic import evaluate_environment
from bsf_air.logging_utils import log_data
from bsf_air.serial_ingest import parse_data_line


class TestBSFAir(unittest.TestCase):
    def test_waste_conversion_and_methane_reduction(self) -> None:
        larvae, frass = waste_conversion(100)
        self.assertEqual(larvae, 20)
        self.assertEqual(frass, 50)
        self.assertEqual(methane_reduction(100), 6)

    def test_control_logic_thresholds(self) -> None:
        cfg = EnvironmentConfig(temp_min=25, temp_max=35, methane_threshold=300)
        decision = evaluate_environment(temperature=36, humidity=60, methane=301, config=cfg)
        self.assertTrue(decision.fan_on)
        self.assertFalse(decision.heater_on)
        self.assertTrue(decision.methane_alert)

    def test_log_data_writes_headers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.csv"
            log_data(30, 70, 250, larvae_growth=2.3, output_file=str(out))

            with out.open("r", encoding="utf-8") as f:
                rows = list(csv.reader(f))

            self.assertEqual(rows[0], ["timestamp", "temperature", "humidity", "methane", "larvae_growth"])
            self.assertEqual(rows[1][1:], ["30", "70", "250", "2.3"])

    def test_parse_data_line(self) -> None:
        self.assertEqual(parse_data_line("DATA,30.2,70.1,310"), (30.2, 70.1, 310))
        self.assertIsNone(parse_data_line("hello"))


if __name__ == "__main__":
    unittest.main()
