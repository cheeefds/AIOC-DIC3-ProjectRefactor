"""Unit tests for Phase 3: Taiwan AQI Domain Rules Engine & Guardrails."""
import unittest

from src.domain.aqi_rules import (
    compute_subindex,
    get_aqi_category,
    verify_aqi_and_dominant_pollutant
)
from src.domain.time_windows import get_pollutant_spec, format_taiwan_time, get_regulatory_caveat
from src.domain.guardrails import check_guardrails

class TestDomainRules(unittest.TestCase):

    def test_subindex_calculation(self):
        # PM2.5 = 15.4 -> Subindex 50
        si_50 = compute_subindex("pm2_5", 15.4)
        self.assertEqual(si_50, 50)

        # PM2.5 = 35.4 -> Subindex 100
        si_100 = compute_subindex("pm2_5", 35.4)
        self.assertEqual(si_100, 100)

        # PM10 = 54 -> Subindex 50
        si_pm10 = compute_subindex("pm10", 54.0)
        self.assertEqual(si_pm10, 50)

    def test_aqi_dominant_pollutant_verification(self):
        # PM2.5 = 35.4 (subindex 100), SO2 = 10 (subindex ~14)
        measurements = {
            "pm2_5": 35.4,
            "pm10": 40.0,
            "so2": 10.0,
            "no2": 20.0
        }
        res = verify_aqi_and_dominant_pollutant(
            reported_aqi=100,
            reported_pollutant="PM2.5",
            measurements=measurements
        )
        self.assertTrue(res.is_aqi_consistent)
        self.assertEqual(res.calculated_aqi, 100)
        self.assertEqual(res.calculated_dominant_pollutant, "pm2_5")
        self.assertEqual(res.category_name, "普通")

    def test_aqi_discrepancy_flagging(self):
        # Reported AQI 150 but all sub-indices are under 50
        measurements = {
            "pm2_5": 10.0,
            "pm10": 20.0,
            "so2": 5.0,
        }
        res = verify_aqi_and_dominant_pollutant(
            reported_aqi=150,
            reported_pollutant="PM2.5",
            measurements=measurements
        )
        self.assertFalse(res.is_aqi_consistent)
        self.assertIsNotNone(res.discrepancy_warning)

    def test_time_windows_and_units(self):
        spec = get_pollutant_spec("pm2_5")
        self.assertIsNotNone(spec)
        self.assertEqual(spec.unit, "μg/m³")
        self.assertIn("加權移動平均", spec.averaging_window)

        taiwan_time = format_taiwan_time("2026-03-01 10:00")
        self.assertIn("UTC+8", taiwan_time)

    def test_guardrails_medical_refusal(self):
        query = "我最近一直咳嗽氣喘，是不是空污害的？我該吃什麼藥？"
        res = check_guardrails(query)
        self.assertTrue(res.is_blocked)
        self.assertEqual(res.guardrail_type, "MEDICAL_DIAGNOSIS")
        self.assertIn("醫療與健康守門聲明", res.policy_response)

    def test_guardrails_causal_refusal(self):
        query = "昨天下午彰化台化廠偷排廢氣，是不是導致西屯站 AQI 破百的元兇？"
        res = check_guardrails(query)
        self.assertTrue(res.is_blocked)
        self.assertEqual(res.guardrail_type, "CAUSAL_ATTRIBUTION")
        self.assertIn("污染源因果推論限制聲明", res.policy_response)

    def test_guardrails_allow_objective_query(self):
        query = "請問西屯站昨天下午三點的 PM2.5 與 AQI 數值是多少？"
        res = check_guardrails(query)
        self.assertFalse(res.is_blocked)
        self.assertIsNone(res.policy_response)

if __name__ == "__main__":
    unittest.main()
