from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path
from statistics import mean

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from bsf_air.control_logic import evaluate_environment

app = FastAPI(title="BSF AIR API", version="1.0.0")

DEFAULT_DATA_FILE = Path("data/bsf_air_data.csv")



def _load_rows(data_file: Path) -> list[dict[str, str]]:
    if not data_file.exists():
        return []

    with data_file.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)



def _as_number(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/readings")
def get_readings(
    limit: int = Query(default=50, ge=1, le=1000),
    data_file: str = Query(default=str(DEFAULT_DATA_FILE)),
) -> dict[str, object]:
    rows = _load_rows(Path(data_file))
    sliced = rows[-limit:]
    return {"count": len(sliced), "readings": sliced}


@app.get("/api/summary")
def get_summary(data_file: str = Query(default=str(DEFAULT_DATA_FILE))) -> dict[str, object]:
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

    temps = [_as_number(r.get("temperature")) for r in rows]
    hums = [_as_number(r.get("humidity")) for r in rows]
    methane = [_as_number(r.get("methane")) for r in rows]
    growth = [_as_number(r.get("larvae_growth")) for r in rows]

    def _avg(values: list[float | None]) -> float | None:
        filtered = [v for v in values if v is not None]
        return round(mean(filtered), 3) if filtered else None

    return {
        "count": len(rows),
        "avg_temperature": _avg(temps),
        "avg_humidity": _avg(hums),
        "avg_methane": _avg(methane),
        "avg_larvae_growth": _avg(growth),
        "last_timestamp": rows[-1].get("timestamp"),
    }


@app.get("/api/decision")
def get_decision(
    temperature: float,
    humidity: float,
    methane: float,
) -> dict[str, object]:
    try:
        decision = evaluate_environment(temperature, humidity, methane)
    except Exception as exc:  # defensive
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "inputs": {
            "temperature": temperature,
            "humidity": humidity,
            "methane": methane,
        },
        "decision": asdict(decision),
    }


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return """
<!doctype html>
<html>
  <head>
    <meta charset='utf-8'>
    <title>BSF AIR Dashboard</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 2rem; background: #f7fafc; color: #1a202c; }
      .card { background: white; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
      h1 { margin-top: 0; }
      table { width: 100%; border-collapse: collapse; }
      th, td { padding: 0.5rem; border-bottom: 1px solid #e2e8f0; text-align: left; }
      .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
      .value { font-size: 1.3rem; font-weight: bold; }
    </style>
  </head>
  <body>
    <h1>BSF AIR Dashboard</h1>
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

        const summaryEl = document.getElementById('summary');
        summaryEl.innerHTML = `
          <div><div>Records</div><div class='value'>${summary.count}</div></div>
          <div><div>Avg Temp</div><div class='value'>${summary.avg_temperature ?? '-'}</div></div>
          <div><div>Avg Humidity</div><div class='value'>${summary.avg_humidity ?? '-'}</div></div>
          <div><div>Avg Methane</div><div class='value'>${summary.avg_methane ?? '-'}</div></div>
          <div><div>Avg Growth</div><div class='value'>${summary.avg_larvae_growth ?? '-'}</div></div>
        `;

        const rowsEl = document.getElementById('rows');
        rowsEl.innerHTML = readings.readings.map(r => `
          <tr>
            <td>${r.timestamp ?? ''}</td>
            <td>${r.temperature ?? ''}</td>
            <td>${r.humidity ?? ''}</td>
            <td>${r.methane ?? ''}</td>
            <td>${r.larvae_growth ?? ''}</td>
          </tr>
        `).join('');
      }
      load();
      setInterval(load, 5000);
    </script>
  </body>
</html>
    """
