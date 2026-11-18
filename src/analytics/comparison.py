"""Station Comparison and Ranking module.
Compares multiple stations over identical time windows, aligns on shared timestamps, and ranks them.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set
from src.retrieval.retriever import RetrievedRow

@dataclass
class StationSummary:
    site_id: int
    site_name: str
    county: str
    valid_points: int
    mean_val: float
    max_val: float
    min_val: float
    latest_val: Optional[float]
    coverage_ratio: float  # Fraction of shared timestamps covered

@dataclass
class ComparisonResult:
    pollutant: str
    stations_ranked: List[StationSummary]
    rank_metric: str  # "mean" or "max"
    shared_timestamps_count: int
    total_distinct_timestamps: int
    max_diff: float
    alignment_warning: Optional[str]

def compare_stations(
    records: List[RetrievedRow],
    pollutant: str = "aqi",
    rank_by: str = "mean",
    align_strict_intersection: bool = True
) -> ComparisonResult:
    """Compare multiple stations across time for a given pollutant.
    
    rank_by: 'mean' or 'max'
    """
    col_name = pollutant.lower().replace(".", "_")
    
    # Group observations by site_id -> timestamp -> value
    station_data: Dict[int, Dict[str, float]] = {}
    station_meta: Dict[int, Dict[str, str]] = {}
    all_timestamps: Set[str] = set()

    for r in records:
        val = getattr(r, col_name, None)
        if val is None:
            continue
        sid = r.site_id
        if sid not in station_data:
            station_data[sid] = {}
            station_meta[sid] = {
                "site_name": r.site_name,
                "county": r.county
            }
        station_data[sid][r.timestamp] = float(val)
        all_timestamps.add(r.timestamp)

    if not station_data:
        return ComparisonResult(
            pollutant=pollutant,
            stations_ranked=[],
            rank_metric=rank_by,
            shared_timestamps_count=0,
            total_distinct_timestamps=0,
            max_diff=0.0,
            alignment_warning="無任何測站具備有效觀測數據。"
        )

    # Determine intersection of timestamps
    timestamp_sets = [set(ts_dict.keys()) for ts_dict in station_data.values()]
    shared_timestamps = set.intersection(*timestamp_sets) if timestamp_sets else set()

    alignment_warning = None
    if len(shared_timestamps) < len(all_timestamps):
        diff_count = len(all_timestamps) - len(shared_timestamps)
        alignment_warning = (
            f"注意：測站間時間戳記並未完全重疊（全集 {len(all_timestamps)} 個時段，完全交集僅 {len(shared_timestamps)} 個時段）。"
            f"為確保比較基準公平，以下統計採共同時段嚴格對齊。"
        )

    summaries: List[StationSummary] = []
    for sid, ts_dict in station_data.items():
        if align_strict_intersection and shared_timestamps:
            eval_values = [ts_dict[t] for t in shared_timestamps if t in ts_dict]
        else:
            eval_values = list(ts_dict.values())

        if not eval_values:
            continue

        mean_val = round(sum(eval_values) / len(eval_values), 4)
        max_val = round(max(eval_values), 4)
        min_val = round(min(eval_values), 4)
        latest_ts = sorted(ts_dict.keys())[-1] if ts_dict else None
        latest_val = ts_dict.get(latest_ts) if latest_ts else None
        cov_ratio = round(len(eval_values) / max(len(shared_timestamps), 1), 2)

        summaries.append(StationSummary(
            site_id=sid,
            site_name=station_meta[sid]["site_name"],
            county=station_meta[sid]["county"],
            valid_points=len(eval_values),
            mean_val=mean_val,
            max_val=max_val,
            min_val=min_val,
            latest_val=latest_val,
            coverage_ratio=cov_ratio
        ))

    # Rank descending by specified metric
    if rank_by == "max":
        summaries.sort(key=lambda s: s.max_val, reverse=True)
    else:
        summaries.sort(key=lambda s: s.mean_val, reverse=True)

    max_diff = round(summaries[0].mean_val - summaries[-1].mean_val, 4) if len(summaries) >= 2 else 0.0

    return ComparisonResult(
        pollutant=pollutant,
        stations_ranked=summaries,
        rank_metric=rank_by,
        shared_timestamps_count=len(shared_timestamps),
        total_distinct_timestamps=len(all_timestamps),
        max_diff=max_diff,
        alignment_warning=alignment_warning
    )
