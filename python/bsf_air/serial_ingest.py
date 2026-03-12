import argparse

from bsf_air.logging_utils import log_data


def parse_data_line(line: str) -> tuple[float, float, int] | None:
    # Expected format from firmware: DATA,temp,humidity,methane
    if not line.startswith("DATA,"):
        return None

    parts = line.strip().split(",")
    if len(parts) != 4:
        return None

    _, temp, humidity, methane = parts
    return float(temp), float(humidity), int(methane)


def run(port: str, baud_rate: int, output_file: str) -> None:
    import serial

    with serial.Serial(port, baud_rate, timeout=1) as ser:
        print(f"Listening on {port} @ {baud_rate}...")
        while True:
            line = ser.readline().decode(errors="ignore").strip()
            if not line:
                continue

            parsed = parse_data_line(line)
            if parsed:
                temp, humidity, methane = parsed
                log_data(temp, humidity, methane, output_file=output_file)
                print(f"Logged from device: T={temp} H={humidity} CH4={methane}")
            else:
                print(line)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest BSF AIR readings from ESP32 serial output")
    parser.add_argument("--port", required=True, help="Serial port (e.g., /dev/ttyUSB0 or COM3)")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--output", default="bsf_air_data.csv")
    args = parser.parse_args()

    run(args.port, args.baud, args.output)


if __name__ == "__main__":
    main()
