import csv
import datetime as dt
from pathlib import Path


HEADERS = ["timestamp", "temperature", "humidity", "methane", "larvae_growth"]


def log_data(temp: float, humidity: float, methane: int, larvae_growth: float | None = None, output_file: str = "bsf_air_data.csv") -> Path:
    """Append a sensor reading row to CSV and return the output path."""
    csv_path = Path(output_file)
    file_exists = csv_path.exists()

    with csv_path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(HEADERS)

        writer.writerow(
            [
                dt.datetime.now().isoformat(timespec="seconds"),
                temp,
                humidity,
                methane,
                "" if larvae_growth is None else larvae_growth,
            ]
        )

    return csv_path
