from __future__ import annotations

import csv
import json
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from statistics import mean
from urllib.parse import parse_qs, urlparse

from bsf_air.control_logic import evaluate_environment

DEFAULT_DATA_FILE = Path("data/bsf_air_data.csv")



def _load_rows(data_file: Path) -> list[dict[str, str]]:
    if not data_file.exists():
        return []
    with data_file.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))



def _to_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None



def readings_payload(limit: int = 50, data_file: str = str(DEFAULT_DATA_FILE)) -> dict[str, object]:
    rows = _load_rows(Path(data_file))
    sliced = rows[-max(1, min(limit, 1000)) :]
    return {"count": len(sliced), "readings": sliced}



def summary_payload(data_file: str = str(DEFAULT_DATA_FILE)) -> dict[str, object]:
    rows = _load_rows(Path(data_file))
    if not rows:
        return {
            "count": 0,
            "avg_temperature": None,
            "avg_humidity": None,
            "avg_methane": None,
            "avg_larvae_growth": None,
            "last_timestamp": None,
        }

    def _avg(name: str) -> float | None:
        values = [_to_float(row.get(name)) for row in rows]
        values = [v for v in values if v is not None]
        return round(mean(values), 3) if values else None

    return {
        "count": len(rows),
        "avg_temperature": _avg("temperature"),
        "avg_humidity": _avg("humidity"),
        "avg_methane": _avg("methane"),
        "avg_larvae_growth": _avg("larvae_growth"),
        "last_timestamp": rows[-1].get("timestamp"),
    }



def decision_payload(temperature: float, humidity: float, methane: float) -> dict[str, object]:
    decision = evaluate_environment(temperature, humidity, methane)
    return {
        "inputs": {"temperature": temperature, "humidity": humidity, "methane": methane},
        "decision": asdict(decision),
    }


DASHBOARD_HTML = """
<!doctype html>
<html>
  <head>
    <meta charset='utf-8'>
    <title>BSF AIR Dashboard (Lite)</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 2rem; background: #f7fafc; color: #1a202c; }
      .card { background: white; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
      table { width: 100%; border-collapse: collapse; }
      th, td { padding: 0.5rem; border-bottom: 1px solid #e2e8f0; text-align: left; }
      .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
      .value { font-size: 1.2rem; font-weight: bold; }
      code { background: #edf2f7; padding: 0.1rem 0.3rem; border-radius: 4px; }
    </style>
  </head>
  <body>
    <h1>BSF AIR Dashboard (Lite)</h1>
    <p>Running in no-dependency mode (stdlib HTTP server).</p>
    <div class='card grid' id='summary'></div>
    <div class='card'>
      <h2>Latest Readings</h2>
      <table>
        <thead><tr><th>Timestamp</th><th>Temp</th><th>Humidity</th><th>Methane</th><th>Growth</th></tr></thead>
        <tbody id='rows'></tbody>
      </table>
    </div>
    <script>
      async function load() {
        const summary = await fetch('/api/summary').then(r => r.json());
        const readings = await fetch('/api/readings?limit=10').then(r => r.json());

        document.getElementById('summary').innerHTML = `
          <div><div>Records</div><div class='value'>${summary.count}</div></div>
          <div><div>Avg Temp</div><div class='value'>${summary.avg_temperature ?? '-'}</div></div>
          <div><div>Avg Humidity</div><div class='value'>${summary.avg_humidity ?? '-'}</div></div>
          <div><div>Avg Methane</div><div class='value'>${summary.avg_methane ?? '-'}</div></div>
          <div><div>Avg Growth</div><div class='value'>${summary.avg_larvae_growth ?? '-'}</div></div>
        `;

        document.getElementById('rows').innerHTML = readings.readings.map(r => `
          <tr><td>${r.timestamp ?? ''}</td><td>${r.temperature ?? ''}</td><td>${r.humidity ?? ''}</td><td>${r.methane ?? ''}</td><td>${r.larvae_growth ?? ''}</td></tr>
        `).join('');
      }
      load();
      setInterval(load, 5000);
    </script>
  </body>
</html>
"""


class LiteHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict[str, object], status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/":
            self._send_html(DASHBOARD_HTML)
            return

        if parsed.path == "/health":
            self._send_json({"status": "ok", "mode": "lite"})
            return

        if parsed.path == "/api/readings":
            limit = int(params.get("limit", ["50"])[0])
            data_file = params.get("data_file", [str(DEFAULT_DATA_FILE)])[0]
            self._send_json(readings_payload(limit=limit, data_file=data_file))
            return

        if parsed.path == "/api/summary":
            data_file = params.get("data_file", [str(DEFAULT_DATA_FILE)])[0]
            self._send_json(summary_payload(data_file=data_file))
            return

        if parsed.path == "/api/decision":
            try:
                temperature = float(params.get("temperature", [""])[0])
                humidity = float(params.get("humidity", [""])[0])
                methane = float(params.get("methane", [""])[0])
            except ValueError:
                self._send_json({"error": "temperature, humidity, methane are required floats"}, status=400)
                return

            self._send_json(decision_payload(temperature, humidity, methane))
            return

        self._send_json({"error": "not found"}, status=404)



def run_lite_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), LiteHandler)
    print(f"BSF AIR lite server running on http://{host}:{port}")
    server.serve_forever()
