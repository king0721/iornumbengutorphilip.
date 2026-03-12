import argparse
import random
import time
from pathlib import Path

from bsf_air.calculator import methane_reduction, waste_conversion
from bsf_air.control_logic import evaluate_environment
from bsf_air.logging_utils import log_data


def run_simulation(samples: int, output_file: str) -> None:
    for _ in range(samples):
        temperature = round(random.uniform(24.0, 36.0), 2)
        humidity = round(random.uniform(55.0, 80.0), 2)
        methane = random.randint(180, 420)
        larvae_growth = round(max(0.0, (temperature * 0.4 + humidity * 0.15) / 10), 3)

        path = log_data(temperature, humidity, methane, larvae_growth=larvae_growth, output_file=output_file)
        print(f"Logged sample to {path}: T={temperature}C H={humidity}% CH4={methane} Growth={larvae_growth}")
        time.sleep(0.2)


def run_calculation(waste_kg: float) -> None:
    larvae, frass = waste_conversion(waste_kg)
    avoided = methane_reduction(waste_kg)

    print(f"Input waste: {waste_kg:.2f} kg")
    print(f"Estimated larvae output: {larvae:.2f} kg")
    print(f"Estimated frass output: {frass:.2f} kg")
    print(f"Estimated methane reduction: {avoided:.2f} kg")


def run_prediction(temperature: float, humidity: float, data_file: str) -> None:
    from bsf_air.ml_model import predict_larvae_growth

    prediction = predict_larvae_growth(temperature, humidity, data_file=data_file)
    print(f"Predicted larvae growth: {prediction:.3f}")



def run_assessment(temperature: float, humidity: float, methane: float) -> None:
    decision = evaluate_environment(temperature, humidity, methane)

    print(f"Fan: {'ON' if decision.fan_on else 'OFF'}")
    print(f"Heater: {'ON' if decision.heater_on else 'OFF'}")
    print(f"Methane alert: {'YES' if decision.methane_alert else 'NO'}")


def run_api_server(host: str, port: int, reload: bool) -> None:
    try:
        import uvicorn
        import fastapi  # noqa: F401

        uvicorn.run("bsf_air.api:app", host=host, port=port, reload=reload)
        return
    except Exception as exc:
        print(f"FastAPI/Uvicorn unavailable ({exc}). Falling back to lite server.")

    from bsf_air.lite_server import run_lite_server

    if reload:
        print("--reload is ignored in lite server mode.")
    run_lite_server(host=host, port=port)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="BSF AIR smart system utility")
    sub = parser.add_subparsers(dest="command", required=True)

    sim = sub.add_parser("simulate", help="Generate synthetic sensor rows")
    sim.add_argument("--samples", type=int, default=10)
    sim.add_argument("--output", default="bsf_air_data.csv")

    calc = sub.add_parser("calculate", help="Run waste conversion and methane estimates")
    calc.add_argument("waste_kg", type=float)

    pred = sub.add_parser("predict", help="Predict larvae growth from conditions")
    pred.add_argument("temperature", type=float)
    pred.add_argument("humidity", type=float)
    pred.add_argument("--data-file", default="bsf_air_data.csv")

    assess = sub.add_parser("assess", help="Evaluate control actions from live sensor values")
    assess.add_argument("temperature", type=float)
    assess.add_argument("humidity", type=float)
    assess.add_argument("methane", type=float)

    serve = sub.add_parser("serve", help="Run the BSF AIR dashboard/API server")
    serve.add_argument("--host", default="0.0.0.0")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--reload", action="store_true")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "simulate":
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        run_simulation(samples=args.samples, output_file=str(output))
    elif args.command == "calculate":
        run_calculation(args.waste_kg)
    elif args.command == "predict":
        run_prediction(args.temperature, args.humidity, args.data_file)
    elif args.command == "assess":
        run_assessment(args.temperature, args.humidity, args.methane)
    elif args.command == "serve":
        run_api_server(host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
