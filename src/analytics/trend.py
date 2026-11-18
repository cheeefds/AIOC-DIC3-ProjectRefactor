"""Deterministic Trend Analytics module.
Computes net difference, percentage change, min, max, average, and direction (increasing, decreasing, stable).
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from src.retrieval.retriever import RetrievedRow

@dataclass
class TrendResult:
    pollutant: str
    site_id: int
    site_name: str
    is_valid: bool
    data_points_count: int
    start_time: Optional[str]
    end_time: Optional[str]
    start_val: Optional[float]
    end_val: Optional[float]
    net_delta: Optional[float]
    pct_change: Optional[float]  # Percentage e.g. +25.0%
    min_val: Optional[float]
    min_time: Optional[str]
    max_val: Optional[float]
    max_time: Optional[str]
    mean_val: Optional[float]
    direction: str  # "上升", "下降", "平穩", "資料不足"
    limitation_warning: Optional[str]

def calculate_trend(
    records: List[RetrievedRow],
    pollutant: str = "pm2_5",
    stable_threshold: float = 0.5
) -> TrendResult:
    """Calculate deterministic trend metrics for a specific pollutant.
    
    stable_threshold: if absolute delta <= stable_threshold, classified as "平穩".
    """
    col_name = pollutant.lower().replace(".", "_")
    valid_points: List[Tuple[str, float]] = []

    site_id = records[0].site_id if records else 0
    site_name = records[0].site_name if records else ""

    for r in records:
        val = getattr(r, col_name, None)
        if val is not None:
            valid_points.append((r.timestamp, float(val)))

    if len(valid_points) < 2:
        return TrendResult(
            pollutant=pollutant,
            site_id=site_id,
            site_name=site_name,
            is_valid=False,
            data_points_count=len(valid_points),
            start_time=valid_points[0][0] if valid_points else None,
            end_time=valid_points[-1][0] if valid_points else None,
            start_val=valid_points[0][1] if valid_points else None,
            end_val=valid_points[-1][1] if valid_points else None,
            net_delta=None,
            pct_change=None,
            min_val=valid_points[0][1] if valid_points else None,
            min_time=valid_points[0][0] if valid_points else None,
            max_val=valid_points[0][1] if valid_points else None,
            max_time=valid_points[0][0] if valid_points else None,
            mean_val=valid_points[0][1] if valid_points else None,
            direction="資料不足",
            limitation_warning=f"有效觀測筆數不足（僅 {len(valid_points)} 筆，至少需 2 筆），無法計算趨勢變化。"
        )

    start_time, start_val = valid_points[0]
    end_time, end_val = valid_points[-1]
    net_delta = round(end_val - start_val, 4)

    if abs(start_val) > 1e-6:
        pct_change = round((net_delta / start_val) * 100.0, 2)
    else:
        pct_change = None

    # Min / Max / Mean
    min_point = min(valid_points, key=lambda x: x[1])
    max_point = max(valid_points, key=lambda x: x[1])
    mean_val = round(sum(p[1] for p in valid_points) / len(valid_points), 4)

    if abs(net_delta) <= stable_threshold:
        direction = "平穩"
    elif net_delta > 0:
        direction = "上升"
    else:
        direction = "下降"

    return TrendResult(
        pollutant=pollutant,
        site_id=site_id,
        site_name=site_name,
        is_valid=True,
        data_points_count=len(valid_points),
        start_time=start_time,
        end_time=end_time,
        start_val=round(start_val, 4),
        end_val=round(end_val, 4),
        net_delta=net_delta,
        pct_change=pct_change,
        min_val=round(min_point[1], 4),
        min_time=min_point[0],
        max_val=round(max_point[1], 4),
        max_time=max_point[0],
        mean_val=mean_val,
        direction=direction,
        limitation_warning=None
    )
