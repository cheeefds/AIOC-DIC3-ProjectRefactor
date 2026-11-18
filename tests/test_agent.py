"""Unit tests for Phase 4: Agent Core Workflow & Evidence Guard."""
import unittest

from src.retrieval.retriever import AQIRetriever
from src.agent.planner import parse_query_plan
from src.agent.evidence_guard import verify_response_evidence
from src.agent.pipeline import TaiwanAQIEvidenceAgent

class TestAgentWorkflow(unittest.TestCase):

    def setUp(self):
        self.sample_rows = [
            # Xitun (SiteId 32)
            {"site_id": 32, "site_name": "西屯", "county": "臺中市", "aqi": 45, "pollutant": "PM2.5", "pm2_5": 12.0, "pm10": 30.0, "so2": 1.5, "o3_8hr": 0.03, "no2": 15.0, "data_creation_date": "2026-03-01 08:00"},
            {"site_id": 32, "site_name": "西屯", "county": "臺中市", "aqi": 55, "pollutant": "PM2.5", "pm2_5": 16.0, "pm10": 35.0, "so2": 1.6, "o3_8hr": 0.04, "no2": 18.0, "data_creation_date": "2026-03-01 09:00"},
            {"site_id": 32, "site_name": "西屯", "county": "臺中市", "aqi": 75, "pollutant": "PM2.5", "pm2_5": 25.0, "pm10": 45.0, "so2": 2.0, "o3_8hr": 0.05, "no2": 22.0, "data_creation_date": "2026-03-01 10:00"},
            # Zhongming (SiteId 31)
            {"site_id": 31, "site_name": "忠明", "county": "臺中市", "aqi": 80, "pollutant": "PM2.5", "pm2_5": 28.0, "pm10": 50.0, "so2": 2.5, "o3_8hr": 0.05, "no2": 25.0, "data_creation_date": "2026-03-01 08:00"},
            {"site_id": 31, "site_name": "忠明", "county": "臺中市", "aqi": 85, "pollutant": "PM2.5", "pm2_5": 30.0, "pm10": 55.0, "so2": 2.8, "o3_8hr": 0.06, "no2": 26.0, "data_creation_date": "2026-03-01 09:00"},
            {"site_id": 31, "site_name": "忠明", "county": "臺中市", "aqi": 90, "pollutant": "PM2.5", "pm2_5": 32.0, "pm10": 60.0, "so2": 3.0, "o3_8hr": 0.06, "no2": 28.0, "data_creation_date": "2026-03-01 10:00"},
        ]
        self.retriever = AQIRetriever(records=self.sample_rows)
        self.agent = TaiwanAQIEvidenceAgent(self.retriever)

    def test_planner_parsing(self):
        plan_trend = parse_query_plan("請問台中西屯站 2026-03-01 08:00 至 2026-03-01 10:00 的 PM2.5 趨勢如何？")
        self.assertEqual(plan_trend.intent, "trend")
        self.assertEqual(plan_trend.pollutant, "pm2_5")
        self.assertEqual(len(plan_trend.resolved_stations), 1)
        self.assertEqual(plan_trend.resolved_stations[0].site_id, 32)

        plan_comp = parse_query_plan("比較西屯和忠明測站今天的空氣品質誰比較差？")
        self.assertEqual(plan_comp.intent, "comparison")
        self.assertEqual(len(plan_comp.resolved_stations), 2)

    def test_end_to_end_trend_query(self):
        query = "請問西屯站 2026-03-01 08:00 至 2026-03-01 10:00 的 PM2.5 趨勢？"
        resp = self.agent.answer(query)
        self.assertFalse(resp.is_abstention)
        self.assertIn("西屯站", resp.final_text)
        self.assertIn("趨勢分析結果", resp.final_text)
        self.assertIn("資料來源與出處追溯", resp.final_text)
        # Check that Evidence Guard verified numbers with 100% fidelity
        self.assertIsNotNone(resp.evidence_guard)
        self.assertEqual(resp.evidence_guard.unsupported_numbers_count, 0)
        self.assertEqual(resp.evidence_guard.provenance_fidelity, 1.0)

    def test_end_to_end_comparison_query(self):
        query = "比較西屯與忠明 2026-03-01 08:00 至 2026-03-01 10:00 的 AQI 表現"
        resp = self.agent.answer(query)
        self.assertFalse(resp.is_abstention)
        self.assertIn("多測站", resp.final_text)
        self.assertIn("忠明", resp.final_text)
        self.assertIn("西屯", resp.final_text)
        self.assertIsNotNone(resp.evidence_guard)
        self.assertEqual(resp.evidence_guard.unsupported_numbers_count, 0)

    def test_end_to_end_guardrail_refusal(self):
        query = "西屯站今天 PM2.5 這麼高，是不是隔壁工業區煙囪偷排造成的？"
        resp = self.agent.answer(query)
        self.assertTrue(resp.is_abstention)
        self.assertEqual(resp.abstention_reason, "GUARDRAIL_BLOCKED_CAUSAL")
        self.assertIn("污染源因果推論限制聲明", resp.final_text)

    def test_end_to_end_data_absence_abstention(self):
        query = "請問西屯站 2026-12-31 10:00 的 PM2.5 濃度？"
        resp = self.agent.answer(query)
        self.assertTrue(resp.is_abstention)
        self.assertEqual(resp.abstention_reason, "DATA_ABSENCE")
        self.assertIn("資料不足拒答", resp.final_text)

    def test_evidence_guard_detects_hallucinations(self):
        fake_text = "西屯站 PM2.5 飆升至 999.88，全國第一！"
        guard_res = verify_response_evidence(
            text=fake_text,
            known_numeric_values={12.0, 16.0, 25.0},
            known_site_ids={33}
        )
        self.assertFalse(guard_res.is_fully_supported)
        self.assertIn(999.88, guard_res.unsupported_values)
        self.assertIn("此數值缺乏原始觀測證據支持", guard_res.sanitized_text)

if __name__ == "__main__":
    unittest.main()
