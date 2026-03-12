# BSF AIR (Black Soldier Fly – Anaerobic Integrated Reactor) Smart System

This repository now contains a runnable **technical code package** for your BSF AIR plug-and-play workflow:

- ESP32 firmware for environmental monitoring and control.
- ESP32 firmware for solar/biogas power switching logic.
- Python utilities for data logging, ingestion, waste conversion estimation, methane reduction estimation, and AI-based larvae growth prediction.

## Repository Layout

- `firmware/environment_monitoring.ino` – DHT22 + MQ4 monitoring, fan/heater control, methane warning.
- `firmware/energy_switching.ino` – solar priority with biogas fallback.
- `python/bsf_air/logging_utils.py` – CSV logger.
- `python/bsf_air/config.py` – configurable thresholds (env-based).
- `python/bsf_air/control_logic.py` – runtime actuator decision logic.
- `python/bsf_air/serial_ingest.py` – listens to serial output from ESP32 and logs data.
- `python/bsf_air/calculator.py` – waste conversion + methane reduction estimators.
- `python/bsf_air/ml_model.py` – linear regression model for larvae growth prediction.
- `python/bsf_air/main.py` – command-line runner for simulation, calculation, prediction, control assessment, and API server.
- `python/bsf_air/api.py` – FastAPI backend + built-in web dashboard.
- `python/tests/test_bsf_air.py` – automated tests for core behavior.
- `python/requirements.txt` – dependencies.

## Quick Start (Python)

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 1) Generate sample data

```bash
PYTHONPATH=. python -m bsf_air.main simulate --samples 20 --output data/bsf_air_data.csv
```

### 2) Run conversion and methane estimates

```bash
PYTHONPATH=. python -m bsf_air.main calculate 100
```

### 3) Predict larvae growth

```bash
PYTHONPATH=. python -m bsf_air.main predict 30 70 --data-file data/bsf_air_data.csv
```

### 4) Ingest data from ESP32 serial (real hardware)

```bash
PYTHONPATH=. python -m bsf_air.serial_ingest --port /dev/ttyUSB0 --baud 115200 --output data/bsf_air_data.csv
```

### 5) Evaluate control decisions from live values

```bash
PYTHONPATH=. python -m bsf_air.main assess 34 72 280
```

### 6) Run tests

```bash
PYTHONPATH=. pytest -q
```

### 7) Run dashboard/API

```bash
PYTHONPATH=. python -m bsf_air.main serve --host 0.0.0.0 --port 8000
```

> If `fastapi`/`uvicorn` are not installable (e.g., proxy-restricted environment), the command automatically falls back to a built-in **lite server** with the same routes using only Python standard library.

Then open:
- Dashboard: `http://localhost:8000/`
- Health: `http://localhost:8000/health`
- Readings API: `http://localhost:8000/api/readings?limit=10`
- Summary API: `http://localhost:8000/api/summary`
- Decision API: `http://localhost:8000/api/decision?temperature=34&humidity=72&methane=280`

### Dependency/Proxy Troubleshooting

If `pip install` fails behind a proxy (403), use one of these:

1. Configure pip proxy/index:
```bash
pip config set global.proxy http://<proxy-host>:<proxy-port>
pip config set global.index-url https://<your-internal-pypi>/simple
```
2. Install from local wheelhouse:
```bash
pip install --no-index --find-links ./wheelhouse fastapi uvicorn
```
3. Use built-in lite server (no extra deps):
```bash
PYTHONPATH=. python -m bsf_air.main serve --host 0.0.0.0 --port 8000
```

### Screenshot Validation Tips

To avoid capturing a non-app page:
- start server first in repo `python/` directory,
- open `http://127.0.0.1:8000/health` and confirm JSON response,
- then capture `http://127.0.0.1:8000/`.

## Firmware Notes

### Environmental Monitoring Firmware

- Reads:
  - DHT22 temperature/humidity
  - MQ4 methane analog value
- Controls:
  - `FAN_PIN` when temperature exceeds `tempMax`
  - `HEATER_PIN` when temperature is below `tempMin`
- Emits machine-readable serial lines in format:

```text
DATA,<temperature>,<humidity>,<methane>
```

These lines are consumed by `serial_ingest.py`.

### Energy Switching Firmware

- If solar sensor value is above threshold: runs on solar.
- Otherwise: enables biogas valve and switches to biogas power.

## What You Still Need to Add (Priority Checklist)

To make BSF AIR truly production plug-and-play, add these next:

1. **Hardware abstraction layer** for sensor calibration and pin-mapping profiles per board variant.
2. **Fail-safe rules** (e.g., methane emergency vent, heater lockout, watchdog reboot).
3. **Persistent device config** (thresholds editable from UI/API and synced to ESP32).
4. **Alerting workflows** (SMS/WhatsApp/email hooks + escalation policy).
5. **Deployment automation** (`systemd` service, startup scripts, and offline install bundle).
6. **Data QA + model lifecycle** (outlier filtering, versioned models, retraining schedule).
