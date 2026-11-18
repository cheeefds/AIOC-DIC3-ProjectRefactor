"""Data Normalizer module for Taiwan AQI observations.
Normalizes missing-value sentinels (-, --, NA, blank) to None and casts numeric columns.
"""
from typing import Any, Dict, Optional, Set

SENTINEL_VALUES: Set[str] = {"-", "--", "NA", "na", "null", "NULL", "N/A", "None", ""}

NUMERIC_COLUMNS = {
    "aqi": int,
    "site_id": int,
    "siteid": int,
    "so2": float,
    "co": float,
    "o3": float,
    "o3_8hr": float,
    "pm10": float,
    "pm2_5": float,
    "pm25": float,
    "no2": float,
    "nox": float,
    "no": float,
    "wind_speed": float,
    "wind_direction": float,
    "lon": float,
    "lat": float,
    "twd97lon": float,
    "twd97lat": float,
}

def normalize_field_name(name: str) -> str:
    """Normalize raw column headers to lowercase snake_case standard."""
    clean = name.strip().lower()
    mapping = {
        "siteid": "site_id",
        "sitename": "site_name",
        "county": "county",
        "aqi": "aqi",
        "pollutant": "pollutant",
        "status": "status",
        "so2": "so2",
        "co": "co",
        "o3": "o3",
        "o3_8hr": "o3_8hr",
        "pm10": "pm10",
        "pm2.5": "pm2_5",
        "pm2_5": "pm2_5",
        "no2": "no2",
        "nox": "nox",
        "no": "no",
        "wind_speed": "wind_speed",
        "wind_direc": "wind_direction",
        "windspeed": "wind_speed",
        "winddirec": "wind_direction",
        "datacreationdate": "data_creation_date",
        "publishtime": "data_creation_date",
        "unit": "unit",
        "co_8hr": "co_8hr",
        "pm2.5_avg": "pm2_5_avg",
        "pm10_avg": "pm10_avg",
        "so2_subindex": "so2_subindex",
        "co_subindex": "co_subindex",
        "o3_subindex": "o3_subindex",
        "o3_8hr_subindex": "o3_8hr_subindex",
        "pm10_subindex": "pm10_subindex",
        "pm2.5_subindex": "pm2_5_subindex",
        "no2_subindex": "no2_subindex",
        "twd97lon": "lon",
        "twd97lat": "lat",
        "longitude": "lon",
        "latitude": "lat",
    }
    return mapping.get(clean, clean)

def normalize_value(field_name: str, raw_value: Any) -> Optional[Any]:
    """Convert raw string values to appropriate types, turning sentinels to None."""
    if raw_value is None:
        return None
    
    val_str = str(raw_value).strip()
    if val_str in SENTINEL_VALUES:
        return None
        
    fn = field_name.lower()
    target_type = NUMERIC_COLUMNS.get(fn) or NUMERIC_COLUMNS.get(fn.replace(".", "_")) or NUMERIC_COLUMNS.get(fn.replace("_", ""))
    if target_type is not None:
        try:
            if target_type is int:
                return int(float(val_str))
            return float(val_str)
        except ValueError:
            return None
            
    return val_str

def normalize_row(raw_row: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize an entire raw CSV row dictionary."""
    normalized: Dict[str, Any] = {}
    for k, v in raw_row.items():
        if k is None:
            continue
        canon_col = normalize_field_name(k)
        normalized[canon_col] = normalize_value(canon_col, v)
    return normalized
