"""Task Planner and Intent Parser for Taiwan AQI Queries.
Parses natural-language user queries into structured execution plans.
"""
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from src.retrieval.station_resolver import resolve_station, clean_location_query
from src.retrieval.stations import TAIWAN_AQI_STATIONS, StationMetadata
from src.domain.guardrails import check_guardrails

@dataclass
class QueryPlan:
    query: str
    intent: str  # "trend", "comparison", "interpretation", "blocked_medical", "blocked_causal", "unsupported", "clarification_needed"
    pollutant: str  # "pm2_5", "aqi", "o3", "pm10", "so2", "co", "no2"
    location_strings: List[str]
    resolved_stations: List[StationMetadata]
    candidate_stations: List[StationMetadata]
    t_start: Optional[str]
    t_end: Optional[str]
    needs_clarification: bool
    is_blocked: bool
    policy_response: Optional[str]
    baseline_requested: bool
    notes: List[str] = field(default_factory=list)

def extract_pollutant(text: str) -> str:
    """Identify target pollutant from query text, defaulting to aqi or pm2_5."""
    t = text.lower()
    if "pm2.5" in t or "pm25" in t or "細懸浮" in t or "微粒" in t:
        return "pm2_5"
    if "pm10" in t or "懸浮微粒" in t:
        return "pm10"
    if "臭氧" in t or "o3" in t:
        return "o3"
    if "二氧化硫" in t or "so2" in t:
        return "so2"
    if "一氧化碳" in t or "co" in t:
        return "co"
    if "二氧化氮" in t or "no2" in t:
        return "no2"
    if "aqi" in t or "空氣品質指標" in t or "空品" in t:
        return "aqi"
    return "pm2_5"  # default pollutant

def extract_time_window(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract explicit date/time intervals from query text."""
    # Look for dates like 2026-03-01, 2026/03/01, 3月1日, 3/1
    # Example: 2026-03-01 08:00 至 2026-03-01 12:00
    date_matches = re.findall(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:\s+\d{1,2}:\d{2})?)", text)
    if len(date_matches) >= 2:
        return date_matches[0], date_matches[1]
    elif len(date_matches) == 1:
        # Check if single timestamp or full day
        single = date_matches[0]
        if ":" in single:
            return single, single
        else:
            return f"{single} 00:00", f"{single} 23:59"

    # Relative time keywords
    if "今天" in text or "今日" in text:
        today_str = "2026-03-01"  # Default snapshot baseline date
        if "上午" in text or "早上" in text:
            return f"{today_str} 06:00", f"{today_str} 12:00"
        elif "下午" in text:
            return f"{today_str} 12:00", f"{today_str} 18:00"
        elif "晚上" in text or "夜間" in text:
            return f"{today_str} 18:00", f"{today_str} 23:00"
        return f"{today_str} 00:00", f"{today_str} 23:59"

    if "昨天" in text or "昨日" in text:
        yesterday_str = "2026-02-28"
        return f"{yesterday_str} 00:00", f"{yesterday_str} 23:59"

    return None, None

def extract_locations(text: str) -> List[str]:
    """Extract potential station names and place names from text."""
    found: List[str] = []
    # Check known stations
    for st in TAIWAN_AQI_STATIONS.values():
        name_zh = st.site_name
        name_norm = name_zh.replace("台", "臺")
        if name_zh in text or name_norm in text:
            if name_zh not in found:
                found.append(name_zh)

    # Check for comparison markers e.g. "A vs B", "A 和 B", "A 與 B"
    vs_match = re.search(r"([\u4e00-\u9fa5]{2,6})\s*(?:vs|和|與|跟|比較)\s*([\u4e00-\u9fa5]{2,6})", text, re.IGNORECASE)
    if vs_match:
        loc1, loc2 = vs_match.group(1), vs_match.group(2)
        loc1_clean = clean_location_query(loc1)
        loc2_clean = clean_location_query(loc2)
        if loc1_clean and loc1_clean not in found:
            found.append(loc1_clean)
        if loc2_clean and loc2_clean not in found:
            found.append(loc2_clean)

    # If still not found, search for patterns ending with 站 or 測站
    if not found:
        generic_matches = re.findall(r"([\u4e00-\u9fa5]{2,5}(?:測站|站))", text)
        for gm in generic_matches:
            c = clean_location_query(gm)
            if c and c not in found:
                found.append(c)

    return found

def parse_query_plan(query_text: str) -> QueryPlan:
    """Parse query text and build QueryPlan."""
    # 1. Guardrail checks
    gr = check_guardrails(query_text)
    if gr.is_blocked:
        intent = "blocked_medical" if gr.guardrail_type == "MEDICAL_DIAGNOSIS" else "blocked_causal"
        return QueryPlan(
            query=query_text,
            intent=intent,
            pollutant="aqi",
            location_strings=[],
            resolved_stations=[],
            candidate_stations=[],
            t_start=None,
            t_end=None,
            needs_clarification=False,
            is_blocked=True,
            policy_response=gr.policy_response,
            baseline_requested=False,
            notes=[f"Blocked by guardrail: {gr.guardrail_type}"]
        )

    pollutant = extract_pollutant(query_text)
    t_start, t_end = extract_time_window(query_text)
    loc_strings = extract_locations(query_text)

    resolved: List[StationMetadata] = []
    candidates: List[StationMetadata] = []
    needs_clarification = False
    notes: List[str] = []

    for loc in loc_strings:
        res = resolve_station(loc)
        if res.is_resolved and res.station:
            if res.station not in resolved:
                resolved.append(res.station)
        else:
            needs_clarification = True
            candidates.extend(res.candidates)
            notes.append(res.message)

    # If no locations identified from text, check if any generic non-existent station was asked
    if not loc_strings:
        needs_clarification = True
        notes.append("未在問題中識別出任何有效的台灣測站或地點。")

    # Determine intent
    is_comparison = len(resolved) >= 2 or any(k in query_text for k in ["比較", "誰比較", "排序", "排名", "vs", "較差", "較高"])
    is_trend = any(k in query_text for k in ["趨勢", "變化", "上升", "下降", "增加", "減少", "走向", "演變"])
    baseline_req = "基準" in query_text or "持續性" in query_text or "persistence" in query_text.lower()

    if is_comparison:
        intent = "comparison"
    elif is_trend:
        intent = "trend"
    else:
        intent = "interpretation"

    return QueryPlan(
        query=query_text,
        intent=intent,
        pollutant=pollutant,
        location_strings=loc_strings,
        resolved_stations=resolved,
        candidate_stations=candidates,
        t_start=t_start,
        t_end=t_end,
        needs_clarification=needs_clarification and len(resolved) == 0,
        is_blocked=False,
        policy_response=None,
        baseline_requested=baseline_req,
        notes=notes
    )
