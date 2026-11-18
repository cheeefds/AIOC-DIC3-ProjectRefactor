"""Persistence Baseline module.
Assumes reading at t_0 persists unchanged throughout the interval and computes deviations/residuals.
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple
from src.retrieval.retriever import RetrievedRow

@dataclass
class BaselinePoint:
    timestamp: str
    observed_value: float
    baseline_value: float
    residual: float  # observed - baseline
    abs_residual: float

@dataclass
class PersistenceBaselineResult:
    pollutant: str
    site_id: int
    site_name: str
    t0_timestamp: str
    t0_value: float
    points: List[BaselinePoint]
    mean_absolute_deviation: float
    max_positive_deviation: float
    max_negative_deviation: float
    max_deviation_time: str
    limitation_warning: Optional[str]

def calculate_persistence_baseline(
    records: List[RetrievedRow],
    pollutant: str = "pm2_5"
) -> Optional[PersistenceBaselineResult]:
    """Calculate persistence baseline (t0 persistent prediction) and residuals."""
    col_name = pollutant.lower().replace(".", "_")
    valid_points: List[Tuple[str, float]] = []

    site_id = records[0].site_id if records else 0
    site_name = records[0].site_name if records else ""

    for r in records:
        val = getattr(r, col_name, None)
        if val is not None:
            valid_points.append((r.timestamp, float(val)))

    if not valid_points:
        return None

    t0_ts, t0_val = valid_points[0]
    points: List[BaselinePoint] = []
    abs_residuals = []

    for ts, obs in valid_points:
        res = round(obs - t0_val, 4)
        abs_res = round(abs(res), 4)
        abs_residuals.append(abs_res)
        points.append(BaselinePoint(
            timestamp=ts,
            observed_value=obs,
            baseline_value=t0_val,
            residual=res,
            abs_residual=abs_res
        ))

    mad = round(sum(abs_residuals) / len(abs_residuals), 4)
    max_point = max(points, key=lambda p: abs(p.residual))
    pos_dev = max([p.residual for p in points], default=0.0)
    neg_dev = min([p.residual for p in points], default=0.0)

    return PersistenceBaselineResult(
        pollutant=pollutant,
        site_id=site_id,
        site_name=site_name,
        t0_timestamp=t0_ts,
        t0_value=t0_val,
        points=points,
        mean_absolute_deviation=mad,
        max_positive_deviation=round(pos_dev, 4),
        max_negative_deviation=round(neg_dev, 4),
        max_deviation_time=max_point.timestamp,
        limitation_warning=None if len(valid_points) >= 2 else "僅有單一觀測點，無時序偏差。"
    )
