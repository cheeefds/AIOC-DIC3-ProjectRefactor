"""Time-series observation retrieval engine with row-level provenance tracking.
Retrieves observations by SiteId (or list of SiteIds) and [T_start, T_end].
"""
import csv
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from src.retrieval.stations import get_station_by_id

@dataclass
class RetrievedRow:
    site_id: int
    site_name: str
    county: str
    timestamp: str  # Original DataCreationDate (Taiwan Time)
    dt: Optional[datetime]
    aqi: Optional[int]
    pollutant: Optional[str]
    status: Optional[str]
    so2: Optional[float]
    co: Optional[float]
    o3: Optional[float]
    o3_8hr: Optional[float]
    pm10: Optional[float]
    pm2_5: Optional[float]
    no2: Optional[float]
    nox: Optional[float]
    no: Optional[float]
    wind_speed: Optional[float]
    wind_direction: Optional[float]
    source_file: str
    record_key: str  # Composite key: (SiteId, DataCreationDate)
    raw_dict: Dict[str, Any]

@dataclass
class RetrievalResult:
    query_site_ids: List[int]
    t_start: Optional[str]
    t_end: Optional[str]
    records: List[RetrievedRow]
    total_records: int
    source_files: List[str]
    is_empty: bool
    status_log: str

def parse_iso_or_custom_dt(dt_str: str) -> Optional[datetime]:
    """Parse common timestamp formats like 2026-03-01 10:00, 2026/03/01 10:00, or 2026-03-01T10:00:00."""
    if not dt_str:
        return None
    cleaned = str(dt_str).strip()
    formats = [
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
        "%Y/%m/%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None

class AQIRetriever:
    """In-memory or file-backed retriever for clean AQI observations."""

    def __init__(self, clean_csv_path: Optional[str] = None, records: Optional[List[Dict[str, Any]]] = None):
        self.clean_csv_path = clean_csv_path
        self._records: List[RetrievedRow] = []
        if records:
            self._load_from_dict_list(records)
        elif clean_csv_path and os.path.exists(clean_csv_path):
            self._load_from_csv(clean_csv_path)

    def _row_to_retrieved_row(self, row: Dict[str, Any]) -> RetrievedRow:
        site_id = int(row.get("site_id", 0))
        date_str = str(row.get("data_creation_date", "")).strip()
        dt_val = parse_iso_or_custom_dt(date_str)
        source_file = row.get("source_file", "aqi_2026_clean.csv")
        record_key = f"({site_id}, {date_str})"

        # Retrieve canonical Chinese station metadata
        st_meta = get_station_by_id(site_id)
        canon_name = st_meta.site_name if st_meta else str(row.get("site_name", ""))
        canon_county = st_meta.county if st_meta else str(row.get("county", ""))

        def _get_float(key: str) -> Optional[float]:
            val = row.get(key)
            if val is None or val == "":
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        def _get_int(key: str) -> Optional[int]:
            val = row.get(key)
            if val is None or val == "":
                return None
            try:
                return int(float(val))
            except (ValueError, TypeError):
                return None

        return RetrievedRow(
            site_id=site_id,
            site_name=canon_name,
            county=canon_county,
            timestamp=date_str,
            dt=dt_val,
            aqi=_get_int("aqi"),
            pollutant=row.get("pollutant"),
            status=row.get("status"),
            so2=_get_float("so2"),
            co=_get_float("co"),
            o3=_get_float("o3"),
            o3_8hr=_get_float("o3_8hr"),
            pm10=_get_float("pm10"),
            pm2_5=_get_float("pm2_5"),
            no2=_get_float("no2"),
            nox=_get_float("nox"),
            no=_get_float("no"),
            wind_speed=_get_float("wind_speed"),
            wind_direction=_get_float("wind_direction"),
            source_file=source_file,
            record_key=record_key,
            raw_dict=row
        )

    def _load_from_dict_list(self, dict_rows: List[Dict[str, Any]]) -> None:
        self._records = [self._row_to_retrieved_row(r) for r in dict_rows]

    def _load_from_csv(self, csv_path: str) -> None:
        self._records = []
        with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self._records.append(self._row_to_retrieved_row(row))

    def retrieve(
        self,
        site_ids: List[int],
        t_start: Optional[str] = None,
        t_end: Optional[str] = None
    ) -> RetrievalResult:
        """Retrieve observations filtered by SiteIds and optional time interval [t_start, t_end]."""
        dt_start = parse_iso_or_custom_dt(t_start) if t_start else None
        dt_end = parse_iso_or_custom_dt(t_end) if t_end else None

        target_set: Set[int] = set(site_ids)
        matched: List[RetrievedRow] = []
        used_files: Set[str] = set()

        for rec in self._records:
            if rec.site_id not in target_set:
                continue

            if dt_start and rec.dt and rec.dt < dt_start:
                continue
            if dt_end and rec.dt and rec.dt > dt_end:
                continue

            matched.append(rec)
            if rec.source_file:
                used_files.add(rec.source_file)

        # Sort chronologically by dt (or timestamp string if dt is None)
        matched.sort(key=lambda x: (x.dt or datetime.min, x.site_id))

        is_empty = len(matched) == 0
        if is_empty:
            status = f"查無資料：在時段 [{t_start or '起始'} 至 {t_end or '結束'}] 內，測站 {site_ids} 無任何有效觀測紀錄。"
        else:
            status = f"成功檢索 {len(matched)} 筆觀測紀錄，涵蓋 {len(target_set)} 個測站，來源檔案: {', '.join(sorted(used_files))}。"

        return RetrievalResult(
            query_site_ids=site_ids,
            t_start=t_start,
            t_end=t_end,
            records=matched,
            total_records=len(matched),
            source_files=sorted(list(used_files)),
            is_empty=is_empty,
            status_log=status
        )
