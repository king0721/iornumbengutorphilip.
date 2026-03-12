import csv
from pathlib import Path
from typing import Iterable

try:
    import pandas as pd
    from sklearn.linear_model import LinearRegression
except Exception:  # Optional dependency path
    pd = None
    LinearRegression = None


REQUIRED_COLUMNS = {"temperature", "humidity", "larvae_growth"}


class SimpleGrowthModel:
    """Fallback linear model: y = a*temperature + b*humidity + c"""

    def __init__(self, a: float, b: float, c: float):
        self.a = a
        self.b = b
        self.c = c

    def predict(self, X: Iterable[Iterable[float]]):
        return [self.a * row[0] + self.b * row[1] + self.c for row in X]


def _solve_3x3(matrix: list[list[float]], vector: list[float]) -> tuple[float, float, float]:
    """Solve Ax=b using Gaussian elimination for a 3x3 matrix."""
    a = [row[:] for row in matrix]
    b = vector[:]

    for i in range(3):
        pivot = a[i][i]
        if abs(pivot) < 1e-12:
            raise ValueError("Singular matrix; cannot solve regression coefficients.")
        for j in range(i, 3):
            a[i][j] /= pivot
        b[i] /= pivot

        for k in range(3):
            if k == i:
                continue
            factor = a[k][i]
            for j in range(i, 3):
                a[k][j] -= factor * a[i][j]
            b[k] -= factor * b[i]

    return b[0], b[1], b[2]


def _train_fallback(data_file: str):
    data_path = Path(data_file)
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    with data_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV has no headers.")

        missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        rows = [row for row in reader if row["temperature"] and row["humidity"] and row["larvae_growth"]]

    if not rows:
        raise ValueError("No rows available after removing missing values.")

    x1 = [float(r["temperature"]) for r in rows]
    x2 = [float(r["humidity"]) for r in rows]
    y = [float(r["larvae_growth"]) for r in rows]
    n = len(rows)

    s_x1 = sum(x1)
    s_x2 = sum(x2)
    s_y = sum(y)
    s_x1x1 = sum(v * v for v in x1)
    s_x2x2 = sum(v * v for v in x2)
    s_x1x2 = sum(a * b for a, b in zip(x1, x2))
    s_x1y = sum(a * b for a, b in zip(x1, y))
    s_x2y = sum(a * b for a, b in zip(x2, y))

    matrix = [
        [s_x1x1, s_x1x2, s_x1],
        [s_x1x2, s_x2x2, s_x2],
        [s_x1, s_x2, n],
    ]
    vector = [s_x1y, s_x2y, s_y]

    a_coef, b_coef, c_coef = _solve_3x3(matrix, vector)
    return SimpleGrowthModel(a_coef, b_coef, c_coef)


def train_growth_model(data_file: str = "bsf_air_data.csv"):
    if pd is not None and LinearRegression is not None:
        data_path = Path(data_file)
        if not data_path.exists():
            raise FileNotFoundError(f"Dataset not found: {data_path}")

        data = pd.read_csv(data_path)
        missing = REQUIRED_COLUMNS.difference(data.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        cleaned = data.dropna(subset=["temperature", "humidity", "larvae_growth"])
        if cleaned.empty:
            raise ValueError("No rows available after removing missing values.")

        X = cleaned[["temperature", "humidity"]]
        y = cleaned["larvae_growth"]

        model = LinearRegression()
        model.fit(X, y)
        return model

    return _train_fallback(data_file)


def predict_larvae_growth(temperature: float, humidity: float, data_file: str = "bsf_air_data.csv") -> float:
    model = train_growth_model(data_file=data_file)
    prediction = model.predict([[temperature, humidity]])
    return float(prediction[0])
