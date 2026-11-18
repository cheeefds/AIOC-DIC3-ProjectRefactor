"""Station Resolver module.
Resolves natural-language place names, county names, and station abbreviations into canonical SiteIds.
"""
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from src.retrieval.stations import TAIWAN_AQI_STATIONS, StationMetadata, get_station_by_id

@dataclass
class ResolutionResult:
    query: str
    is_resolved: bool
    station: Optional[StationMetadata]
    candidates: List[StationMetadata]
    status: str
    message: str

def clean_location_query(text: str) -> str:
    """Strip common suffixes like 測站, 站, 空氣品質測站, 監測站."""
    cleaned = text.strip()
    # Normalize traditional/simplified variants
    cleaned = cleaned.replace("台", "臺")
    # Remove station suffixes
    cleaned = re.sub(r"(空氣品質測站|監測站|測站|測點|站)$", "", cleaned).strip()
    return cleaned

def resolve_station(location_query: str) -> ResolutionResult:
    """Deterministically resolve a location query to a canonical StationMetadata.
    
    Rules:
    1. If integer string: direct lookup by SiteId.
    2. Exact match against SiteName or SiteEngName.
    3. Prefix/substring match on SiteName.
    4. If matches a County, return all stations in that County as candidates.
    5. If 1 candidate -> resolved.
    6. If > 1 candidates -> ambiguous, requires user clarification.
    7. If 0 candidates -> unknown.
    """
    raw_query = location_query.strip()
    if not raw_query:
        return ResolutionResult(
            query=location_query,
            is_resolved=False,
            station=None,
            candidates=[],
            status="EMPTY_QUERY",
            message="查詢地點為空。"
        )

    # 1. Direct SiteId lookup
    if raw_query.isdigit():
        site_id = int(raw_query)
        st = get_station_by_id(site_id)
        if st:
            return ResolutionResult(
                query=location_query,
                is_resolved=True,
                station=st,
                candidates=[st],
                status="EXACT_ID_MATCH",
                message=f"成功依測站代碼 {site_id} 解析為 {st.county}{st.site_name}站。"
            )

    cleaned = clean_location_query(raw_query)

    # 2. Exact match on Chinese name
    for st in TAIWAN_AQI_STATIONS.values():
        if st.site_name.replace("台", "臺") == cleaned:
            return ResolutionResult(
                query=location_query,
                is_resolved=True,
                station=st,
                candidates=[st],
                status="EXACT_NAME_MATCH",
                message=f"精確匹配測站：{st.county}{st.site_name}（SiteId: {st.site_id}）。"
            )

    # 3. Exact match on English name (case-insensitive)
    for st in TAIWAN_AQI_STATIONS.values():
        if st.site_eng_name.lower() == raw_query.lower():
            return ResolutionResult(
                query=location_query,
                is_resolved=True,
                station=st,
                candidates=[st],
                status="EXACT_ENG_NAME_MATCH",
                message=f"精確匹配英文測站：{st.county}{st.site_name} ({st.site_eng_name}, SiteId: {st.site_id})。"
            )

    # 4. Composite matches, e.g. "臺中西屯", "台中市西屯"
    for st in TAIWAN_AQI_STATIONS.values():
        county_norm = st.county.replace("台", "臺").replace("市", "").replace("縣", "")
        site_norm = st.site_name.replace("台", "臺")
        combined = f"{county_norm}{site_norm}"
        if combined in cleaned or cleaned in combined:
            return ResolutionResult(
                query=location_query,
                is_resolved=True,
                station=st,
                candidates=[st],
                status="COMPOSITE_MATCH",
                message=f"複合比對成功：{st.county}{st.site_name}（SiteId: {st.site_id}）。"
            )

    # 5. County-level query (e.g. "臺北市", "台中", "高雄市")
    county_matches: List[StationMetadata] = []
    cleaned_county = cleaned.replace("市", "").replace("縣", "")
    for st in TAIWAN_AQI_STATIONS.values():
        if cleaned_county in st.county.replace("台", "臺"):
            county_matches.append(st)

    if county_matches:
        if len(county_matches) == 1:
            return ResolutionResult(
                query=location_query,
                is_resolved=True,
                station=county_matches[0],
                candidates=county_matches,
                status="COUNTY_SINGLE_MATCH",
                message=f"縣市對應唯一測站：{county_matches[0].county}{county_matches[0].site_name}（SiteId: {county_matches[0].site_id}）。"
            )
        candidate_names = [f"{s.site_name}(ID:{s.site_id})" for s in county_matches[:6]]
        return ResolutionResult(
            query=location_query,
            is_resolved=False,
            station=None,
            candidates=county_matches,
            status="AMBIGUOUS_COUNTY_MATCH",
            message=f"地點「{location_query}」包含多個測站，請指定具體測站名稱，候選測站：{', '.join(candidate_names)} 等共 {len(county_matches)} 站。"
        )

    # 6. Substring match
    sub_matches: List[StationMetadata] = []
    for st in TAIWAN_AQI_STATIONS.values():
        if cleaned in st.site_name.replace("台", "臺") or st.site_name.replace("台", "臺") in cleaned:
            sub_matches.append(st)

    if len(sub_matches) == 1:
        st = sub_matches[0]
        return ResolutionResult(
            query=location_query,
            is_resolved=True,
            station=st,
            candidates=sub_matches,
            status="SUBSTRING_MATCH",
            message=f"部分匹配成功：{st.county}{st.site_name}（SiteId: {st.site_id}）。"
        )
    elif len(sub_matches) > 1:
        candidate_names = [f"{s.site_name}(ID:{s.site_id})" for s in sub_matches]
        return ResolutionResult(
            query=location_query,
            is_resolved=False,
            station=None,
            candidates=sub_matches,
            status="AMBIGUOUS_SUBSTRING_MATCH",
            message=f"「{location_query}」匹配到多個測站：{', '.join(candidate_names)}，請明確指定測站。"
        )

    return ResolutionResult(
        query=location_query,
        is_resolved=False,
        station=None,
        candidates=[],
        status="UNKNOWN_LOCATION",
        message=f"無法識別地點「{location_query}」，未找到對應之台灣空氣品質測站。"
    )
