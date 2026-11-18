"""Unit tests for Phase 1: Data Preparation & Quality Verification Pipeline."""
import os
import tempfile
import unittest
import csv

from src.data_prep.normalizer import normalize_row, normalize_value
from src.data_prep.spatial_recovery import recover_site_id
from src.data_prep.deduplicator import process_observations, compare_and_merge_group
from src.data_prep.auditor import audit_raw_directory, compute_md5
from scripts.clean_aqi_data import run_cleaning_pipeline

class TestDataPrep(unittest.TestCase):

    def test_sentinel_normalization(self):
        # Sentinels should be normalized to None
        self.assertIsNone(normalize_value("pm2_5", "-"))
        self.assertIsNone(normalize_value("aqi", "--"))
        self.assertIsNone(normalize_value("so2", "NA"))
        self.assertIsNone(normalize_value("status", ""))
        self.assertIsNone(normalize_value("status", "null"))
        # Valid numeric strings should be converted to float/int
        self.assertEqual(normalize_value("aqi", "45"), 45)
        self.assertAlmostEqual(normalize_value("pm2_5", "12.3"), 12.3)
        self.assertEqual(normalize_value("site_name", "西屯"), "西屯")

    def test_spatial_site_id_recovery(self):
        # Known coordinates for 西屯 (SiteId 32, 臺中市, 120.616917, 24.162197)
        site_id, status = recover_site_id("臺中市", 120.6169, 24.1622)
        self.assertEqual(site_id, 32)
        self.assertIn("RECOVERED", status)

        # Unknown location or coordinate should fail gracefully
        site_id_none, status_none = recover_site_id("未知縣市", 99.0, 99.0)
        self.assertIsNone(site_id_none)
        self.assertEqual(status_none, "NO_MATCH_FOUND")

    def test_deduplication_consistent_merge(self):
        row1 = {
            "site_id": 32,
            "data_creation_date": "2026-03-01 10:00",
            "aqi": 55,
            "pm2_5": 16.0,
            "so2": None,
            "site_name": "西屯"
        }
        row2 = {
            "site_id": 32,
            "data_creation_date": "2026-03-01 10:00",
            "aqi": 55,
            "pm2_5": 16.0,
            "so2": 2.1,
            "site_name": "Xitun"
        }
        merged, conflicts, diff = compare_and_merge_group([row1, row2])
        self.assertIsNotNone(merged)
        self.assertIsNone(conflicts)
        self.assertEqual(merged["so2"], 2.1)
        self.assertEqual(merged["pm2_5"], 16.0)

    def test_deduplication_conflict_isolation(self):
        row1 = {
            "site_id": 32,
            "data_creation_date": "2026-03-01 10:00",
            "aqi": 55,
            "pm2_5": 16.0,
        }
        row2 = {
            "site_id": 32,
            "data_creation_date": "2026-03-01 10:00",
            "aqi": 75, # Conflicting AQI
            "pm2_5": 25.0, # Conflicting PM2.5
        }
        merged, conflicts, diff = compare_and_merge_group([row1, row2])
        self.assertIsNone(merged)
        self.assertIsNotNone(conflicts)
        self.assertEqual(len(conflicts), 2)
        self.assertIn("aqi", diff)
        self.assertIn("pm2_5", diff)

    def test_end_to_end_pipeline_with_temp_files(self):
        with tempfile.TemporaryDirectory() as tmp_raw, tempfile.TemporaryDirectory() as tmp_proc:
            # Create a sample raw CSV file
            csv_path = os.path.join(tmp_raw, "aqi_sample_202603.csv")
            fieldnames = ["SiteId", "SiteName", "County", "AQI", "Pollutant", "PM2.5", "SO2", "DataCreationDate", "TWD97Lon", "TWD97Lat"]
            rows = [
                # Valid observation 1 (西屯, site 32)
                {"SiteId": "32", "SiteName": "西屯", "County": "臺中市", "AQI": "45", "Pollutant": "PM2.5", "PM2.5": "12.0", "SO2": "1.5", "DataCreationDate": "2026-03-01 09:00", "TWD97Lon": "120.6169", "TWD97Lat": "24.1622"},
                # Consistent duplicate of observation 1 (e.g. English version or backfill)
                {"SiteId": "32", "SiteName": "Xitun", "County": "Taichung", "AQI": "45", "Pollutant": "PM2.5", "PM2.5": "12.0", "SO2": "-", "DataCreationDate": "2026-03-01 09:00", "TWD97Lon": "120.6169", "TWD97Lat": "24.1622"},
                # Observation 2 with sentinel values (忠明, site 31)
                {"SiteId": "31", "SiteName": "忠明", "County": "臺中市", "AQI": "60", "Pollutant": "-", "PM2.5": "18.5", "SO2": "--", "DataCreationDate": "2026-03-01 09:00", "TWD97Lon": "120.6411", "TWD97Lat": "24.1520"},
                # Observation 3 with missing SiteId, to be spatially recovered (西屯 coords -> site 32)
                {"SiteId": "", "SiteName": "", "County": "臺中市", "AQI": "50", "Pollutant": "PM2.5", "PM2.5": "14.0", "SO2": "1.0", "DataCreationDate": "2026-03-01 11:00", "TWD97Lon": "120.6169", "TWD97Lat": "24.1622"},
                # Conflict pair (SiteId 32, 2026-03-01 12:00) with contradictory AQI
                {"SiteId": "32", "SiteName": "西屯", "County": "臺中市", "AQI": "50", "Pollutant": "PM2.5", "PM2.5": "15.0", "SO2": "1.0", "DataCreationDate": "2026-03-01 12:00", "TWD97Lon": "120.6169", "TWD97Lat": "24.1622"},
                {"SiteId": "32", "SiteName": "西屯", "County": "臺中市", "AQI": "80", "Pollutant": "PM2.5", "PM2.5": "28.0", "SO2": "1.0", "DataCreationDate": "2026-03-01 12:00", "TWD97Lon": "120.6169", "TWD97Lat": "24.1622"},
            ]
            with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            run_cleaning_pipeline(tmp_raw, tmp_proc)

            clean_file = os.path.join(tmp_proc, "aqi_2026_clean.csv")
            conflict_file = os.path.join(tmp_proc, "aqi_2026_conflicts.csv")
            report_file = os.path.join(tmp_proc, "cleaning_report.md")

            self.assertTrue(os.path.exists(clean_file))
            self.assertTrue(os.path.exists(conflict_file))
            self.assertTrue(os.path.exists(report_file))

            with open(clean_file, "r", encoding="utf-8") as f:
                clean_rows = list(csv.DictReader(f))
            with open(conflict_file, "r", encoding="utf-8") as f:
                conflict_rows = list(csv.DictReader(f))

            # Expected clean: observation 1 (merged from 2 duplicates, site 32), observation 2 (忠明, site 31), observation 3 (recovered SiteId 32)
            # Total clean rows = 3
            self.assertEqual(len(clean_rows), 3)
            # Find the merged row for site 32 at 09:00
            merged_row = next(r for r in clean_rows if r["site_id"] == "32" and r["data_creation_date"] == "2026-03-01 09:00")
            self.assertEqual(merged_row["so2"], "1.5")
            # Recovered row has site_id 32 at 11:00
            recovered_row = next(r for r in clean_rows if r["site_id"] == "32" and r["data_creation_date"] == "2026-03-01 11:00")
            self.assertEqual(recovered_row["pm2_5"], "14.0")

            # Conflicting rows isolated
            self.assertEqual(len(conflict_rows), 2)
            for cr in conflict_rows:
                self.assertIn("DISAGREEMENT_IN_FIELDS", cr["conflict_reason"])

if __name__ == "__main__":
    unittest.main()
