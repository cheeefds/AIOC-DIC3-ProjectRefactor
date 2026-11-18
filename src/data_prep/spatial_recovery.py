"""Spatial SiteId Recovery module.
Attempts deterministic recovery of missing SiteId values using County and exact (Lon, Lat) coordinates.
"""
from typing import Dict, List, Optional, Tuple
from src.retrieval.stations import TAIWAN_AQI_STATIONS, StationMetadata

# Build spatial lookup table: (County, round(lon, 4), round(lat, 4)) -> List[SiteId]
_SPATIAL_LOOKUP: Dict[Tuple[str, float, float], List[int]] = {}

for st in TAIWAN_AQI_STATIONS.values():
    key = (st.county, round(st.lon, 4), round(st.lat, 4))
    if key not in _SPATIAL_LOOKUP:
        _SPATIAL_LOOKUP[key] = []
    _SPATIAL_LOOKUP[key].append(st.site_id)

def recover_site_id(
    county: Optional[str],
    lon: Optional[Any],
    lat: Optional[Any],
    tolerance: float = 0.005
) -> Tuple[Optional[int], str]:
    """Deterministically recover SiteId from county and coordinates.
    
    Returns:
        (resolved_site_id, status_message)
        If resolved: (site_id, "RECOVERED_EXACT_MATCH")
        If ambiguous or no match: (None, "NO_MATCH" or "AMBIGUOUS_MATCH")
    """
    if county is None or lon is None or lat is None:
        return None, "MISSING_COORDINATES_OR_COUNTY"

    try:
        f_lon = float(lon)
        f_lat = float(lat)
    except (ValueError, TypeError):
        return None, "INVALID_NUMERIC_COORDINATES"

    exact_key = (str(county).strip(), round(f_lon, 4), round(f_lat, 4))
    if exact_key in _SPATIAL_LOOKUP and len(_SPATIAL_LOOKUP[exact_key]) == 1:
        return _SPATIAL_LOOKUP[exact_key][0], "RECOVERED_EXACT_MATCH"

    # Search within strict tolerance
    candidates: List[int] = []
    for st in TAIWAN_AQI_STATIONS.values():
        if st.county == str(county).strip():
            if abs(st.lon - f_lon) <= tolerance and abs(st.lat - f_lat) <= tolerance:
                candidates.append(st.site_id)
                
    if len(candidates) == 1:
        return candidates[0], "RECOVERED_SPATIAL_TOLERANCE"
    elif len(candidates) > 1:
        return None, f"AMBIGUOUS_MATCH_MULTIPLE_CANDIDATES_{candidates}"
    else:
        return None, "NO_MATCH_FOUND"
