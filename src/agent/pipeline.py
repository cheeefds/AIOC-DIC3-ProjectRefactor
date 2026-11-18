"""Agent Execution Pipeline module.
Orchestrates Planner, Retrieval, Deterministic Analytics, Domain Rules, Response Generator, and Evidence Guard.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from src.retrieval.retriever import AQIRetriever, RetrievalResult
from src.agent.planner import parse_query_plan, QueryPlan
from src.analytics.trend import calculate_trend, TrendResult
from src.analytics.comparison import compare_stations, ComparisonResult
from src.analytics.baseline import calculate_persistence_baseline, PersistenceBaselineResult
from src.domain.aqi_rules import verify_aqi_and_dominant_pollutant, AQIVerificationResult
from src.domain.time_windows import format_taiwan_time
from src.agent.gemini_client import GeminiClient
from src.agent.response_generator import (
    format_trend_response,
    format_comparison_response,
    format_interpretation_response,
    build_provenance_block
)
from src.agent.evidence_guard import verify_response_evidence, EvidenceGuardResult

@dataclass
class AgentResponse:
    query: str
    query_plan: QueryPlan
    retrieval_result: Optional[RetrievalResult]
    final_text: str
    is_abstention: bool
    abstention_reason: Optional[str]
    evidence_guard: Optional[EvidenceGuardResult]
    trace: List[str] = field(default_factory=list)

class TaiwanAQIEvidenceAgent:
    """Tool-augmented Evidence Agent for Taiwan Air Quality Q&A."""

    def __init__(self, retriever: AQIRetriever, gemini_client: Optional[GeminiClient] = None):
        self.retriever = retriever
        self.gemini_client = gemini_client or GeminiClient()

    def answer(self, query: str) -> AgentResponse:
        trace: List[str] = []
        trace.append(f"Received query: '{query}'")

        # Step 1: Planning and Intent Parsing
        plan = parse_query_plan(query)
        trace.append(f"Parsed plan: intent={plan.intent}, pollutant={plan.pollutant}, stations={[s.site_name for s in plan.resolved_stations]}")

        # Step 2: Handle Guardrails Block
        if plan.is_blocked:
            trace.append(f"Query blocked by domain guardrail: {plan.intent}")
            return AgentResponse(
                query=query,
                query_plan=plan,
                retrieval_result=None,
                final_text=plan.policy_response or "此查詢因違反領域守門規則被系統攔截。",
                is_abstention=True,
                abstention_reason=f"GUARDRAIL_{plan.intent.upper()}",
                evidence_guard=None,
                trace=trace
            )

        # Step 3: Check Clarification / Station Ambiguity
        if plan.needs_clarification or not plan.resolved_stations:
            trace.append("Clarification required: unknown location or multiple candidate stations.")
            clarification_msg = "、".join(plan.notes) if plan.notes else "未指定明確測站或地點未識別。"
            response_text = f"【需要澄清】\n{clarification_msg}\n請提供確切的測站名稱（例如：台中西屯、忠明、板橋、前金等）。"
            return AgentResponse(
                query=query,
                query_plan=plan,
                retrieval_result=None,
                final_text=response_text,
                is_abstention=True,
                abstention_reason="NEEDS_CLARIFICATION",
                evidence_guard=None,
                trace=trace
            )

        # Step 4: Deterministic Retrieval
        site_ids = [s.site_id for s in plan.resolved_stations]
        retrieval = self.retriever.retrieve(
            site_ids=site_ids,
            t_start=plan.t_start,
            t_end=plan.t_end
        )
        trace.append(f"Retrieved {len(retrieval.records)} records from {len(site_ids)} stations.")

        # Step 5: Handle Data Absence (Evidence-linked refusal)
        if retrieval.is_empty:
            trace.append("Retrieval returned 0 records -> Triggering evidence-linked abstention.")
            station_names = ", ".join(f"{s.county}{s.site_name}(ID:{s.site_id})" for s in plan.resolved_stations)
            refusal_text = (
                f"## 🚫 資料不足拒答 (Evidence-linked Abstention)\n"
                f"在指定查詢條件下查無任何觀測記錄：\n"
                f"- **查詢測站**：{station_names}\n"
                f"- **查詢時段**：{plan.t_start or '未指定'} 至 {plan.t_end or '未指定'}\n\n"
                f"依據本系統防幻覺原則，嚴格禁止自行插補或猜測數值。請確認所查詢的測站或時間是否在有效資料庫範圍內。"
            )
            prov = build_provenance_block(retrieval, plan.pollutant, ["指定時窗或測站於資料庫中完全缺失。"])
            return AgentResponse(
                query=query,
                query_plan=plan,
                retrieval_result=retrieval,
                final_text=refusal_text + "\n" + prov,
                is_abstention=True,
                abstention_reason="DATA_ABSENCE",
                evidence_guard=None,
                trace=trace
            )

        # Collect verified numbers for Evidence Guard
        verified_numbers: Set[float] = set()
        for r in retrieval.records:
            for field_name in ["aqi", "pm2_5", "pm10", "so2", "co", "o3", "o3_8hr", "no2", "wind_speed", "wind_direction"]:
                val = getattr(r, field_name, None)
                if val is not None:
                    verified_numbers.add(float(val))

        # Step 6: Deterministic Analytics & Formatting based on Intent
        baseline_res = None
        if plan.baseline_requested or plan.intent == "trend":
            baseline_res = calculate_persistence_baseline(retrieval.records, plan.pollutant)
            if baseline_res:
                verified_numbers.add(baseline_res.t0_value)
                verified_numbers.add(baseline_res.mean_absolute_deviation)
                verified_numbers.add(baseline_res.max_positive_deviation)
                verified_numbers.add(baseline_res.max_negative_deviation)
                verified_numbers.add(abs(baseline_res.max_positive_deviation))
                verified_numbers.add(abs(baseline_res.max_negative_deviation))

        if plan.intent == "trend":
            trend_res = calculate_trend(retrieval.records, plan.pollutant)
            if trend_res.is_valid:
                verified_numbers.add(trend_res.start_val or 0.0)
                verified_numbers.add(trend_res.end_val or 0.0)
                if trend_res.net_delta is not None:
                    verified_numbers.add(trend_res.net_delta)
                    verified_numbers.add(abs(trend_res.net_delta))
                verified_numbers.add(trend_res.min_val or 0.0)
                verified_numbers.add(trend_res.max_val or 0.0)
                verified_numbers.add(trend_res.mean_val or 0.0)
                if trend_res.pct_change is not None:
                    verified_numbers.add(trend_res.pct_change)
                    verified_numbers.add(abs(trend_res.pct_change))
            draft_text = format_trend_response(
                trend_res, retrieval, baseline_res,
                gemini_client=self.gemini_client, query=query
            )

        elif plan.intent == "comparison":
            comp_res = compare_stations(retrieval.records, plan.pollutant)
            for s in comp_res.stations_ranked:
                verified_numbers.add(s.mean_val)
                verified_numbers.add(s.max_val)
                verified_numbers.add(s.min_val)
                if s.latest_val is not None:
                    verified_numbers.add(s.latest_val)
            verified_numbers.add(comp_res.max_diff)
            draft_text = format_comparison_response(
                comp_res, retrieval,
                gemini_client=self.gemini_client, query=query
            )

        else: # Interpretation
            latest_rec = retrieval.records[-1]
            measurements = {
                "pm2_5": latest_rec.pm2_5,
                "pm10": latest_rec.pm10,
                "o3_8hr": latest_rec.o3_8hr,
                "so2": latest_rec.so2,
                "no2": latest_rec.no2,
            }
            verif_res = verify_aqi_and_dominant_pollutant(
                latest_rec.aqi,
                latest_rec.pollutant,
                measurements
            )
            for si in verif_res.sub_indices.values():
                verified_numbers.add(float(si))
            draft_text = format_interpretation_response(
                retrieval.records, verif_res, retrieval,
                gemini_client=self.gemini_client, query=query
            )

        # Step 7: Evidence Guard Verification
        guard_res = verify_response_evidence(
            text=draft_text,
            known_numeric_values=verified_numbers,
            known_site_ids=set(site_ids)
        )
        trace.append(f"Evidence Guard checked: fidelity={guard_res.provenance_fidelity}, unsupported_count={guard_res.unsupported_numbers_count}")

        return AgentResponse(
            query=query,
            query_plan=plan,
            retrieval_result=retrieval,
            final_text=guard_res.sanitized_text,
            is_abstention=False,
            abstention_reason=None,
            evidence_guard=guard_res,
            trace=trace
        )
