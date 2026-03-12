from dataclasses import dataclass

from bsf_air.config import EnvironmentConfig


@dataclass(frozen=True)
class ControlDecision:
    fan_on: bool
    heater_on: bool
    methane_alert: bool



def evaluate_environment(
    temperature: float,
    humidity: float,
    methane: float,
    config: EnvironmentConfig | None = None,
) -> ControlDecision:
    """Convert sensor readings into actuator decisions and safety flags."""
    cfg = config or EnvironmentConfig.from_env()

    fan_on = temperature > cfg.temp_max
    heater_on = temperature < cfg.temp_min
    methane_alert = methane > cfg.methane_threshold

    # humidity kept for future decision extension (dehumidifier/misting control)
    _ = humidity

    return ControlDecision(
        fan_on=fan_on,
        heater_on=heater_on,
        methane_alert=methane_alert,
    )
