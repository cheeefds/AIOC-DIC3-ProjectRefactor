"""Unit tests for Phase 2: Deterministic Retrieval & Analytics Suite."""
import unittest
from datetime import datetime

from src.retrieval.station_resolver import resolve_station
from src.retrieval.retriever import AQIRetriever
from src.analytics.trend import calculate_trend
from src.analytics.comparison import compare_stations
from src.analytics.baseline import calculate_persistence_baseline

class TestRetrievalAndAnalytics(unittest.TestCase):

    def test_station_resolver(self):
        # Exact Chinese
        res_xitun = resolve_station("西屯")
        self.assertTrue(res_xitun.is_resolved)
        self.assertEqual(res_xitun.station.site_id, 32)

        # Suffix stripping
        res_suffix = resolve_station("西屯測站")
        self.assertTrue(res_suffix.is_resolved)
        self.assertEqual(res_suffix.station.site_id, 32)

        # English
        res_eng = resolve_station("Keelung")
        self.assertTrue(res_eng.is_resolved)
        self.assertEqual(res_eng.station.site_id, 1)

        # Ambiguous county
        res_county = resolve_station("臺中市")
        self.assertFalse(res_county.is_resolved)
        self.assertEqual(res_county.status, "AMBIGUOUS_COUNTY_MATCH")
        self.assertGreater(len(res_county.candidates), 1)

        # Unknown location
        res_unk = resolve_station("火星基地")
        self.assertFalse(res_unk.is_resolved)
        self.assertEqual(res_unk.status, "UNKNOWN_LOCATION")

    def test_retriever_and_trend_analytics(self):
        sample_rows = [
            {"site_id": 33, "site_name": "西屯", "county": "臺中市", "aqi": 40, "pm2_5": 10.0, "data_creation_date": "2026-03-01 08:00"},
            {"site_id": 33, "site_name": "西屯", "county": "臺中市", "aqi": 50, "pm2_5": 15.0, "data_creation_date": "2026-03-01 09:00"},
            {"site_id": 33, "site_name": "西屯", "county": "臺中市", "aqi": 70, "pm2_5": 25.0, "data_creation_date": "2026-03-01 10:00"},
            {"site_id": 33, "site_name": "西屯", "county": "臺中市", "aqi": 80, "pm2_5": 30.0, "data_creation_date": "2026-03-01 11:00"},
        ]
        retriever = AQIRetriever(records=sample_rows)
        ret_res = retriever.retrieve([33], t_start="2026-03-01 08:00", t_end="2026-03-01 11:00")
        self.assertEqual(len(ret_res.records), 4)

        # Test Trend Calculation
        trend = calculate_trend(ret_res.records, pollutant="pm2_5")
        self.assertTrue(trend.is_valid)
        self.assertEqual(trend.direction, "上升")
        self.assertAlmostEqual(trend.net_delta, 20.0) # 30.0 - 10.0
        self.assertAlmostEqual(trend.pct_change, 200.0) # +200%
        self.assertEqual(trend.min_val, 10.0)
        self.assertEqual(trend.max_val, 30.0)

    def test_trend_insufficient_data(self):
        sample_rows = [
            {"site_id": 33, "site_name": "西屯", "county": "臺中市", "aqi": 40, "pm2_5": 10.0, "data_creation_date": "2026-03-01 08:00"},
        ]
        retriever = AQIRetriever(records=sample_rows)
        ret_res = retriever.retrieve([33])
        trend = calculate_trend(ret_res.records, pollutant="pm2_5")
        self.assertFalse(trend.is_valid)
        self.assertEqual(trend.direction, "資料不足")
        self.assertIsNotNone(trend.limitation_warning)

    def test_multi_station_comparison(self):
        sample_rows = [
            # Station 32 (西屯)
            {"site_id": 32, "site_name": "西屯", "county": "臺中市", "aqi": 50, "data_creation_date": "2026-03-01 09:00"},
            {"site_id": 32, "site_name": "西屯", "county": "臺中市", "aqi": 70, "data_creation_date": "2026-03-01 10:00"},
            # Station 31 (忠明)
            {"site_id": 31, "site_name": "忠明", "county": "臺中市", "aqi": 80, "data_creation_date": "2026-03-01 09:00"},
            {"site_id": 31, "site_name": "忠明", "county": "臺中市", "aqi": 90, "data_creation_date": "2026-03-01 10:00"},
        ]
        retriever = AQIRetriever(records=sample_rows)
        ret_res = retriever.retrieve([31, 32])
        comp = compare_stations(ret_res.records, pollutant="aqi", rank_by="mean")
        self.assertEqual(len(comp.stations_ranked), 2)
        # 忠明 (mean 85) should rank ahead of 西屯 (mean 60)
        self.assertEqual(comp.stations_ranked[0].site_name, "忠明")
        self.assertAlmostEqual(comp.stations_ranked[0].mean_val, 85.0)
        self.assertEqual(comp.stations_ranked[1].site_name, "西屯")
        self.assertAlmostEqual(comp.stations_ranked[1].mean_val, 60.0)
        self.assertAlmostEqual(comp.max_diff, 25.0)

    def test_persistence_baseline(self):
        sample_rows = [
            {"site_id": 33, "site_name": "西屯", "pm2_5": 10.0, "data_creation_date": "2026-03-01 08:00"},
            {"site_id": 33, "site_name": "西屯", "pm2_5": 15.0, "data_creation_date": "2026-03-01 09:00"},
            {"site_id": 33, "site_name": "西屯", "pm2_5": 8.0, "data_creation_date": "2026-03-01 10:00"},
        ]
        retriever = AQIRetriever(records=sample_rows)
        ret_res = retriever.retrieve([33])
        baseline_res = calculate_persistence_baseline(ret_res.records, pollutant="pm2_5")
        self.assertIsNotNone(baseline_res)
        self.assertEqual(baseline_res.t0_value, 10.0)
        # Residuals from 10.0: [0, +5.0, -2.0]
        self.assertEqual(baseline_res.points[1].residual, 5.0)
        self.assertEqual(baseline_res.points[2].residual, -2.0)
        # Mean absolute deviation: (|0| + |5| + |-2|) / 3 = 7/3 = 2.3333
        self.assertAlmostEqual(baseline_res.mean_absolute_deviation, 2.3333, places=3)

if __name__ == "__main__":
    unittest.main()
