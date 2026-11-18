"""Observation Deduplicator and Conflict Isolator module.
Groups records by primary observation key (SiteId, DataCreationDate).
Merges consistent duplicates (e.g. English/Chinese records or backfill) and isolates conflicting variants.
"""
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

# Columns considered when evaluating numeric agreement
MEASUREMENT_COLUMNS = [
    "aqi", "so2", "co", "o3", "o3_8hr", "pm10", "pm2_5", 
    "no2", "nox", "no", "wind_speed", "wind_direction"
]

@dataclass
class DeduplicationResult:
    clean_records: List[Dict[str, Any]]
    conflict_records: List[Dict[str, Any]]
    conflict_count_groups: int
    conflict_count_rows: int
    merged_rows_count: int
    recovered_site_id_count: int

def compare_and_merge_group(
    records: List[Dict[str, Any]], 
    tolerance: float = 1e-3
) -> Tuple[Optional[Dict[str, Any]], Optional[List[Dict[str, Any]]], List[str]]:
    """Compare rows sharing the same key.
    
    Returns:
        (merged_record, None, []) if consistent
        (None, conflicting_records_with_metadata, conflicting_fields) if conflicting
    """
    if len(records) == 1:
        return records[0], None, []

    conflicting_fields: Set[str] = set()

    for col in MEASUREMENT_COLUMNS:
        values = [r[col] for r in records if r.get(col) is not None]
        if len(values) > 1:
            # Check if all values in this column are within tolerance
            first = values[0]
            for val in values[1:]:
                if abs(val - first) > tolerance:
                    conflicting_fields.add(col)
                    break

    if conflicting_fields:
        # Tag each row with the detected conflicting fields
        flagged_conflicts: List[Dict[str, Any]] = []
        field_str = ";".join(sorted(conflicting_fields))
        for r in records:
            c = dict(r)
            c["conflict_reason"] = f"DISAGREEMENT_IN_FIELDS:{field_str}"
            flagged_conflicts.append(c)
        return None, flagged_conflicts, sorted(list(conflicting_fields))

    # All numeric columns agree: safely merge, preferring Chinese metadata if available
    merged: Dict[str, Any] = {}
    for r in records:
        for k, v in r.items():
            if v is not None:
                if k not in merged or merged[k] is None:
                    merged[k] = v
                elif isinstance(v, str) and re.search(r"[\u4e00-\u9fa5]", v) and isinstance(merged[k], str) and not re.search(r"[\u4e00-\u9fa5]", merged[k]):
                    # Prefer Chinese name/county/status
                    merged[k] = v
                
    return merged, None, []

def process_observations(records: List[Dict[str, Any]]) -> DeduplicationResult:
    """Group, deduplicate, and isolate conflicts for a collection of normalized records."""
    groups: Dict[Tuple[Any, Any], List[Dict[str, Any]]] = {}
    
    # Also collect rows that lack SiteId or DataCreationDate
    invalid_key_records: List[Dict[str, Any]] = []

    for r in records:
        site_id = r.get("site_id")
        date_key = r.get("data_creation_date")
        if site_id is None or date_key is None:
            r_copy = dict(r)
            r_copy["conflict_reason"] = "MISSING_PRIMARY_KEY"
            invalid_key_records.append(r_copy)
            continue
        key = (site_id, str(date_key).strip())
        if key not in groups:
            groups[key] = []
        groups[key].append(r)

    clean_records: List[Dict[str, Any]] = []
    conflict_records: List[Dict[str, Any]] = list(invalid_key_records)
    conflict_groups = 0
    conflict_rows = len(invalid_key_records)
    merged_count = 0

    for key, group in groups.items():
        if len(group) == 1:
            clean_records.append(group[0])
        else:
            merged, conflicts, diff_fields = compare_and_merge_group(group)
            if merged is not None:
                clean_records.append(merged)
                merged_count += (len(group) - 1)
            else:
                conflict_groups += 1
                conflict_rows += len(conflicts)
                conflict_records.extend(conflicts)

    # Sort clean records chronologically by date and site_id
    clean_records.sort(key=lambda x: (str(x.get("data_creation_date")), x.get("site_id", 0)))

    return DeduplicationResult(
        clean_records=clean_records,
        conflict_records=conflict_records,
        conflict_count_groups=conflict_groups,
        conflict_count_rows=conflict_rows,
        merged_rows_count=merged_count,
        recovered_site_id_count=0
    )
