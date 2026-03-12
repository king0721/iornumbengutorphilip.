from dataclasses import dataclass
import os


@dataclass(frozen=True)
class EnvironmentConfig:
    temp_min: float = 25.0
    temp_max: float = 35.0
    methane_threshold: float = 300.0

    @staticmethod
    def from_env() -> "EnvironmentConfig":
        return EnvironmentConfig(
            temp_min=float(os.getenv("BSF_TEMP_MIN", 25.0)),
            temp_max=float(os.getenv("BSF_TEMP_MAX", 35.0)),
            methane_threshold=float(os.getenv("BSF_METHANE_THRESHOLD", 300.0)),
        )
